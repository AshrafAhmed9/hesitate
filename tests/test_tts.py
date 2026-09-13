"""Locks in the ElevenLabs quota guard (COMPETITION.md decision: reserved
for final demo + finale only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.voice.tts import speak, TTSMode


def test_default_mode_spends_no_quota():
    r = speak("This should not cost anything.")
    assert r.mode == TTSMode.DEV
    assert r.characters_spent == 0
    assert r.audio_bytes is None


def test_dev_mode_explicit_also_spends_no_quota():
    r = speak("Same guarantee when passed explicitly.", mode=TTSMode.DEV)
    assert r.characters_spent == 0
