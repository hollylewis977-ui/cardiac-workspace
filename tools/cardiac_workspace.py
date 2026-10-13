#!/usr/bin/env python3
"""Inspect the linked cardiac project and run one bounded experiment."""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def child_path(root, name):
    value = (root / name).resolve()
    if Path(name).is_absolute() or not value.is_relative_to(root.resolve()):
        raise ValueError(f"Path must stay inside {root}: {name}")
    return value


def load_config(path):
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    if config.get("schema_version") != 1:
        raise ValueError("Expected config schema_version=1")
    project = (path.parent / config["project_root"]).resolve()
    runs = child_path(path.parent, config.get("runs_dir", "runs"))
    if runs == path.parent:
        raise ValueError("runs_dir must be a dedicated subdirectory")
    threads = config.get("threads", 2)
    if type(threads) is not int or threads < 1:
        raise ValueError("threads must be a positive integer")
    for name, task in config["tasks"].items():
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
            raise ValueError(f"Invalid task ID: {name}")
        if not isinstance(task.get("argv"), list) or not task["argv"]:
            raise ValueError(f"Task {name} needs an argv list")
        if not all(isinstance(arg, str) and arg for arg in task["argv"]):
            raise ValueError(f"Task {name} argv must contain nonempty strings")
        timeout = task.get("timeout_seconds")
        if type(timeout) not in (int, float) or not 0 < timeout < float("inf"):
            raise ValueError(f"Task {name} needs a finite positive timeout")
        child_path(project, task["cwd"])
    return config, path, project, runs


def npy_header(stream):
    if stream.read(6) != b"\x93NUMPY":
        raise ValueError("Invalid NPY magic")
    version = tuple(stream.read(2))
    formats = {(1, 0): (2, "<H"), (2, 0): (4, "<I"), (3, 0): (4, "<I")}
    if version not in formats:
        raise ValueError(f"Unsupported NPY version: {version}")
    size, fmt = formats[version]
    raw_size = stream.read(size)
    if len(raw_size) != size:
        raise ValueError("Truncated NPY header length")
    length = struct.unpack(fmt, raw_size)[0]
    if length > 65536:
        raise ValueError("NPY header exceeds 64 KiB")
    raw = stream.read(length)
    if len(raw) != length:
        raise ValueError("Truncated NPY header")
    header = ast.literal_eval(raw.decode("utf-8" if version == (3, 0) else "latin1"))
    if not isinstance(header, dict) or not isinstance(header.get("descr"), str):
        raise ValueError("Expected a numeric NPY dtype")
    if "O" in header["descr"]:
        raise ValueError("Object arrays are not supported")
    shape = header.get("shape")
    if not isinstance(shape, tuple) or not all(type(n) is int and n >= 0 for n in shape):
        raise ValueError("Invalid NPY shape")
    return {"shape": list(shape), "dtype": header["descr"], "fortran_order": header["fortran_order"]}


