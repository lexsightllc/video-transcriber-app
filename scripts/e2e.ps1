# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

pytest tests/e2e
