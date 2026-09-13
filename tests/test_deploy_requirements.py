"""
Regression guard for the real bug found on the live Render deployment:
the top-level `livekit` PyPI package does not include the `api`
submodule that agent/voice/token.py needs — that's the separate
`livekit-api` package. The full dev requirements.txt masked this (it
comes in transitively via livekit-agents), so this test checks
requirements-web.txt explicitly names it, rather than relying on
re-deploying to notice the next time someone edits that file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_requirements_web_includes_livekit_api():
    content = (Path(__file__).parent.parent / "requirements-web.txt").read_text()
    assert "livekit-api" in content, (
        "requirements-web.txt must list livekit-api explicitly — the bare "
        "'livekit' package does not provide livekit.api, which agent/voice/"
        "token.py's issue_room_token() needs. This exact gap took down "
        "/token in production once already."
    )
