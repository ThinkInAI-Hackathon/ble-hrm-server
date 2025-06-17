# Root AGENT instructions

This repository uses Python and expects all development tasks to use `uv` for environment and package management.

## Development workflow

1. Use `uv` to create a virtual environment and sync dependencies:
   ```bash
   uv venv
   uv sync
   ```
2. When adding or updating dependencies, edit `pyproject.toml` and run `uv pip install <package>` followed by `uv pip freeze > uv.lock`.
3. Run tests with `uv`:
   ```bash
   uv run pytest
   ```
   Run coverage with:
   ```bash
   uv run coverage run -m pytest
   uv run coverage xml
   ```
4. Follow PEP8 guidelines. Format code with `black` and lint with `ruff` if available.
5. Provide docstrings for all public functions and classes.
6. Commit messages should be concise but descriptive.
7. After making changes, ensure all tests pass before committing.

