param(
    [switch]$DryRun
)

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

if ($DryRun) {
    semantic-release version --noop
} else {
    semantic-release version
    semantic-release publish
}
