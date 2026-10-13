"""Cardiac adaptation of the original bounded packets, journal and telemetry runtime."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile


PHASES = {"analyze", "implement", "experiment", "assess"}
STATES = {"queued", "pushing", "waiting", "blocked", "completed", "runtime-error", "paused"}
PROTECTED = ("state.json", "CURRENT_STATE.md", "progress.md", "verification-ledger.md")
KINDS = {"frontier-advance", "route-elimination", "enabling-result", "experimental-signal", "reformulation",
         "repeat", "inconclusive", "regression", "candidate-solution"}
LEVELS = {"conjecture", "experimental", "partial-result", "proof-draft"}
DIMENSIONS = {"code", "numerics", "data", "prediction", "personalization", "uncertainty"}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(path.read_bytes()) if path.is_file() else None


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def write_json(path, value):
    atomic(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def local(root, name):
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes {root}: {name}")
    return path


@contextmanager
def lock(path, create=True):
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b" if create else "r+b") as stream:
        if path.stat().st_size == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError("Another research runner holds the workspace lock") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def locked(path):
    if not path.exists():
        return False
    try:
        with lock(path, create=False):
            return False
    except RuntimeError:
        return True


def initial_state(task):
    return {"slug": task["slug"], "status": "queued", "phase": "analyze", "attempts": 0,
            "failures": 0, "no_progress": 0, "next_action": task["objective"], "summary": "Not started",
            "not_before": 0, "active_round": None, "last_round": None,
            "input_tokens": 0, "output_tokens": 0, "usage_complete": True}


def initialize(directory, task):
    directory.mkdir(parents=True, exist_ok=True)
    initial = {"state.json": json.dumps(initial_state(task), ensure_ascii=False, indent=2) + "\n",
               "CURRENT_STATE.md": f"# {task['title']}\n\n{task['objective']}\n\nNext: analyze existing evidence.\n",
               "progress.md": "# Research rounds\n", "verification-ledger.md": "# Reported evidence\n"}
    for name, body in initial.items():
        path = directory / name
        if not path.exists():
            atomic(path, body.encode("utf-8"))


def packet(workspace, project, item_file, directory, state, round_id, timeout, max_bytes):
    task = read_json(item_file)
    parts = ["# Autonomous cardiac research round", f"Round ID: {round_id}",
             f"Project: {project}\nWorkspace: {workspace}\nTask state: {directory}",
             f"Time limit for this round: {timeout:g} seconds. Current phase: {state['phase']}",
             "Task definition (fixed scope and acceptance):\n" + json.dumps(task, ensure_ascii=False, indent=2),
             "Runner state:\n" + json.dumps(state, ensure_ascii=False, indent=2)]
    files = [workspace / "AGENTS.md", workspace / "agents/core/research-core.md",
             workspace / "agents/core/queue-core.md", workspace / "agents/protocols/round-result.md",
             workspace / "projects/cardiac-ep/problem.md", workspace / "projects/cardiac-ep/CURRENT_STATE.md",
             workspace / "projects/cardiac-ep/claim-map.md", workspace / "projects/cardiac-ep/SOURCE_MAP.md",
             directory / "CURRENT_STATE.md"]
    protocol = {"analyze": "explore", "implement": "computation", "experiment": "data-validation", "assess": "model-validation"}
    files.append(workspace / f"agents/protocols/{protocol[state['phase']]}.md")
    for path in files:
        body = path.read_text(encoding="utf-8-sig") if path.exists() else (task['objective'] if path == directory / 'CURRENT_STATE.md' else '')
        if not body:
            raise ValueError(f"Missing required research guidance: {path}")
        if path == directory / "CURRENT_STATE.md" and (len(body.encode("utf-8")) > 12288 or len(body.splitlines()) > 300):
            raise ValueError("Task CURRENT_STATE exceeds 12 KiB/300 lines")
        parts.append(f"\nSource: {path}\n{body}")
    round_config = directory / ".runtime/rounds" / round_id / "EXPERIMENT_CONFIG.json"
    parts.append(f"""For predefined experiments, use this round's configuration:
python \"{workspace / 'tools/cardiac_workspace.py'}\" --config \"{round_config}\" run <task>
It preserves the project and data paths and writes logs under this round's artifacts/experiments/.
Do not use the helper's default configuration from a queue worker; its global output directory is
outside this worker's writable task directory. Direct experiment commands can also use artifacts/.
""")
    parts.append("""Continue from next_action and cited evidence. Make a concrete contribution: analyze a failure,
