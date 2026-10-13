import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CURL_STUB = r"""
import json
import os
import sys
from pathlib import Path
args = sys.argv[1:]
url = next(arg for arg in args if arg.startswith("https://"))
if "resolveHandle" in url:
    result = {"did": "did:plc:test"}
elif "plc.directory" in url:
    result = {"service": [{"type": "AtprotoPersonalDataServer", "serviceEndpoint": "https://pds.test"}]}
elif "createSession" in url:
    result = {"did": "did:plc:test", "accessJwt": "test-token"}
elif "getRecord" in url:
    result = {"value": {"repoDid": "did:plc:repo"}}
elif "uploadBlob" in url:
    result = {"blob": {"ref": {"$link": "test-blob"}, "mimeType": "application/octet-stream", "size": 4}}
elif "createRecord" in url:
    payload = json.loads(args[args.index("-d") + 1])
    Path(os.environ["UPLOAD_RECORD"]).write_text(json.dumps(payload))
    result = {"uri": "at://test/artifact"}
else:
    raise ValueError(url)
print(json.dumps(result))
"""


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name)
        self.env = os.environ | {
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Release test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Release test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "TANGLED_PIPELINE_KIND": "push",
            "TANGLED_REF_NAME": "2.0.5",
            "ATP_IDENTIFIER": "test.invalid",
            "ATP_APP_PASSWORD": "test-password",
            "TANGLED_REPO_NAME": "bibata-cursor",
            "UPLOAD_RECORD": str(self.repository / "uploaded.json"),
        }
        self.env.pop("TANGLED_RELEASE_TAG", None)
        self.git("init", "-q")
        self.git("commit", "-q", "--allow-empty", "-m", "Create release test fixture")
        (self.repository / "dist").mkdir()
        (self.repository / "dist" / "fixture.zip").write_bytes(b"test")
        tools = self.repository / "tools"
        tools.mkdir()
        curl = tools / "curl"
        curl.write_text(f"#!{sys.executable}\n" + CURL_STUB)
        curl.chmod(0o755)
        self.env["PATH"] = str(tools) + os.pathsep + self.env["PATH"]

    def git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repository,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def publish(self, **env):
        return subprocess.run(
            ["bash", str(ROOT / "scripts/publish-tangled-artifacts.sh")],
            cwd=self.repository,
            env=self.env | env,
            capture_output=True,
            text=True,
        )

    def assert_uploaded(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((self.repository / "uploaded.json").read_text())["record"]
        tag_hash = self.git("rev-parse", "refs/tags/2.0.5")
        expected = base64.b64encode(bytes.fromhex(tag_hash)).decode().rstrip("=")
        self.assertEqual(record["tag"]["$bytes"], expected)
        self.assertEqual(record["name"], "fixture.zip")

    def test_lightweight_tag_upload(self):
        self.git("tag", "2.0.5")
        self.assert_uploaded(self.publish())

    def test_annotated_tag_upload(self):
        self.git("tag", "-a", "2.0.5", "-m", "Release 2.0.5")
        self.assert_uploaded(self.publish(TANGLED_REF_NAME="refs/tags/2.0.5"))

    def test_manual_branch_rerun_at_tag(self):
        self.git("tag", "2.0.5")
        self.assert_uploaded(
            self.publish(TANGLED_PIPELINE_KIND="manual", TANGLED_REF_NAME="main")
        )

    def test_manual_untagged_build_does_not_upload(self):
        result = self.publish(TANGLED_PIPELINE_KIND="manual", TANGLED_REF_NAME="main")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipping artifact publishing", result.stdout)
        self.assertFalse((self.repository / "uploaded.json").exists())

    def test_mismatched_tag_does_not_upload(self):
        self.git("tag", "2.0.5")
        self.git("commit", "-q", "--allow-empty", "-m", "Move beyond release tag")
        result = self.publish(TANGLED_PIPELINE_KIND="manual")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match", result.stderr)
        self.assertFalse((self.repository / "uploaded.json").exists())

    def test_ambiguous_tags_require_explicit_selection(self):
        self.git("tag", "2.0.5")
        self.git("tag", "other-release")
        result = self.publish(TANGLED_PIPELINE_KIND="manual", TANGLED_REF_NAME="main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Multiple release tags", result.stderr)
        self.assert_uploaded(
            self.publish(
                TANGLED_PIPELINE_KIND="manual",
                TANGLED_REF_NAME="main",
                TANGLED_RELEASE_TAG="2.0.5",
            )
        )

    def test_invalid_explicit_tag_does_not_upload(self):
        result = self.publish(
            TANGLED_PIPELINE_KIND="manual", TANGLED_RELEASE_TAG="missing"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Release tag not found", result.stderr)
        self.assertFalse((self.repository / "uploaded.json").exists())


if __name__ == "__main__":
    unittest.main()
