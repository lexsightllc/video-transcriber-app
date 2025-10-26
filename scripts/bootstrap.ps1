# SPDX-License-Identifier: MPL-2.0

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

pip install --upgrade pip
pip install -e .[dev]

if (Test-Path "$ProjectRoot/.pre-commit-config.yaml") {
    pre-commit install | Out-Null
    pre-commit install --hook-type commit-msg | Out-Null
}

git config commit.template "$ProjectRoot/.gitmessage"

Write-Host "✅ Environment ready at $VenvDir"
