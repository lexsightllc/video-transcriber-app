# SPDX-License-Identifier: MPL-2.0

"""Core transcription services for the Video Transcriber application."""

from __future__ import annotations

import logging
import os
import ssl
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from moviepy.editor import VideoFileClip

import whisper

from .phi3_brain import Phi3Brain

# Fix SSL certificate verification issues
ssl._create_default_https_context = ssl._create_unverified_context

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants for Whisper models and languages
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large", "large-v2"]

SUPPORTED_LANGUAGES = ["en", "pt", "es", "fr", "de", "it", "ja", "ko", "zh"]


def transcribe_video_enhanced(
    video_path: str,
    model_name: str = "base",
    language: Optional[str] = "pt",
    enable_phi3: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    Enhanced video transcription with Phi-3 brain integration.
    
    Args:
        video_path (str): The path to the input video file.
        model_name (str): The Whisper model to use (e.g., "base", "small", "medium", "large").
        language (str): The language of the audio (e.g., "pt" for Portuguese).
        enable_phi3 (bool): Whether to enable Phi-3 brain analysis.
        progress_callback (callable, optional): A function to call with progress updates.
    
    Returns:
        Dict[str, Any]: Enhanced transcription results with analysis.
    """
    # First get the basic transcription
    basic_transcription = transcribe_video(video_path, model_name, language, progress_callback)
    
    result = {
        "transcription": basic_transcription,
        "video_path": video_path,
        "model_used": model_name,
        "language": language,
        "phi3_enabled": enable_phi3
    }
    
    if enable_phi3:
        try:
            if progress_callback:
                progress_callback("Initializing Phi-3 brain...", 70)
            
            brain = Phi3Brain()
            
            if progress_callback:
                progress_callback("Analyzing transcription quality...", 80)
            
            # Generate comprehensive analysis
            result["phi3_analysis"] = brain.generate_metadata(basic_transcription)
            
            if progress_callback:
                progress_callback("Analysis complete!", 100)
                
        except Exception as exc:  # pragma: no cover - defensive programming
            logger.error("Phi-3 analysis failed: %s", exc)
            result["phi3_analysis"] = {"error": str(exc)}
    
    return result

def transcribe_video(
    video_path: str,
    model_name: str = "base",
    language: Optional[str] = "pt",
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> str:
    """
    Transcribes the audio from a video file and returns the SRT content.

    Args:
        video_path (str): The path to the input video file.
        model_name (str): The Whisper model to use (e.g., "base", "small", "medium", "large").
        language (str): The language of the audio (e.g., "pt" for Portuguese).
        progress_callback (callable, optional): A function to call with progress updates.
                                                It should accept (current_step_str, percentage_float).

    Returns:
        str: The content of the SRT subtitle file.

    Raises:
        FileNotFoundError: If the video_path does not exist.
        ValueError: If the video has no audio track or transcription fails.
        Exception: For other unexpected errors during processing.
    """
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path_obj}")

    temp_audio_file = None
    try:
        # Load the Whisper model
        if progress_callback:
            progress_callback("Carregando modelo Whisper...", 5)
        logger.info("Carregando modelo Whisper: %s...", model_name)
        model = whisper.load_model(model_name)
        logger.info("Modelo Whisper carregado com sucesso.")
        if progress_callback:
            progress_callback("Modelo Whisper carregado.", 10)

        # Extract audio using moviepy
        logger.info("Extraindo áudio de: %s", video_path_obj)
        with VideoFileClip(str(video_path_obj)) as video:
            if video.audio is None:
                raise ValueError("O vídeo não contém uma faixa de áudio.")

            # Create a temporary file for the audio
            temp_audio_file = Path(tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name)
            
            if progress_callback:
                progress_callback("Exportando áudio...", 20)
            video.audio.write_audiofile(str(temp_audio_file), logger=None)
            logger.info("Áudio exportado para: %s", temp_audio_file)
            if progress_callback:
                progress_callback("Áudio exportado com sucesso.", 30)

        # Transcribe audio
        if progress_callback:
            progress_callback("Transcrevendo áudio (isso pode levar tempo)...", 40)
        logger.info("Iniciando transcrição de áudio em %s...", language)
        
        # Use the correct parameters for the current Whisper version
        if language and language.lower() != 'auto':
            result = model.transcribe(str(temp_audio_file), language=language)
        else:
            result = model.transcribe(str(temp_audio_file))
            
        logger.info("Transcrição concluída com sucesso.")
        if progress_callback:
            progress_callback("Transcrição concluída.", 90)

        # Format result to SRT
        srt_content = ""
        for i, segment in enumerate(result["segments"]):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            srt_content += f"{i + 1}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment['text'].strip()}\n\n"
        
        if progress_callback:
            progress_callback("SRT gerado com sucesso.", 100)
        logger.info("Conteúdo SRT gerado.")
        return srt_content

    except FileNotFoundError as e:
        logger.error("Erro: %s", e)
        raise
    except ValueError as exc:
        logger.error("Erro de validação: %s", exc)
        raise
    except Exception as exc:  # pragma: no cover - unexpected failure path
        logger.critical("Erro inesperado durante a transcrição: %s", exc, exc_info=True)
        raise RuntimeError(f"Erro inesperado: {exc}. Verifique os logs para mais detalhes.") from exc
    finally:
        # Clean up temporary audio file
        if temp_audio_file and temp_audio_file.exists():
            temp_audio_file.unlink()
            logger.info("Arquivo temporário de áudio removido: %s", temp_audio_file)


def format_timestamp(seconds: float) -> str:
    """Formats a time in seconds to SRT timestamp format (HH:MM:SS,ms)."""
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds * 1000):03}"


if __name__ == "__main__":
    # Example usage for CLI testing
    import argparse

    def print_cli_progress(step, percentage):
        print(f"Progresso: {step} ({percentage:.1f}%)")

    parser = argparse.ArgumentParser(description="Transcreve áudio de um arquivo de vídeo para SRT.")
    parser.add_argument("video_file", type=str, help="Caminho para o arquivo de vídeo.")
    parser.add_argument("--model", type=str, default="base", help="Nome do modelo Whisper (e.g., 'base', 'small', 'medium').")
    parser.add_argument("--lang", type=str, default="pt", help="Idioma do áudio (e.g., 'pt', 'en').")
    parser.add_argument("--output", type=str, help="Caminho para salvar o arquivo SRT de saída.")

    args = parser.parse_args()

    try:
        print(f"Iniciando transcrição para: {args.video_file}")
        srt_content = transcribe_video(args.video_file, args.model, args.lang, progress_callback=print_cli_progress)
        
        output_path = args.output
        if not output_path:
            # Generate default output path
            base_name = os.path.splitext(args.video_file)[0]
            output_path = f"{base_name}.srt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"Transcrição salva em: {output_path}")

    except Exception as e:
        print(f"Erro durante a transcrição: {e}")
        exit(1)
