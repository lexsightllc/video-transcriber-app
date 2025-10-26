. "$PSScriptRoot/Utils.ps1"

Activate-Venv

if (-not (Test-Path "$ProjectRoot/sbom")) {
    New-Item -ItemType Directory -Path "$ProjectRoot/sbom" | Out-Null
}

cyclonedx-bom -r -f json -o "$ProjectRoot/sbom/cyclonedx.json"
