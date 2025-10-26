"""Integration-style tests for CLI presentation helpers."""

from video_transcriber_app.cli_app import display_analysis_results


def test_display_analysis_results_handles_minimal_payload(capsys) -> None:
    """Ensure the CLI renderer can handle partial Phi-3 data."""

    payload = {
        "transcription": "Hello world",
        "phi3_analysis": {
            "summary": "Summary text",
            "key_topics": ["testing"],
            "quality_assessment": {"quality_score": 7, "confidence_level": "medium"},
            "sentiment_analysis": {"sentiment": "positive", "tone": "friendly"},
            "suggested_questions": ["What was said?"],
            "word_count": 2,
            "estimated_duration_minutes": 0.1,
        },
    }

    display_analysis_results(payload)

    captured = capsys.readouterr()
    assert "PHI-3 BRAIN ANALYSIS" in captured.out
    assert "Summary text" in captured.out
