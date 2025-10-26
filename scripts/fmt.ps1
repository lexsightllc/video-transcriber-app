. "$PSScriptRoot/Utils.ps1"

Activate-Venv

ruff check --select I --fix src tests
ruff format src tests
black src tests
isort src tests
