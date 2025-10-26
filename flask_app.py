#!/usr/bin/env python3
"""
Flask-based Video Transcriber Web Application
A working alternative to the Streamlit version that had server issues.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from transcriber import transcribe_video, WHISPER_MODELS, SUPPORTED_LANGUAGES
import threading
import time

app = Flask(__name__)
app.secret_key = 'video_transcriber_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Global variables for progress tracking
transcription_progress = {}
transcription_results = {}

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def progress_callback(job_id):
    """Create a progress callback function for a specific job"""
    def callback(step_description, percentage):
        transcription_progress[job_id] = {
            'step': step_description,
            'percentage': percentage,
            'timestamp': time.time()
        }
    return callback

def transcribe_worker(job_id, video_path, model_name, language):
    """Worker function to handle transcription in background"""
    try:
        callback = progress_callback(job_id)
        
        # Start transcription
        srt_content = transcribe_video(
            video_path=video_path,
            model_name=model_name,
            language=language if language != 'auto' else None,
            progress_callback=callback
        )
        
        # Save results
        result_file = os.path.join(RESULTS_FOLDER, f"{job_id}.srt")
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        transcription_results[job_id] = {
            'status': 'completed',
            'srt_content': srt_content,
            'result_file': result_file,
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
        if os.path.exists(video_path):
            os.remove(video_path)

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
        video_path = os.path.join(UPLOAD_FOLDER, job_id)
        file.save(video_path)
        
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
        
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

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
        if result['status'] == 'completed' and os.path.exists(result['result_file']):
            return send_file(
                result['result_file'],
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
