<!-- SPDX-License-Identifier: MPL-2.0 -->

# Video Transcriber

Video Transcriber is a Python-based toolkit for converting video content into high quality SRT transcripts using OpenAI Whisper with optional Phi-3 analysis. The project ships with a Streamlit experience, a Flask backend, and a CLI workflow so the same transcription core can be reused across multiple form factors.

## Table of Contents
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Developer Tasks](#developer-tasks)
- [Quality Gates](#quality-gates)
- [Applications](#applications)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Project Structure
```
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Dockerfile
├── Makefile
├── README.md
├── docker-compose.yml
├── docs/
├── scripts/
├── src/
│   └── video_transcriber_app/
│       ├── __init__.py
│       ├── cli_app.py
│       ├── phi3_brain.py
│       ├── transcriber.py
│       └── web/
│           ├── basic_streamlit_app.py
│           ├── flask_app.py
│           ├── simple_server.py
│           ├── streamlit_app.py
│           └── templates/
├── tests/
│   ├── e2e/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
└── data/
    ├── results/
    ├── samples/
    └── uploads/
```

## Getting Started
1. **Clone** the repository and `cd` into it.
2. Copy `.env.example` to `.env` and adjust values as needed.
3. Run the bootstrap routine:
   ```bash
   scripts/bootstrap
   ```
4. Activate the virtual environment (`.venv/bin/activate` on Unix-like systems) when running commands manually.

The bootstrap workflow installs runtime and development dependencies, configures pre-commit hooks, and prepares local directories for generated assets.

## Developer Tasks
All project automation is exposed via the scripts in `scripts/`. Each script accepts `--help` and is mirrored as a `make` target for convenience.

| Task | Script | Description |
| ---- | ------ | ----------- |
| Environment bootstrap | `scripts/bootstrap` | Create/upgrade the Python virtualenv, install dependencies, and register pre-commit hooks. |
| Developer server | `scripts/dev` | Launch the Streamlit experience with hot reloading. |
| Lint | `scripts/lint` | Run Ruff (lint) and ESLint stubs to enforce style. |
| Format | `scripts/fmt` | Apply Black, Ruff format, and isort fixes. |
| Type check | `scripts/typecheck` | Execute mypy in strict mode. |
| Unit & integration tests | `scripts/test` | Run pytest suites with coverage disabled. |
| End-to-end tests | `scripts/e2e` | Placeholder hook for future browser-based scenarios. |
| Coverage | `scripts/coverage` | Run pytest with coverage enforcement. |
| Build | `scripts/build` | Generate Python distributions with `python -m build`. |
| Package | `scripts/package` | Create distributable artifacts (wheel + sdist). |
| Release | `scripts/release` | Invoke semantic-release for versioning and changelog updates. |
| Dependency updates | `scripts/update-deps` | Refresh locked dependencies using `pip-compile`. |
| Security scanning | `scripts/security-scan` | Execute Bandit and Safety audits. |
| SBOM | `scripts/sbom` | Produce a CycloneDX SBOM via Syft (when available). |
| Documentation | `scripts/gen-docs` | Build MkDocs-powered documentation. |
| Database migrations | `scripts/migrate` | Placeholder hook for data/schema migrations. |
| Clean | `scripts/clean` | Remove build artifacts and temporary files. |
| All checks | `scripts/check` | Run lint, type check, tests, coverage, and security scans. |

Invoke the equivalent `make` target (e.g., `make lint`) to run the same automation.

## Quality Gates
- **Linting**: `ruff` enforces code style and static checks. `black` + `isort` maintain formatting order.
- **Type Checking**: `mypy` runs in strict mode and relies on `pyproject.toml` configuration.
- **Testing**: Pytest covers unit and integration suites. Coverage thresholds are defined in `pyproject.toml`.
- **Security**: Bandit and Safety provide static and dependency analysis.
- **Commit Hygiene**: Pre-commit hooks format code, run lint checks, and enforce Conventional Commit messages via Commitizen.

## Applications
The repository ships multiple entry points built on a shared transcription core:
- `src/video_transcriber_app/web/streamlit_app.py` – feature-rich Streamlit interface with Phi-3 analysis.
- `src/video_transcriber_app/web/basic_streamlit_app.py` – lightweight Streamlit fallback UI.
- `src/video_transcriber_app/web/flask_app.py` – Flask API and templated UI for background processing.
- `src/video_transcriber_app/cli_app.py` – command-line automation with optional Phi-3 enrichment.

Use `scripts/dev` to launch Streamlit, or run `python -m video_transcriber_app.web.flask_app` for the Flask server.

## Configuration
Key configuration surfaces:
- `.env` – runtime flags such as `WHISPER_MODEL` or `FLASK_SECRET_KEY`.
- `project.yaml` – structured metadata consumed by tooling and reporting.
- `pyproject.toml` – dependency definitions, tool configuration, and packaging metadata.
- `docker-compose.yml` / `Dockerfile` – containerised development entry points.

Generated assets are stored under `data/` and ignored by version control. Uploads and results directories are created automatically during bootstrap.

## Documentation
Architectural decision records live under `docs/adr/`. Additional documentation can be authored with MkDocs and generated via `scripts/gen-docs`.

## Contributing
Please review [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md) before opening pull requests. Run `scripts/check` and ensure all automation passes prior to submission. Conventional Commit messages are required to satisfy semantic-release.

## License
Video Transcriber is distributed under the [Mozilla Public License 2.0](LICENSE). The MPL requires that any modifications to MPL-covered files remain available under the same license, but it permits you to combine those files within larger proprietary solutions without obligating you to open your entire codebase.

## Credits
Copyright © 2025 Augusto "Guto" Ochoa Ughini. See [NOTICE](NOTICE) for attribution details for third-party dependencies and ensure that NOTICE accompanies any distributions that bundle this project.
