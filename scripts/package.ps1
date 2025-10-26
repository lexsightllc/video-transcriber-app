# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

python -m build
python -m twine check dist/*