def data_summary(data_dir, expected):
    files = sorted(data_dir.glob("batch_[0-9][0-9][0-9].npz"))
    errors, entries = [], []
    expected_names = [f"batch_{i:03d}.npz" for i in range(expected["batches"])]
    if [p.name for p in files] != expected_names:
        errors.append(f"Expected batch_000 through batch_{expected['batches'] - 1:03d}; found {len(files)} files")
    b, t, n = (expected[k] for k in ("samples_per_batch", "frames", "nodes"))
    shapes = {"u": [b, t, n], "ca": [b, t, n], "x_uni": [b, n, 2], "x_mesh": [b, n, 2], "full_init": [b, n * 21]}
    for path in files:
        item = {"name": path.name, "bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns, "arrays": {}}
        try:
            with zipfile.ZipFile(path) as archive:
                for name, shape in shapes.items():
                    member = archive.getinfo(name + ".npy")
                    if member.compress_type != zipfile.ZIP_STORED:
                        errors.append(f"{path.name}:{name} is compressed; NpzBatch requires ZIP_STORED")
                    with archive.open(member) as stream:
                        header = npy_header(stream)
                        offset = stream.tell()
                    item["arrays"][name] = header
                    if header["shape"] != shape:
                        errors.append(f"{path.name}:{name} shape {header['shape']} != {shape}")
                    itemsize = 2 if name in ("u", "ca") else 4
                    if header["dtype"] not in (f"<f{itemsize}", f">f{itemsize}", f"=f{itemsize}"):
                        errors.append(f"{path.name}:{name} expected float{itemsize * 8}, got {header['dtype']}")
                    elif member.file_size != offset + math.prod(header["shape"]) * itemsize:
                        errors.append(f"{path.name}:{name} payload size does not match NPY header")
        except (OSError, KeyError, ValueError, SyntaxError, zipfile.BadZipFile) as exc:
            errors.append(f"{path.name}: {exc}")
        entries.append(item)
    return {"directory": str(data_dir), "files": entries, "errors": errors,
            "scope": "NPZ headers only; no full-array, duplicate, numerical or clinical validation"}


def packages(names):
    result = {}
    for name in names:
        if importlib.util.find_spec(name) is None:
            result[name] = None
            continue
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "importable; distribution version unknown"
    return result


def doctor(config, project):
    errors = []
    for name in config["entrypoints"]:
        if not child_path(project, name).is_file():
            errors.append(f"Missing entrypoint: {name}")
    deps = packages(sorted({dep for task in config["tasks"].values() for dep in task.get("dependencies", [])}))
    errors.extend(f"Missing Python dependency: {name}" for name, value in deps.items() if value is None)
    data = data_summary((project / config["data_dir"]).resolve(), config["expected_data"])
    errors.extend(data["errors"])
    return {"project": str(project), "python": sys.executable, "python_version": platform.python_version(),
            "packages": deps, "data": data, "errors": errors, "ready": not errors}


def source_hashes(config, project):
    files = set()
    for name in config["source_roots"]:
        directory = child_path(project, name)
        files.update(p for p in directory.rglob("*.py") if p.is_file() and p.resolve().is_relative_to(project))
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def make_plan(config, project, runs, task_id, run_dir=None):
    if task_id not in config["tasks"]:
        raise ValueError(f"Unknown task {task_id}; use list")
    task = config["tasks"][task_id]
    cwd = child_path(project, task["cwd"])
    if not cwd.is_dir():
        raise ValueError(f"Missing task working directory: {cwd}")
    mapping = {"{python}": sys.executable, "{project_root}": str(project),
               "{data_dir}": str((project / config["data_dir"]).resolve()),
               "{run_dir}": str(run_dir or runs / "NEW-RUN")}
    argv = []
    for argument in task["argv"]:
        for key, value in mapping.items():
            argument = argument.replace(key, value)
        argv.append(argument)
    return {"task": task_id, "description": task.get("description", task_id), "argv": argv,
            "cwd": str(cwd), "timeout_seconds": task["timeout_seconds"],
            "threads": config.get("threads", 2), "requires_data": task.get("requires_data", False)}


def save_json(path, value):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_task(config, config_path, project, runs, task_id):
    make_plan(config, project, runs, task_id)
    task = config["tasks"][task_id]
    deps = packages(task.get("dependencies", []))
    missing = [name for name, value in deps.items() if value is None]
    if missing:
        raise ValueError(f"Missing dependencies in {sys.executable}: {', '.join(missing)}")
    inputs = None
    if task.get("requires_data"):
        inputs = data_summary((project / config["data_dir"]).resolve(), config["expected_data"])
        if inputs["errors"]:
            raise ValueError("Data preflight failed: " + "; ".join(inputs["errors"][:8]))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + task_id + "-" + uuid.uuid4().hex[:8]
    run_dir = runs / run_id
    plan = make_plan(config, project, runs, task_id, run_dir)
    hashes = source_hashes(config, project)
    run_dir.mkdir(parents=True, exist_ok=False)
    evidence = {key: "not-assessed" for key in ("code", "numerics", "data", "prediction", "personalization", "uncertainty")}
    record = {"schema_version": 1, "run_id": run_id, **plan, "status": "running",
              "started_at": stamp(), "finished_at": None, "exit_code": None,
              "python": sys.executable, "python_version": platform.python_version(),
              "platform": platform.platform(), "packages": deps,
              "config_file": str(config_path), "config": config,
              "source_sha256": hashes, "input_files": inputs,
              "stdout": str(run_dir / "stdout.log"), "stderr": str(run_dir / "stderr.log"),
              "evidence": evidence, "limitation": "Process success is not predictive or personalization validation"}
    result_path = run_dir / "run.json"
    save_json(result_path, record)
    env = os.environ.copy()
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
    env.update({key: str(plan["threads"]) for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")})
    print(f"Running {task_id}; logs: {run_dir}", flush=True)
    try:
        with open(record["stdout"], "w", encoding="utf-8") as stdout, open(record["stderr"], "w", encoding="utf-8") as stderr:
            result = subprocess.run(plan["argv"], cwd=plan["cwd"], env=env, shell=False,
                                    stdout=stdout, stderr=stderr, timeout=plan["timeout_seconds"])
        record["exit_code"] = result.returncode
        record["status"] = "completed" if result.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        record.update(status="timed-out", exit_code=124)
    except KeyboardInterrupt:
        record.update(status="interrupted", exit_code=130)
    except OSError as exc:
        record.update(status="failed", exit_code=1, error=str(exc))
    finally:
        record["finished_at"] = stamp()
        record["evidence"]["code"] = "execution-passed" if record["status"] == "completed" else "unverified"
        record["source_changed_during_run"] = source_hashes(config, project) != hashes
        save_json(result_path, record)
    print(f"{record['status']}; exit={record['exit_code']}; result={result_path}")
    return record


def packet(task, config_path=None, project=None):
    parts = ["# Cardiac research packet", "Task: " + task,
             "Active configuration: " + str(config_path or ROOT / "cardiac-workspace.json"),
             "Inspect current project diffs before editing."]
    if project is not None:
        parts.append("Resolved project root: " + str(project))
    for name in ("AGENTS.md", "agents/core/research-core.md", "projects/cardiac-ep/CURRENT_STATE.md", "projects/cardiac-ep/SOURCE_MAP.md"):
        value = (ROOT / name).read_text(encoding="utf-8")
        if name.endswith("CURRENT_STATE.md") and (len(value.encode("utf-8")) > 12288 or len(value.splitlines()) > 300):
            raise ValueError("CURRENT_STATE exceeds 12 KiB/300 lines; compact without losing evidence")
        parts.extend(["\nSource: " + name, value])
    result = "\n\n".join(parts)
    if len(result.encode("utf-8")) > 32768:
        raise ValueError("Packet exceeds 32 KiB; shorten indexes instead of truncating evidence")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "cardiac-workspace.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Read-only source, environment and NPZ-header check")
    commands.add_parser("list", help="List defined tasks; no execution")
    commands.add_parser("status", help="Read existing run records")
    commands.add_parser("packet", help="Print bounded context for the interactive agent").add_argument("--task", default="Continue the user's cardiac coding/experiment task")
    for command in ("plan", "run"):
        commands.add_parser(command).add_argument("task")
    args = parser.parse_args(argv)
    try:
        config, config_path, project, runs = load_config(args.config)
        if args.command == "doctor":
            report = doctor(config, project)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ready"] else 1
        if args.command == "list":
            for name, task in config["tasks"].items():
                print(f"{name}: {task.get('description', name)} (timeout={task['timeout_seconds']}s)")
        elif args.command == "plan":
            print(json.dumps(make_plan(config, project, runs, args.task), ensure_ascii=False, indent=2))
        elif args.command == "run":
            record = run_task(config, config_path, project, runs, args.task)
            return 0 if record["exit_code"] == 0 else 1
        elif args.command == "status":
            for path in sorted(runs.glob("*/run.json")):
                record = json.loads(path.read_text(encoding="utf-8"))
                print(f"{record['run_id']}: {record['status']} exit={record['exit_code']}")
        elif args.command == "packet":
            print(packet(args.task, config_path, project))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
