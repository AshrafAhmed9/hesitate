"""
Regression guard for the real bug found on the live Render deployment:
the top-level `livekit` PyPI package does not include the `api`
submodule that agent/voice/token.py needs — that's the separate
`livekit-api` package. The full dev requirements.txt masked this (it
comes in transitively via livekit-agents), so this test checks
requirements-deploy.txt (what Render actually installs) explicitly
names it, rather than relying on re-deploying to notice the next time
someone edits that file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_requirements_deploy_includes_livekit_api():
    content = (Path(__file__).parent.parent / "requirements-deploy.txt").read_text()
    assert "livekit-api" in content, (
        "requirements-deploy.txt must list livekit-api explicitly — the bare "
        "'livekit' package does not provide livekit.api, which agent/voice/"
        "token.py's issue_room_token() needs. This exact gap took down "
        "/token in production once already."
    )


def test_requirements_deploy_excludes_torch():
    lines = (Path(__file__).parent.parent / "requirements-deploy.txt").read_text().splitlines()
    deps = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    assert not any("sentence-transformers" in d or "torch" in d for d in deps), (
        "agent/gate/semantic.py (the only consumer of sentence-transformers/"
        "torch) is never imported by the deployed agent or web app — only "
        "by tests. Installing it on Render wastes build time/RAM and "
        "contributed to an OOM crash-loop found on 2026-09-14."
    )
