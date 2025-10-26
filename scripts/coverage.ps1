. "$PSScriptRoot/Utils.ps1"

Activate-Venv

pytest --cov=video_transcriber_app --cov-report=term-missing --cov-report=xml tests
