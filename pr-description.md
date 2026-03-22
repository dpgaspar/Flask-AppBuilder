<!--- Thank you for contributing to Flask-Appbuilder. -->
<!--- This repo uses a PR lint bot (https://github.com/apps/prlint), make sure to prefix your PR title with one of: -->
<!--- build|chore|ci|docs|feat|fix|perf|refactor|style|test|other -->

### Description

Replace the legacy linting toolchain (black, flake8, flake8-import-order) with **ruff** and switch CI from running individual lint commands to **prek** (a Rust-based pre-commit runner) executing hooks defined in `.pre-commit-config.yaml`.

**What changed:**
- **Ruff** now handles both linting (`ruff check`, replacing flake8 + flake8-import-order) and formatting (`ruff format`, replacing black). Mypy is kept as-is since ruff does not cover type checking.
- **prek** replaces the ad-hoc `pip install` + manual invocation approach in CI with a single `prek run --all-files` step.
- Added `.pre-commit-config.yaml` with ruff and mypy hooks.
- Added `[tool.ruff]` configuration in `pyproject.toml`, matching the previous flake8 settings (line-length 90, same excludes, google-style import ordering via isort rules).
- Removed `[flake8]` section from `setup.cfg`, removed `[testenv:flake8]` and `[testenv:black]` from `tox.ini`.
- Updated `requirements/dev.in`: dropped black, flake8, flake8-import-order; added ruff and prek.
- Auto-fixed ~62 import ordering issues and reformatted ~31 files to match ruff's formatter output.
- Added per-file-ignores for pre-existing E721 and F811 violations to keep the migration clean.

### ADDITIONAL INFORMATION
<!--- Check any relevant boxes with "x" -->
<!--- HINT: Include "Fixes #nnn" if you are fixing an existing issue -->
- [ ] Has associated issue:
- [ ] Is CRUD MVC related.
- [ ] Is Auth, RBAC security related.
- [ ] Changes the security db schema.
- [ ] Introduces new feature
- [ ] Removes existing feature
