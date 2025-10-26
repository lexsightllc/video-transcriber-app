# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

mypy src tests
