$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Global:ProjectRoot = Resolve-Path (Join-Path $ScriptRoot "..").Path
$Global:VenvDir = if ($env:VENV_DIR) { $env:VENV_DIR } else { Join-Path $ProjectRoot ".venv" }
$Global:PythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }

function Ensure-Venv {
    if (-not (Test-Path $Global:VenvDir)) {
        & $Global:PythonBin -m venv $Global:VenvDir
    }
}

function Activate-Venv {
    Ensure-Venv
    $activateScript = Join-Path $Global:VenvDir "Scripts/Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        throw "Unable to locate PowerShell activation script at $activateScript"
    }
    . $activateScript
    Set-Location $Global:ProjectRoot
}
