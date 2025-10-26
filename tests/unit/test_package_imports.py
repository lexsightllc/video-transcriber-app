# SPDX-License-Identifier: MPL-2.0

"""Unit tests ensuring the core package exports are available."""

from video_transcriber_app import (
    SUPPORTED_LANGUAGES,
    WHISPER_MODELS,
    transcribe_video,
    transcribe_video_enhanced,
)


def test_supported_languages_contains_portuguese() -> None:
    """Basic sanity check on supported language configuration."""

    assert "pt" in SUPPORTED_LANGUAGES


def test_whisper_models_contains_base() -> None:
    """Ensure that the default Whisper model is exposed."""

    assert "base" in WHISPER_MODELS


def test_transcription_functions_are_callable() -> None:
    """Verify that the core API functions are importable."""

    assert callable(transcribe_video)
    assert callable(transcribe_video_enhanced)
