"""
Proves the reusability claim (PLAN.md section 9): the same verification
gate used by HesitateAgent (voice) works unmodified in a plain text
agent, with zero clinic-specific code added here. Mocks the LLM call so
this test doesn't spend Groq API tokens on every run.
"""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.text_chat_agent import ask


def test_hallucinated_reply_is_corrected_through_the_same_gate():
    with patch("examples.text_chat_agent.generate_reply") as mock_gen:
        mock_gen.return_value = {"text": "You'll need to fast for twelve hours.", "latency_ms": 0, "reasoning_tokens": 0, "completion_tokens": 0}
        result = ask("How long do I need to fast?")
    assert result.startswith("[CORRECTED]")
    assert "8" in result
    assert "twelve" not in result


def test_correct_reply_passes_through_unmodified():
    with patch("examples.text_chat_agent.generate_reply") as mock_gen:
        mock_gen.return_value = {"text": "Fast for 8 hours before your appointment.", "latency_ms": 0, "reasoning_tokens": 0, "completion_tokens": 0}
        result = ask("How long do I need to fast?")
    assert result == "Fast for 8 hours before your appointment."
    assert not result.startswith("[")
