<!-- SPDX-License-Identifier: MPL-2.0 -->

# Contributing

Thanks for your interest in improving the Video Transcriber application!

## Getting Started
1. Clone the repository and create a new branch.
2. Run `scripts/bootstrap` to set up your environment.
3. Use `scripts/check` to run the full quality gate before submitting changes.

## Coding Guidelines
- Follow the formatting enforced by `ruff`, `black`, and `isort`.
- Keep functions small and focused. Prefer dependency injection for testability.
- Document new functionality with docstrings and updates to the `docs/` directory.

## Commit Messages
- Use [Conventional Commits](https://www.conventionalcommits.org/) to describe changes.
- Include tests for bug fixes and new features.

## Pull Requests
- Ensure CI passes (`make check`).
- Update documentation, changelog, and project metadata when introducing significant changes.
- Request review from the CODEOWNERS listed in `.github/CODEOWNERS`.

## License for Contributions
- By submitting a contribution, you agree that it will be licensed under the [Mozilla Public License 2.0](LICENSE), matching the outbound license for this project.
- Contributions must not include code that is incompatible with MPL-2.0. Ensure third-party additions retain their original license information in NOTICE or vendor directories as applicable.
