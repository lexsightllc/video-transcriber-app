# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/Utils.ps1"

if (Test-Path "$ProjectRoot/alembic.ini") {
    Activate-Venv
    alembic upgrade head
} else {
    Write-Warning "No migrations defined; skipping."
}
