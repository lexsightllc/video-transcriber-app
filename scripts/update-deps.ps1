# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

pip-compile pyproject.toml --extra dev --output-file requirements.lock
pip-compile pyproject.toml --output-file requirements-runtime.lock
