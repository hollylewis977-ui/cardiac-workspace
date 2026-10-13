import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import research_runtime as runtime


class ClaimFieldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.workspace = root / "workspace"
        self.project = root / "project"
        self.project.mkdir()
        self.round_dir = self.workspace / "rounds/r1"
        (self.round_dir / "artifacts").mkdir(parents=True)
        (self.round_dir / "artifacts/check.log").write_text("ok", encoding="utf-8")
        runtime.write_json(self.round_dir / "PACKET.json", {"round_id": "r1", "packet_sha256": "abc"})
        self.task = {"acceptance": [{"id": "C1", "description": "fixture"}]}
        self.ref = "workspace:rounds/r1/artifacts/check.log"

    def result(self, **extra):
        return {"schema_version": 1, "round_id": "r1", "packet_sha256": "abc", "status": "continue",
                "next_phase": "assess", "progress_made": True, "summary": "s", "next_action": "n",
                "current_state": "c", "blocker": "", "evidence": [self.ref],
                "checks": [{"command": "x", "exit_code": 0, "log": self.ref}],
                "acceptance": [{"id": "C1", "outcome": "not-run", "evidence": []}], **extra}

    def validate(self, value):
        return runtime.validate_result(value, self.task, self.round_dir, self.workspace, self.project)

    def progress(self, **override):
        return {"claimed_kind": "route-elimination", "main_problem_effect": "none",
                "scope_limitations": "single seed", "evidence_level": "experimental", **override}

    def test_result_without_claim_fields_is_valid(self):
        self.validate(self.result())

    def test_progress_with_known_kind_and_level_is_valid(self):
        self.validate(self.result(progress=self.progress()))

    def test_progress_rejects_unknown_kind(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(progress=self.progress(claimed_kind="breakthrough")))

    def test_progress_rejects_level_above_proof_draft(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(progress=self.progress(evidence_level="agent-verified")))

    def test_new_claim_needs_level_dimensions_and_verified_evidence(self):
        claim = {"id": "A9", "statement": "s", "level": "experimental", "dimensions": ["prediction"], "evidence": [self.ref]}
        self.validate(self.result(new_claims=[claim]))
        with self.assertRaises(ValueError):
            self.validate(self.result(new_claims=[{**claim, "level": "human-verified"}]))
        with self.assertRaises(ValueError):
            self.validate(self.result(new_claims=[{**claim, "dimensions": ["vibes"]}]))
        with self.assertRaises(ValueError):
            self.validate(self.result(new_claims=[{**claim, "evidence": ["workspace:missing.log"]}]))


if __name__ == "__main__":
    unittest.main()
