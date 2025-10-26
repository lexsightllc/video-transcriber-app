# SPDX-License-Identifier: MPL-2.0

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

. "$PSScriptRoot/Utils.ps1"

Activate-Venv

$mode = if ($env:VIDEO_TRANSCRIBER_APP) { $env:VIDEO_TRANSCRIBER_APP } else { "streamlit" }
$port = if ($env:STREAMLIT_SERVER_PORT) { $env:STREAMLIT_SERVER_PORT } else { "8501" }

switch ($mode) {
    "flask" { python -m video_transcriber_app.web.flask_app }
    "simple" { python -m video_transcriber_app.web.simple_server }
    default { streamlit run src/video_transcriber_app/web/streamlit_app.py --server.port $port --server.address 0.0.0.0 }
}
