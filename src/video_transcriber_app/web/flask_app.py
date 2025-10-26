#!/usr/bin/env python3
"""Flask-based Video Transcriber web application."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from ..transcriber import SUPPORTED_LANGUAGES, WHISPER_MODELS, transcribe_video

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_FOLDER = DATA_DIR / "uploads"
RESULTS_FOLDER = DATA_DIR / "results"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
app.secret_key = 'video_transcriber_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Global variables for progress tracking
transcription_progress: Dict[str, Dict[str, float]] = {}
transcription_results: Dict[str, Dict[str, str]] = {}


def allowed_file(filename: str) -> bool:
    """Check whether a filename has an allowed extension."""

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def progress_callback(job_id: str):
    """Create a progress callback function for a specific job."""

    def callback(step_description: str, percentage: float) -> None:
        transcription_progress[job_id] = {
            'step': step_description,
            'percentage': percentage,
            'timestamp': time.time()
        }

    return callback

def transcribe_worker(job_id: str, video_path: Path, model_name: str, language: str) -> None:
    """Worker function to handle transcription in background."""
    video_path_obj = Path(video_path)

    try:
        callback = progress_callback(job_id)

        # Start transcription
        srt_content = transcribe_video(
            video_path=str(video_path_obj),
            model_name=model_name,
            language=language if language != 'auto' else None,
            progress_callback=callback
        )

        # Save results
        result_file = RESULTS_FOLDER / f"{job_id}.srt"
        result_file.write_text(srt_content, encoding='utf-8')

        transcription_results[job_id] = {
            'status': 'completed',
            'srt_content': srt_content,
            'result_file': str(result_file),
            'timestamp': time.time()
        }
        
        # Update progress to 100%
        transcription_progress[job_id] = {
            'step': 'Transcrição concluída!',
            'percentage': 100,
            'timestamp': time.time()
        }
        
    except Exception as e:
        transcription_results[job_id] = {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }
        transcription_progress[job_id] = {
            'step': f'Erro: {str(e)}',
            'percentage': 0,
            'timestamp': time.time()
        }
    finally:
        # Clean up uploaded file
        if video_path_obj.exists():
            video_path_obj.unlink()

@app.route('/')
def index():
    return render_template('index.html', 
                         whisper_models=WHISPER_MODELS, 
                         languages=SUPPORTED_LANGUAGES)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
    
    file = request.files['video_file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo foi selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de arquivo não suportado'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        job_id = f"{int(time.time())}_{filename}"
        video_path = UPLOAD_FOLDER / job_id
        file.save(str(video_path))
        
        # Get transcription parameters
        model_name = request.form.get('model', 'base')
        language = request.form.get('language', 'pt')
        
        # Start transcription in background
        thread = threading.Thread(
            target=transcribe_worker,
            args=(job_id, video_path, model_name, language)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Upload realizado com sucesso. Transcrição iniciada.'
        })
        
    except Exception as exc:
        return jsonify({'error': f'Erro no upload: {str(exc)}'}), 500

@app.route('/progress/<job_id>')
def get_progress(job_id):
    progress = transcription_progress.get(job_id, {'step': 'Preparando...', 'percentage': 0})
    result = transcription_results.get(job_id, {'status': 'processing'})
    
    return jsonify({
        'progress': progress,
        'result': result
    })

@app.route('/download/<job_id>')
def download_result(job_id):
    if job_id in transcription_results:
        result = transcription_results[job_id]
        result_file = Path(result['result_file'])
        if result['status'] == 'completed' and result_file.exists():
            return send_file(
                result_file,
                as_attachment=True,
                download_name=f"{job_id}.srt",
                mimetype='application/x-subrip'
            )
    
    return jsonify({'error': 'Arquivo não encontrado'}), 404

if __name__ == '__main__':
    print("🎙️ Video Transcriber Flask App")
    print("✅ Starting server on http://localhost:5000")
    print("🔍 This is a working alternative to the Streamlit version")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
