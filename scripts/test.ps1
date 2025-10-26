. "$PSScriptRoot/Utils.ps1"

Activate-Venv

pytest tests/unit tests/integration
