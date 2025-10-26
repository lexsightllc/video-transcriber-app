# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

bandit -r src -ll
safety check --full-report
