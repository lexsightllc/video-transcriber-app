. "$PSScriptRoot/Utils.ps1"

& "$PSScriptRoot/lint.ps1"
& "$PSScriptRoot/typecheck.ps1"
& "$PSScriptRoot/test.ps1"
& "$PSScriptRoot/coverage.ps1"
& "$PSScriptRoot/security-scan.ps1"
