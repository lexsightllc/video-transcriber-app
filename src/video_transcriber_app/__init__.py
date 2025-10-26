# SPDX-License-Identifier: MPL-2.0

"""Video Transcriber application package."""

from __future__ import annotations

from importlib import metadata

from .transcriber import SUPPORTED_LANGUAGES, WHISPER_MODELS, transcribe_video, transcribe_video_enhanced

try:
    __version__ = metadata.version("video-transcriber-app")
except metadata.PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.0.0"

__all__ = [
    "SUPPORTED_LANGUAGES",
    "WHISPER_MODELS",
    "transcribe_video",
    "transcribe_video_enhanced",
]
