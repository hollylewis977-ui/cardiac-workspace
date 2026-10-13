import contextlib
import copy
import io
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cardiac_workspace as cardiac


def npy_bytes(shape, dtype="<f2"):
    header = repr({"descr": dtype, "fortran_order": False, "shape": tuple(shape)}).encode("ascii") + b"\n"
    data = b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header)) + header
    return data + bytes(math.prod(shape) * int(dtype[-1])) if dtype[-1].isdigit() else data


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "agent space"
        self.workspace.mkdir()
        self.project = self.root / "PDE \u5fc3\u810f code"
        (self.project / "code").mkdir(parents=True)
        (self.project / "data").mkdir()
        (self.project / "code" / "main.py").write_text("print('source')\n", encoding="utf-8")
        self.config_path = self.workspace / "config.json"
        self.config = {
            "schema_version": 1, "project_root": "../" + self.project.name,
            "data_dir": "data", "runs_dir": "runs", "threads": 1,
            "entrypoints": ["code/main.py"], "source_roots": ["code"],
            "expected_data": {"batches": 1, "samples_per_batch": 1, "frames": 3, "nodes": 2},
            "tasks": {"test": {"cwd": "code", "argv": ["{python}", "-c", "print('ok')"],
                               "timeout_seconds": 5, "requires_data": False, "dependencies": []}},
        }
        self.write_config()

    def write_config(self):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def data(self, compression=zipfile.ZIP_STORED, wrong_shape=False):
        shapes = {"u": (1, 3, 2), "ca": (1, 3, 2), "x_uni": (1, 2, 2),
                  "x_mesh": (1, 2, 2), "full_init": (1, 42)}
        if wrong_shape:
            shapes["ca"] = (1, 2, 3)
        with zipfile.ZipFile(self.project / "data" / "batch_000.npz", "w", compression=compression) as archive:
            for name, shape in shapes.items():
                archive.writestr(name + ".npy", npy_bytes(shape, "<f2" if name in ("u", "ca") else "<f4"))

    def run_task(self):
        self.write_config()
        config, path, project, runs = cardiac.load_config(self.config_path)
        with contextlib.redirect_stdout(io.StringIO()):
            return cardiac.run_task(config, path, project, runs, "test")

    def test_paths_use_config_directory_and_argv_preserves_spaces(self):
        config, _, project, runs = cardiac.load_config(self.config_path)
        plan = cardiac.make_plan(config, project, runs, "test")
        self.assertEqual(project, self.project.resolve())
        self.assertEqual(plan["cwd"], str(self.project / "code"))
        self.assertEqual(plan["argv"][0], sys.executable)
        self.assertFalse(runs.exists())

    def test_doctor_reads_headers_without_creating_outputs(self):
        self.data()
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        report = cardiac.doctor(self.config, self.project)
        self.assertTrue(report["ready"], report["errors"])
        self.assertEqual(report["data"]["files"][0]["arrays"]["u"]["shape"], [1, 3, 2])
        self.assertEqual(before, sorted(p.relative_to(self.root) for p in self.root.rglob("*")))

    def test_compressed_npz_rejected_for_memmap_loader(self):
        self.data(compression=zipfile.ZIP_DEFLATED)
        report = cardiac.doctor(self.config, self.project)
        self.assertFalse(report["ready"])
        self.assertTrue(any("ZIP_STORED" in error for error in report["errors"]))

    def test_shape_mismatch_is_not_ready(self):
        self.data(wrong_shape=True)
        self.assertFalse(cardiac.doctor(self.config, self.project)["ready"])

    def test_truncated_array_payload_is_not_ready(self):
        self.data()
        path = self.project / "data" / "batch_000.npz"
        with zipfile.ZipFile(path) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        members["u.npy"] = members["u.npy"][:-2]
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in members.items():
                archive.writestr(name, content)
        self.assertFalse(cardiac.doctor(self.config, self.project)["ready"])

    def test_missing_data_prevents_training_and_leaves_no_run(self):
        self.config["tasks"]["test"]["requires_data"] = True
        with self.assertRaisesRegex(ValueError, "preflight"):
            self.run_task()
        self.assertFalse((self.workspace / "runs").exists())

    def test_literal_shell_metacharacters_and_unicode_are_preserved(self):
        token = "space \u5fc3\u810f; $(echo unexpected) `literal`"
        self.config["tasks"]["test"]["argv"] = ["{python}", "-c", "import sys; print(sys.argv[1])", token]
        result = self.run_task()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(Path(result["stdout"]).read_text(encoding="utf-8").strip(), token)
        self.assertEqual(result["evidence"]["prediction"], "not-assessed")
        self.assertEqual(result["evidence"]["personalization"], "not-assessed")
        self.assertIn("code/main.py", result["source_sha256"])

    def test_failure_is_recorded_and_does_not_freeze_next_run(self):
        self.config["tasks"]["test"]["argv"] = ["{python}", "-c", "import sys; print('bad',file=sys.stderr); sys.exit(7)"]
        failed = self.run_task()
        self.assertEqual((failed["status"], failed["exit_code"]), ("failed", 7))
        self.assertIn("bad", Path(failed["stderr"]).read_text(encoding="utf-8"))
        self.config["tasks"]["test"]["argv"] = ["{python}", "-c", "print('recovered')"]
        passed = self.run_task()
        self.assertEqual(passed["status"], "completed")
        self.assertNotEqual(failed["run_id"], passed["run_id"])
        old = json.loads((Path(failed["stdout"]).parent / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(old["exit_code"], 7)

    def test_timeout_has_persisted_terminal_status(self):
        self.config["tasks"]["test"].update(argv=["{python}", "-c", "import time; time.sleep(30)"], timeout_seconds=0.05)
        result = self.run_task()
        self.assertEqual((result["status"], result["exit_code"]), ("timed-out", 124))
        saved = json.loads((Path(result["stdout"]).parent / "run.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(saved["finished_at"])
        self.assertEqual(saved["evidence"]["prediction"], "not-assessed")

    def test_spawn_failure_is_recorded(self):
        self.config["tasks"]["test"]["argv"] = [str(self.root / "nonexistent-executable")]
        result = self.run_task()
        self.assertEqual(result["status"], "failed")
        self.assertIn("error", result)

    def test_interrupt_is_recorded(self):
        with patch.object(cardiac.subprocess, "run", side_effect=KeyboardInterrupt):
            result = self.run_task()
        self.assertEqual((result["status"], result["exit_code"]), ("interrupted", 130))

    def test_source_changes_are_reported(self):
        self.config["tasks"]["test"]["argv"] = ["{python}", "-c", "from pathlib import Path; Path('main.py').write_text('changed')"]
        result = self.run_task()
        self.assertTrue(result["source_changed_during_run"])

    def test_unsafe_paths_and_unbounded_timeouts_rejected(self):
        original = copy.deepcopy(self.config)
        for field, value in [("runs_dir", "../outside"), ("cwd", "../../outside"), ("timeout_seconds", 0), ("timeout_seconds", float("inf"))]:
            with self.subTest(field=field, value=value):
                self.config = copy.deepcopy(original)
                if field == "runs_dir":
                    self.config[field] = value
                else:
                    self.config["tasks"]["test"][field] = value
                self.write_config()
                with self.assertRaises(ValueError):
                    cardiac.load_config(self.config_path)

    def test_invalid_headers_rejected(self):
        for content in [b"bad", b"\x93NUMPY\x01\x00\x10", npy_bytes((1,), "|O"),
                        b"\x93NUMPY\x02\x00" + struct.pack("<I", 1000000)]:
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    cardiac.npy_header(io.BytesIO(content))

    def test_packet_is_bounded_and_contains_real_source_context(self):
        result = cardiac.packet("Inspect the AR baseline")
        self.assertIn("TC_GCN_server", result)
        self.assertLessEqual(len(result.encode("utf-8")), 32768)


if __name__ == "__main__":
    unittest.main()
