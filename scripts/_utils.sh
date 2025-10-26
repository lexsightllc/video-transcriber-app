#!/usr/bin/env bash
# SPDX-License-Identifier: MPL-2.0

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

export ROOT_DIR VENV_DIR PYTHON_BIN

ensure_python() {
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python interpreter '$PYTHON_BIN' not found." >&2
    exit 1
  fi
}

ensure_venv() {
  ensure_python
  if [[ ! -d "$VENV_DIR" ]]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi
}

activate_venv() {
  ensure_venv
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  cd "$ROOT_DIR"
}

run_in_venv() {
  activate_venv
  "$@"
}

run_pre_commit() {
  if [[ -f "$ROOT_DIR/.pre-commit-config.yaml" ]]; then
    run_in_venv pre-commit install >/dev/null
    run_in_venv pre-commit install --hook-type commit-msg >/dev/null
  fi
}

parse_common_flags() {
  for arg in "$@"; do
    case "$arg" in
      --fix)
        export APPLY_FIXES=1
        ;;
      --non-interactive)
        export NON_INTERACTIVE=1
        ;;
    esac
  done
}
