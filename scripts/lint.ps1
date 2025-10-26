. "$PSScriptRoot/Utils.ps1"

Activate-Venv

ruff check src tests
black --check src tests
isort --check-only src tests