modify code, run an authorized experiment, or evaluate its results. Choose the next phase from evidence;
do not stop simply because one bounded round ends. Preserve existing edits and running experiments.
Inspect the previous round directory after an interrupted attempt before repeating any experiment.
Do not edit task.json, runner configuration, state.json, CURRENT_STATE.md, progress.md or the
verification-ledger.md in the task directory. The runner commits those files. Do not rewrite the global
research state; other sessions may be updating it. Write code in the linked project and supporting notes
or logs in this round's artifacts directory. Existing cardiac_workspace.py is a subordinate experiment tool.
Do not recursively launch this queue or extra agents. Do not change permissions or submit/cancel remote
jobs beyond the task's existing authorization. Missing permissions/resources are a concrete blocker.
Return the required JSON result. Copy round_id and packet_sha256 from PACKET.json. Use continue when
there is a next action, waiting for external jobs, blocked for a specific missing prerequisite, and completed
only when every task acceptance criterion is passed with existing direct evidence. Every evidence/log
reference uses workspace:<relative path> or project:<relative path>. Report execution success separately
from scientific validity. A plan, smoke run or passing unit tests cannot alone establish prediction quality.
""")
    text = "\n\n".join(parts)
    if len(text.encode("utf-8")) > max_bytes:
        raise ValueError("Research packet exceeds limit; shorten indexes without discarding evidence")
    return text


def prepare(directory, round_dir, text, item_file, config_file, workspace_config):
    round_dir.mkdir(parents=True, exist_ok=False)
    (round_dir / "artifacts").mkdir()
    atomic(round_dir / "RESEARCH_PACKET.md", text.encode("utf-8"))
    write_json(round_dir / "PACKET.json", {"round_id": round_dir.name, "packet_sha256": sha(text.encode("utf-8"))})
    baseline = {name: digest(directory / name) for name in PROTECTED}
    write_json(round_dir / "BASELINE.json", baseline)
    write_json(round_dir / "INPUTS.json", {str(path): digest(path) for path in (item_file, config_file, workspace_config)})


def evidence_file(reference, workspace, project):
    if not isinstance(reference, str) or ":" not in reference:
        raise ValueError("Evidence must use workspace: or project: relative paths")
    scope, relative = reference.split(":", 1)
    if scope not in {"workspace", "project"}:
        raise ValueError("Invalid evidence scope")
    path = local(workspace if scope == "workspace" else project, relative)
    if not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError(f"Evidence must be an existing file <=16 MiB; cite a summary/manifest for large artifacts: {reference}")
    return path


def validate_claims(value, verified):
    progress = value.get("progress")
    if progress is not None:
        if not isinstance(progress, dict) or progress.get("claimed_kind") not in KINDS or progress.get("evidence_level") not in LEVELS:
            raise ValueError("progress needs a known claimed_kind and evidence_level at most proof-draft")
        for key in ("main_problem_effect", "scope_limitations"):
            if not isinstance(progress.get(key), str) or not progress[key].strip():
                raise ValueError(f"progress.{key} must be nonempty text")
    for claim in value.get("new_claims") or []:
        if not isinstance(claim, dict) or claim.get("level") not in LEVELS:
            raise ValueError("new_claims entries need a level at most proof-draft")
        for key in ("id", "statement"):
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                raise ValueError(f"new_claims.{key} must be nonempty text")
        dims = claim.get("dimensions")
        if not isinstance(dims, list) or not dims or not set(dims) <= DIMENSIONS:
            raise ValueError("new_claims.dimensions must list known verification dimensions")
        if not isinstance(claim.get("evidence"), list) or any(ref not in verified for ref in claim["evidence"]):
            raise ValueError("new_claims.evidence must be in the verified list")


def validate_result(value, task, round_dir, workspace, project):
    metadata = read_json(round_dir / "PACKET.json")
    if value.get("schema_version") != 1 or value.get("round_id") != round_dir.name or value.get("packet_sha256") != metadata["packet_sha256"]:
        raise ValueError("Result schema, round ID or packet hash mismatch")
    if value.get("status") not in {"continue", "waiting", "blocked", "completed"} or value.get("next_phase") not in PHASES:
        raise ValueError("Invalid round status/phase")
    if type(value.get("progress_made")) is not bool:
        raise ValueError("progress_made must be a boolean")
    for key in ("summary", "next_action", "current_state"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError(f"Missing {key}")
        if len(value[key].encode("utf-8")) > 12288 or len(value[key].splitlines()) > 300:
            raise ValueError(f"Oversized {key}")
    if not isinstance(value.get("blocker"), str):
        raise ValueError("blocker must be text, empty when not blocked")
    if value["status"] in {"waiting", "blocked"} and not value["blocker"].strip():
        raise ValueError("Waiting/blocked requires a concrete reason")
    evidence = value.get("evidence")
    checks = value.get("checks")
    acceptance = value.get("acceptance")
    if not all(isinstance(x, list) for x in (evidence, checks, acceptance)) or len(evidence) > 32 or len(checks) > 32:
        raise ValueError("Invalid/bloated evidence, checks or acceptance lists")
    if not all(isinstance(row, dict) for row in checks + acceptance) or not all(isinstance(ref, str) for ref in evidence):
        raise ValueError("Malformed evidence/check/acceptance entries")
    verified = {ref: digest(evidence_file(ref, workspace, project)) for ref in evidence}
    for check in checks:
        if not isinstance(check.get("command"), str) or not check["command"].strip():
            raise ValueError("Check needs a command or exact inspection description")
        if check.get("exit_code") is not None and type(check["exit_code"]) is not int:
            raise ValueError("Invalid check exit code")
        if check.get("log") not in verified:
            raise ValueError("Check log must be cited as evidence")
    expected = {row["id"] for row in task["acceptance"]}
    if len(acceptance) != len(expected) or {row.get("id") for row in acceptance} != expected:
        raise ValueError("Acceptance must cover exactly the original task criteria")
    for row in acceptance:
        if row.get("outcome") not in {"passed", "failed", "not-run"} or not isinstance(row.get("evidence"), list):
            raise ValueError("Invalid acceptance outcome/evidence")
        if any(ref not in verified for ref in row["evidence"]):
            raise ValueError("Acceptance evidence must be in the verified list")
        if row["outcome"] == "passed" and not row["evidence"]:
            raise ValueError("Passed criterion requires direct evidence")
    validate_claims(value, verified)
    if value["status"] == "completed":
        if any(row["outcome"] != "passed" for row in acceptance) or not checks or any(row["exit_code"] != 0 for row in checks):
            raise ValueError("Completion requires all criteria passed and successful recorded checks")
        if value["blocker"].strip():
            raise ValueError("Completed task cannot have a blocker")
    return verified


def recover(directory, round_dir):
    if (round_dir / "APPLIED.json").exists():
        return
    journal = read_json(round_dir / "COMMIT.json")
    for name, entry in journal.items():
        if name not in PROTECTED or digest(directory / name) not in (entry["before"], entry["after"]):
            raise ValueError(f"Concurrent state edit prevents recovery: {name}")
        if digest(round_dir / "after" / name) != entry["after"]:
            raise ValueError(f"Corrupt transaction payload: {name}")
    for name, entry in journal.items():
        if digest(directory / name) != entry["after"]:
            atomic(directory / name, (round_dir / "after" / name).read_bytes())
    write_json(round_dir / "APPLIED.json", {"at": now(), "result_sha256": digest(round_dir / "ROUND_RESULT.json")})


def commit(directory, round_dir, value, state, verified):
    if (round_dir / "COMMIT.json").exists():
        recover(directory, round_dir)
        return
    baseline = read_json(round_dir / "BASELINE.json")
    for name, expected in baseline.items():
        if digest(directory / name) != expected:
            raise ValueError(f"Protected state changed during round: {name}")
    for name, expected in read_json(round_dir / "INPUTS.json").items():
        if digest(Path(name)) != expected:
            raise ValueError("Task or runner configuration changed during round; preserve result for review")
    entry = f"\n## {now()} / {round_dir.name}\n\n{value['summary']}\n\nNext: {value['next_action']}\nResult: {round_dir / 'ROUND_RESULT.json'}\n"
    evidence = entry + "\n".join(f"- {ref}; sha256={hashed}" for ref, hashed in verified.items()) + "\n"
    updates = {"state.json": (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
               "CURRENT_STATE.md": (value["current_state"].rstrip() + "\n").encode("utf-8"),
               "progress.md": (directory / "progress.md").read_bytes() + entry.encode("utf-8"),
               "verification-ledger.md": (directory / "verification-ledger.md").read_bytes() + evidence.encode("utf-8")}
    journal = {}
    for name, data in updates.items():
        atomic(round_dir / "before" / name, (directory / name).read_bytes())
        atomic(round_dir / "after" / name, data)
        journal[name] = {"before": baseline[name], "after": sha(data)}
    write_json(round_dir / "COMMIT.json", journal)
    recover(directory, round_dir)


def telemetry(path):
    usage = {key: None for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")}
    turns, calls, malformed = 0, set(), 0
    thread_id = None
    if path.is_file():
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except ValueError:
                    malformed += 1
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "thread.started":
                    thread_id = event.get("thread_id")
                if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                    turns += 1
                    for key in usage:
                        number = event["usage"].get(key)
                        if type(number) is int and number >= 0:
                            usage[key] = (usage[key] or 0) + number
                item = event.get("item", {})
                if isinstance(item, dict) and item.get("type") in {"command_execution", "mcp_tool_call", "web_search", "tool_call"} and item.get("id"):
                    calls.add(item["id"])
    return {**usage, "completed_turns": turns, "tool_calls": len(calls), "thread_id": thread_id,
            "non_json_lines": malformed, "usage_available": turns > 0 and usage['input_tokens'] is not None and usage['output_tokens'] is not None}
