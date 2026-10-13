#!/usr/bin/env python3
"""Autonomous cardiac research queue, adapted from the original conjecture runner."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

import cardiac_workspace as experiments
import research_runtime as runtime


ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
DEFAULTS = {"max_rounds": 0, "max_wall_hours": 24, "round_timeout_minutes": 90,
            "max_tokens": 0, "idle_seconds": 60, "poll_seconds": 60,
            "max_consecutive_runtime_failures": 3, "max_no_progress_rounds": 3,
            "packet_max_bytes": 49152, "model": "", "reasoning_effort": "", "web_search": False}


def slug_check(slug):
    if not SLUG.fullmatch(slug):
        raise ValueError("Task ID must use lowercase letters, numbers, underscore or hyphen")


def load_config(path):
    path = path.resolve()
    config = {**DEFAULTS, **runtime.read_json(path)}
    if config.get("schema_version") != 1:
        raise ValueError("Expected queue schema_version=1")
    for key in ("max_rounds", "max_tokens", "max_consecutive_runtime_failures", "max_no_progress_rounds", "packet_max_bytes"):
        if type(config[key]) is not int or config[key] < (0 if key in {"max_rounds", "max_tokens"} else 1):
            raise ValueError(f"Invalid {key}")
    for key in ("max_wall_hours", "round_timeout_minutes", "idle_seconds", "poll_seconds"):
        if type(config[key]) not in (int, float) or not math.isfinite(config[key]) or config[key] < (0 if key == "max_wall_hours" else 0.01):
            raise ValueError(f"Invalid {key}")
    workspace_config = runtime.local(path.parent, config["workspace_config"])
    workspace_data, _, project, _ = experiments.load_config(workspace_config)
    config.update(config_path=path, workspace_config_path=workspace_config,
                  workspace=workspace_config.parent, project=project, workspace_data=workspace_data)
    for key in ("items_dir", "state_dir", "runtime_dir"):
        config[key] = runtime.local(path.parent, config[key])
        if config[key] == path.parent:
            raise ValueError(f"{key} must be a dedicated directory")
    prefix = config.get("codex_command", [])
    if not isinstance(prefix, list) or not all(isinstance(part, str) and part for part in prefix):
        raise ValueError("codex_command must be an argv prefix list, or [] for automatic discovery")
    return config


def codex_prefix(config):
    if config.get("codex_command"):
        return config["codex_command"]
    found = shutil.which("codex") or shutil.which("codex.cmd")
    if not found:
        raise ValueError("Codex CLI not found; configure codex_command or install it")
    path = Path(found)
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".ps1", ".bat"}:
        package = path.parent / "node_modules/@openai/codex"
        matches = sorted((package / "node_modules/@openai").glob("codex-win32-*/vendor/*/codex/codex.exe"))
        if len(matches) == 1:
            return [str(matches[0])]
        node = shutil.which("node")
        wrapper = package / "bin/codex.js"
        if node and wrapper.is_file():
            return [node, str(wrapper)]
        raise ValueError("Set codex_command to the native codex.exe or node + codex.js; no shell wrapper is executed")
    return [found]


def task_file(config, slug):
    slug_check(slug)
    return runtime.local(config["items_dir"], slug) / "task.json"


def task_directory(config, slug):
    slug_check(slug)
    return runtime.local(config["state_dir"], slug)


def read_task(path):
    task = runtime.read_json(path)
    slug_check(task["slug"])
    if task["slug"] != path.parent.name:
        raise ValueError("Task ID does not match its directory")
    for key in ("title", "objective", "scope"):
        if not isinstance(task.get(key), str) or not task[key].strip():
            raise ValueError(f"Task needs {key}")
    criteria = task.get("acceptance")
    if not isinstance(criteria, list) or not criteria or not all(isinstance(c, dict) and c.get("id") and c.get("description") for c in criteria):
        raise ValueError("Task needs explicit acceptance criteria")
    if len({c['id'] for c in criteria}) != len(criteria):
        raise ValueError("Duplicate criterion ID")
    if type(task.get("ready")) is not bool or type(task.get("enabled", True)) is not bool:
        raise ValueError("ready/enabled must be booleans")
    if type(task.get("max_rounds", 0)) is not int or task.get("max_rounds", 0) < 0:
        raise ValueError("Invalid task max_rounds")
    return task


def read_state(config, task):
    path = task_directory(config, task["slug"]) / "state.json"
    state = runtime.read_json(path) if path.exists() else runtime.initial_state(task)
    if state.get("status") not in runtime.STATES or state.get("phase") not in runtime.PHASES:
        raise ValueError(f"Invalid state for {task['slug']}")
    return state


def discover(config, slug=None):
    paths = [task_file(config, slug)] if slug else sorted(config["items_dir"].glob("*/task.json"))
    return [read_task(path) for path in paths]


def candidates(config, tasks):
    result = []
    for task in tasks:
        state = read_state(config, task)
        if not task["ready"] or not task.get("enabled", True) or state["status"] not in {"queued", "pushing", "waiting"}:
            continue
        if task.get("max_rounds", 0) and state["attempts"] >= task["max_rounds"]:
            continue
        if state.get("not_before", 0) > time.time():
            continue
        result.append((task, state))
    return sorted(result, key=lambda row: (row[1].get("last_started_epoch", 0), -row[0].get("priority", 0), row[0]["slug"]))


def command(config, directory, round_dir):
    argv = codex_prefix(config) + ["-C", str(config["project"]), "-s", "workspace-write", "-a", "never"]
    argv += ["--search"] if config["web_search"] else ["-c", 'web_search="disabled"']
    if config["model"]:
        argv += ["-m", config["model"]]
    if config["reasoning_effort"]:
        argv += ["-c", 'model_reasoning_effort=' + json.dumps(config["reasoning_effort"])]
    return argv + ["exec", "--skip-git-repo-check", "--ephemeral", "--add-dir", str(directory),
                   "--json", "--output-schema", str(ROOT / "templates/cardiac-round-result.schema.json"),
                   "--output-last-message", str(round_dir / "ROUND_RESULT.json"), "-"]


def preview(config, task):
    directory = task_directory(config, task["slug"])
    state = read_state(config, task)
    round_dir = directory / ".runtime/rounds/PREVIEW"
    return {"task": task, "state": state, "cwd": str(config["project"]),
            "argv": command(config, directory, round_dir), "timeout_seconds": config["round_timeout_minutes"] * 60,
            "max_rounds": config["max_rounds"], "max_wall_hours": config["max_wall_hours"],
            "max_tokens": config["max_tokens"], "dry_run": True}


def process_options():
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def terminate(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=10, check=False)
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def run_process(argv, project, round_dir, timeout):
    prompt = (f"Execute one autonomous cardiac research round. Read {round_dir / 'RESEARCH_PACKET.md'} "
              f"and {round_dir / 'PACKET.json'}. Return the required structured result for this round. "
              "Work on the actual task within the specified scope and budget.")
    env = os.environ.copy()
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    process = None
    with (round_dir / "events.jsonl").open("w", encoding="utf-8") as out, (round_dir / "stderr.log").open("w", encoding="utf-8") as err:
        try:
            process = subprocess.Popen(argv, cwd=project, env=env, stdin=subprocess.PIPE, stdout=out,
                                       stderr=err, text=True, encoding="utf-8", shell=False, **process_options())
            runtime.write_json(round_dir / "PROCESS.json", {"pid": process.pid, "started_at": runtime.now()})
            process.communicate(prompt, timeout=timeout)
            return process.returncode, "finished"
        except subprocess.TimeoutExpired:
            terminate(process)
            return 124, "timed-out"
        except KeyboardInterrupt:
            if process:
                terminate(process)
            return 130, "interrupted"
        except OSError as exc:
            err.write(str(exc))
            return 1, "spawn-error"


def execute_attempt(config, task, timeout):
    directory = task_directory(config, task["slug"])
    runtime.initialize(directory, task)
    state = read_state(config, task)
    round_id = f"round-{state['attempts'] + 1:06d}-" + uuid.uuid4().hex[:10]
    round_dir = directory / ".runtime/rounds" / round_id
    text = runtime.packet(config["workspace"], config["project"], task_file(config, task["slug"]), directory,
                          state, round_id, timeout, config["packet_max_bytes"])
    state.update(attempts=state["attempts"] + 1, active_round=round_id, status="pushing", last_started_epoch=time.time())
    runtime.write_json(directory / "state.json", state)
    runtime.prepare(directory, round_dir, text, task_file(config, task["slug"]), config["config_path"], config["workspace_config_path"])
    experiment_config = copy.deepcopy(config["workspace_data"])
    experiment_config.update(project_root=str(config["project"]), runs_dir="artifacts/experiments")
    runtime.write_json(round_dir / "EXPERIMENT_CONFIG.json", experiment_config)
    argv = command(config, directory, round_dir)
    record = {"round_id": round_id, "task": task["slug"], "started_at": runtime.now(), "argv": argv,
              "cwd": str(config["project"]), "timeout_seconds": timeout,
              "model_requested": config["model"] or "CLI default", "phase": state["phase"],
              "source_before": experiments.source_hashes(config["workspace_data"], config["project"])}
    runtime.write_json(round_dir / "RUN.json", record)
    print(f"[{runtime.now()}] {task['slug']} {round_id} phase={state['phase']}", flush=True)
    code, outcome = run_process(argv, config["project"], round_dir, timeout)
    usage = runtime.telemetry(round_dir / "events.jsonl")
    record.update(exit_code=code, process_status=outcome, finished_at=runtime.now(), usage=usage)
    updated = copy.deepcopy(state)
    updated.update(active_round=None, last_round=round_id, last_exit_code=code, last_finished_at=runtime.now())
    for key in ("input_tokens", "output_tokens"):
        updated[key] += usage[key] or 0
    updated["usage_complete"] &= usage["usage_available"]
    try:
        if code != 0:
            raise ValueError(f"Codex process {outcome}; exit={code}; inspect stderr.log/events.jsonl")
        value = runtime.read_json(round_dir / "ROUND_RESULT.json")
        verified = runtime.validate_result(value, task, round_dir, config["workspace"], config["project"])
        updated.update(status="pushing" if value["status"] == "continue" else value["status"],
                       phase=value["next_phase"], summary=value["summary"], next_action=value["next_action"],
                       blocker=value["blocker"], failures=0, last_error=None)
        updated["no_progress"] = 0 if value["progress_made"] else updated["no_progress"] + (value["status"] == "continue")
        updated["not_before"] = time.time() + config["poll_seconds"] if value["status"] == "waiting" else 0
        if value["status"] == "continue" and updated["no_progress"] >= config["max_no_progress_rounds"]:
            updated.update(status="blocked", blocker="Consecutive rounds reported no progress; inspect the recorded obstacle and change the approach")
        runtime.commit(directory, round_dir, value, updated, verified)
        record["result_status"] = updated["status"]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        record.update(result_error=str(exc), result_status="rejected")
        if (round_dir / "COMMIT.json").exists():
            record["recovery_required"] = True
        else:
            baseline = runtime.read_json(round_dir / "BASELINE.json")
            conflict = any(runtime.digest(directory / name) != expected for name, expected in baseline.items())
            conflict |= any(runtime.digest(Path(name)) != expected for name, expected in runtime.read_json(round_dir / "INPUTS.json").items())
            updated.update(failures=state["failures"] + 1, last_error=str(exc), status="queued", not_before=time.time() + config["poll_seconds"])
            if conflict or updated["failures"] >= config["max_consecutive_runtime_failures"]:
                updated["status"] = "runtime-error"
            # Never overwrite externally modified state; recovery marks this item explicitly.
            if not conflict:
                runtime.write_json(directory / "state.json", updated)
            else:
                runtime.write_json(directory / "CONFLICT.json", {"round": round_id, "error": str(exc)})
                record["recovery_required"] = True
        print(f"Round rejected: {exc}", flush=True)
    record["source_after"] = experiments.source_hashes(config["workspace_data"], config["project"])
    runtime.write_json(round_dir / "RUN.json", record)
    print(f"[{runtime.now()}] {task['slug']}: {record['result_status']}; exit={code}", flush=True)
    return record


def recover_tasks(config, tasks):
    for task in tasks:
        directory = task_directory(config, task["slug"])
        if not (directory / "state.json").exists():
            continue
        try:
            for journal in sorted((directory / ".runtime/rounds").glob("*/COMMIT.json")):
                if not (journal.parent / "APPLIED.json").exists():
                    runtime.recover(directory, journal.parent)
            state = read_state(config, task)
            if state.get("active_round") or (directory / "CONFLICT.json").exists():
                state.update(status="runtime-error", last_error="Interrupted round or concurrent state edit: inspect artifacts, then resume explicitly")
                runtime.write_json(directory / "state.json", state)
        except (OSError, ValueError, KeyError) as exc:
            state = read_state(config, task)
            state.update(status="runtime-error", last_error=str(exc))
            runtime.write_json(directory / "state.json", state)


def run_loop(config, slug=None, once=False, dry_run=False):
    tasks = discover(config, slug)
    if dry_run:
        choices = candidates(config, tasks)
        print(json.dumps(preview(config, choices[0][0]) if choices else {"message": "No eligible task"}, ensure_ascii=False, indent=2))
        return 0
    codex_prefix(config)
    if not config["project"].is_dir():
        raise ValueError("Linked project directory is missing")
    home = config["runtime_dir"]
    with runtime.lock(home / "runner.lock"):
        recover_tasks(config, tasks)
        started = time.monotonic()
        rounds, tokens = 0, 0
        launch = {"pid": os.getpid(), "slug": slug, "started_at": runtime.now(), "status": "running", "rounds": 0, "tokens": 0}
        runtime.write_json(home / "RUNNER.json", launch)
        try:
            while True:
                if (home / "STOP").exists():
                    (home / "STOP").unlink()
                    launch["status"] = "stopped"
                    break
                remaining = config["max_wall_hours"] * 3600 - (time.monotonic() - started) if config["max_wall_hours"] else float("inf")
                if remaining <= 0 or (config["max_rounds"] and rounds >= config["max_rounds"]) or (config["max_tokens"] and tokens >= config["max_tokens"]):
                    launch["status"] = "budget-exhausted"
                    break
                tasks = discover(config, slug)
                choices = candidates(config, tasks)
                if not choices:
                    pending = [task for task in tasks if task["ready"] and task.get("enabled", True)
                               and read_state(config, task)["status"] in {"queued", "pushing", "waiting"}
                               and (not task.get("max_rounds") or read_state(config, task)["attempts"] < task['max_rounds'])]
                    if once or not pending:
                        launch["status"] = "idle"
                        break
                    time.sleep(min(1, config["idle_seconds"], max(0.01, remaining)))
                    continue
                task, _ = choices[0]
                launch.update(task=task["slug"], updated_at=runtime.now())
                runtime.write_json(home / "RUNNER.json", launch)
                try:
                    record = execute_attempt(config, task, min(config["round_timeout_minutes"] * 60, remaining))
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    # A malformed packet or task-specific setup failure must not freeze other tasks.
                    directory = task_directory(config, task["slug"])
                    state = read_state(config, task)
                    state.update(status="runtime-error", last_error=f"Round preparation failed: {exc}")
                    runtime.write_json(directory / "state.json", state)
                    runtime.write_json(directory / "PREPARATION_ERROR.json", {"at": runtime.now(), "error": str(exc)})
                    launch.update(last_result_status="rejected", updated_at=runtime.now())
                    print(f"Task {task['slug']} paused: {exc}", flush=True)
                    if once:
                        launch["status"] = "round-preparation-failed"
                        break
                    continue
                rounds += 1
                tokens += (record["usage"]["input_tokens"] or 0) + (record["usage"]["output_tokens"] or 0)
                if record.get("recovery_required"):
                    recover_tasks(config, [task])
                    round_dir = task_directory(config, task["slug"]) / ".runtime/rounds" / record["round_id"]
                    if (round_dir / "APPLIED.json").exists():
                        record.update(result_status=read_state(config, task)["status"], recovered=True, recovery_required=False)
                        runtime.write_json(round_dir / "RUN.json", record)
                launch.update(rounds=rounds, tokens=tokens, last_round=record["round_id"], last_result_status=record["result_status"])
                runtime.write_json(home / "RUNNER.json", launch)
                if record["exit_code"] == 130:
                    launch["status"] = "interrupted"
                    break
                if config["max_tokens"] and not record["usage"]["usage_available"]:
                    launch["status"] = "usage-unavailable"
                    break
                if once:
                    launch["status"] = "round-finished"
                    break
        except KeyboardInterrupt:
            launch["status"] = "interrupted"
        except (OSError, ValueError, KeyError, RuntimeError):
            launch["status"] = "runtime-error"
            raise
        finally:
            launch["finished_at"] = runtime.now()
            runtime.write_json(home / "RUNNER.json", launch)
        print(json.dumps(launch, ensure_ascii=False, indent=2))
        return 1 if launch["status"] in {"usage-unavailable", "runtime-error"} or launch.get("last_result_status") == "rejected" else 0


def doctor(config):
    errors, warnings = [], []
    prefix = codex_prefix(config)
    for args in (["--version"], ["exec", "--help"], ["login", "status"]):
        check = subprocess.run(prefix + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, **process_options())
        if args[0] == "login":
            if check.returncode:
                warnings.append("CLI login status is not authenticated; custom providers may use separate credentials. Verify a bounded round before long runs.")
        elif check.returncode:
            errors.append("Codex CLI self-check failed: " + " ".join(args))
        elif args[0] == "exec" and any(flag not in check.stdout for flag in ("--output-schema", "--add-dir", "--json")):
            errors.append("Codex CLI is missing required noninteractive flags")
    if not config["project"].is_dir():
        errors.append("Linked project is missing")
    print(json.dumps({"codex_command": prefix, "project": str(config["project"]), "tasks": len(discover(config)),
                      "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def start(config, args):
    home = config["runtime_dir"]
    if runtime.locked(home / "runner.lock"):
        raise ValueError("Research runner is already active")
    codex_prefix(config)
    home.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--config", str(config["config_path"]), "run"]
    for name in ("slug", "max_rounds", "max_hours", "max_tokens"):
        value = getattr(args, name, None)
        if value is not None:
            argv += ["--" + name.replace("_", "-"), str(value)]
    with (home / "runner.log").open("ab") as stream:
        process = subprocess.Popen(argv, cwd=config["workspace"], stdin=subprocess.DEVNULL, stdout=stream,
                                   stderr=subprocess.STDOUT, **process_options())
    print(f"Started PID {process.pid}; use status/watch to check startup; log={home / 'runner.log'}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "research-queue.json")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "list", "status", "stop"):
        sub.add_parser(name)
    add = sub.add_parser("add")
    add.add_argument("slug")
    add.add_argument("title")
    add.add_argument("--objective", required=True)
    add.add_argument("--criterion", action="append", required=True)
    add.add_argument("--scope", default="Local code, tests and bounded experiments within the existing project authorization; no new remote submissions")
    add.add_argument("--ready", action="store_true")
    for name in ("enable", "resume", "pause", "packet", "plan"):
        sub.add_parser(name).add_argument("slug")
    for name in ("run", "once", "start"):
        p = sub.add_parser(name)
        p.add_argument("--slug")
        p.add_argument("--max-rounds", type=int)
        p.add_argument("--max-hours", type=float)
        p.add_argument("--max-tokens", type=int)
        p.add_argument("--dry-run", action="store_true")
    watch = sub.add_parser("watch")
    watch.add_argument("--lines", type=int, default=25)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        for attr, key in (("max_rounds", "max_rounds"), ("max_hours", "max_wall_hours"), ("max_tokens", "max_tokens")):
            value = getattr(args, attr, None)
            if value is not None:
                if value < 0 or not math.isfinite(value):
                    raise ValueError("Budgets must be finite and nonnegative; 0 means no limit")
                config[key] = value
        if args.command == "check":
            return doctor(config)
        if args.command in {"run", "once", "start"}:
            if args.command == "start" and not args.dry_run:
                return start(config, args)
            return run_loop(config, args.slug, once=args.command == "once", dry_run=args.dry_run)
        if args.command == "stop":
            runtime.atomic(config["runtime_dir"] / "STOP", b"Stop at the next round boundary\n")
            print("Stop requested; the active round can finish and commit its state")
        elif args.command in {"list", "status"}:
            print(f"runner_active={runtime.locked(config['runtime_dir'] / 'runner.lock')}")
            for task in discover(config):
                state = read_state(config, task)
                print(f"{task['slug']}: ready={task['ready']} status={state['status']} rounds={state['attempts']} phase={state['phase']}")
            record = config["runtime_dir"] / "RUNNER.json"
            if args.command == "status" and record.exists():
                print(record.read_text(encoding="utf-8"))
        elif args.command == "watch":
            path = config["runtime_dir"] / "runner.log"
            if path.exists():
                with path.open("rb") as stream:
                    stream.seek(max(0, path.stat().st_size - 65536))
                    print("\n".join(stream.read().decode("utf-8", errors="replace").splitlines()[-max(1, args.lines):]))
        elif args.command in {"plan", "packet"}:
            task = read_task(task_file(config, args.slug))
            if args.command == "plan":
                print(json.dumps(preview(config, task), ensure_ascii=False, indent=2))
            else:
                print(runtime.packet(config["workspace"], config["project"], task_file(config, args.slug), task_directory(config, args.slug),
                                     read_state(config, task), "PREVIEW", config["round_timeout_minutes"] * 60, config["packet_max_bytes"]))
        elif args.command in {"add", "enable"}:
            # New/disabled task definitions may be prepared while another task is running.
            with runtime.lock(config["runtime_dir"] / "definitions.lock"):
                path = task_file(config, args.slug)
                if args.command == "add":
                    if path.exists():
                        raise ValueError("Task already exists")
                    runtime.write_json(path, {"slug": args.slug, "title": args.title, "objective": args.objective, "scope": args.scope,
                                             "ready": args.ready, "enabled": True, "priority": 0, "max_rounds": 0,
                                             "acceptance": [{"id": f"C{i+1}", "description": text} for i, text in enumerate(args.criterion)]})
                elif args.command == "enable":
                    task = read_task(path)
                    if not task["ready"] or not task.get("enabled", True):
                        task.update(ready=True, enabled=True)
                        runtime.write_json(path, task)
                print(f"{args.command}: {args.slug}")
        else:
            with runtime.lock(config["runtime_dir"] / "runner.lock"):
                task = read_task(task_file(config, args.slug))
                directory = task_directory(config, args.slug)
                runtime.initialize(directory, task)
                recover_tasks(config, [task])
                if any(not (p.parent / "APPLIED.json").exists() for p in (directory / ".runtime/rounds").glob("*/COMMIT.json")):
                    raise ValueError("Resolve the conflicting transaction before resuming")
                state = read_state(config, task)
                state.update(status="paused" if args.command == "pause" else "queued", active_round=None, not_before=0, failures=0, no_progress=0)
                runtime.write_json(directory / "state.json", state)
                (directory / "CONFLICT.json").unlink(missing_ok=True)
                print(f"{args.command}: {args.slug}")
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
