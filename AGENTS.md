# AGENTS GUIDE

This document briefs autonomous agents operating in this repository. Follow it before making edits, running commands, or coordinating workflows.

## Repository Orientation
- Primary language: Python 3.8+ CLI around `super_image` upscalers.
- Core module: `resize.py`; tests live in `tests/test_resize.py`.
- Dependencies enumerated in `requirements.txt`; optional extras (torch) may be needed for runtime but are not pinned.
- Virtual environment at `.venv/`; never commit or edit inside it.
- No compiled assets or build outputs are tracked in git.
- License: Apache-2.0 (`LICENSE`) governs contributions and reuse.

## Environment Setup
- Use system Python 3.8+; prefer matching packaged version used in CI.
- Recommended bootstrap:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Install `torch` manually when super-resolution backends complain; choose build matching local hardware.
- Always activate the venv before running CLI commands or tests to avoid cross-environment contamination.
- Keep environment-specific files (`.env`, `venv/`) gitignored.

## Command Cheatsheet
- `python resize.py input.jpg` upscales a single image with default suffix.
- `python resize.py folder/ --output out/ --scale 3 --model edsr` covers directory workflows.
- `python resize.py --help` exhibits all switches and documentation.
- Avoid running CLI against large directories in parallel; models load once per invocation.

## Testing
- Framework: pytest 9.x (installed via requirements).
- Run full suite: `pytest`.
- Run a single test: `pytest tests/test_resize.py::test_directory_processing_calls_upscale`.
- Filter by keyword: `pytest -k "skip_single_file"` to target logical slices.
- Pytest auto-discovers tests in `tests/`; keep new tests in that tree.
- Tests currently stub out `super_image` to keep execution fast; preserve that pattern.
- Use `tmp_path`, `monkeypatch`, and `capsys` fixtures instead of manual temp folders or stdout capture.
- Clean caches with `rm -rf .pytest_cache` if collection misbehaves.

## Linting and Formatting
- No automated linters are configured. Before adding new tooling, coordinate with maintainers.
- Mirror existing style: `resize.py` uses tabs for indentation; do not rewrite the file to spaces unless agreed.
- Keep lines <= 100 chars when practical; multi-arg calls can wrap with hanging indentation.
- Strip trailing whitespace; ensure files end with a newline.
- Format docstrings and comments in plain prose; avoid Markdown inside code blocks.
- If you introduce `ruff` or `black` locally, audit diffs to avoid mass reformatting.

## Imports
- Group imports: stdlib, third-party, local; separate groups with a blank line.
- Order within a group alphabetically by module path.
- Avoid `from module import *`; explicitly spell out symbols.
- When mocking heavy deps (e.g., `super_image`), isolate fakes inside test helpers like `_load_module`.
- Keep import side effects minimal; CLI logic lives under `if __name__ == "__main__"`.

## Types and Interfaces
- Public functions should carry type hints for arguments and return values.
- Use `str | os.PathLike[str]` when accepting filesystem inputs; convert immediately with `Path`.
- Favor concrete return types over `Any`; use `None` for side-effect functions.
- Document error conditions in docstrings when raising exceptions.
- Avoid runtime type checks where structural typing suffices.

## Naming Conventions
- Modules, packages, and functions follow `snake_case`.
- Constants use `UPPER_CASE` and live near module tops.
- CLI flags adopt hyphenated names (`--upscale-suffix`) aligning with argparse defaults.
- Tests name fixtures with descriptive verbs (`fake_upscale`, `fail_upscale`).
- Temporary filesystem paths should reference intent (`out_dir`, `dir_path`) rather than letters.

## Error Handling
- Prefer `ValueError` for argument validation, `FileNotFoundError` for missing inputs, `SystemExit` via `sys.exit` for CLI aborts.
- Wrap filesystem creation in try/except and surface actionable messages, as shown when creating output directories.
- Print user-facing info via `print`; reserve exceptions for fatal errors.
- When propagating exceptions, include context (e.g., file path or model name) to help diagnose remote runs.
- For non-fatal directory iteration issues, log and continue rather than crashing the batch.

## CLI Behavior
- Resolve paths with `Path.expanduser()` and `resolve()` where possible.
- Accept directories and single files; keep suffix checks consistent with `DEFAULT_UPSCALE_SUFFIX`.
- Avoid re-loading models inside loops; load once and reuse reference.
- Skip already processed files gracefully, mirroring existing messages ("Skipping ...").
- When introducing new flags, update argparse help strings and maintain backwards compatibility.

## Testing Practices
- Keep tests deterministic; avoid downloading model weights or touching the network.
- Use PIL to synthesize minimal images instead of relying on fixtures in repo.
- Validate both success paths and skip conditions; inspect captured stdout where behavior is user-visible.
- When adding CLI flags, add tests under `tests/` proving argument parsing and branching logic.
- Mark slow or optional tests with `pytest.mark.slow` only after introducing marker configuration.

## Filesystem and IO
- Respect `SUPPORTED_EXTS`; extend carefully and update tests when adding new formats.
- When creating directories, allow `exist_ok=True` only where idempotent.
- Use `Path` operations; avoid manual string concatenation and `os.path` unless necessary.
- Ensure output files adopt same extension as input unless intentionally overridden.
- Close images promptly using context managers (`with Image.open(...) as img`).

## Dependency Guidance
- Dependencies live in `requirements.txt`; keep versions unconstrained unless stability demands pins.
- Heavy packages (torch) stay optional; document installation steps rather than embedding in requirements.
- Favor standard library modules before bringing in new third-party packages.
- When adding dependencies, verify they coexist with `super_image` and are license-compatible.
- Update README when altering runtime requirements.

## Git Hygiene
- Do not commit virtualenv contents, caches, or OS files (`.DS_Store` already ignored).
- Keep commits focused and descriptive; avoid bundling refactors with feature changes.
- Run tests before opening PRs; capture command outputs in PR descriptions rather than committing logs.
- Respect existing `.gitignore`; extend when introducing new tooling artifacts.
- Never rewrite history on shared branches unless maintainers approve.

## Documentation Expectations
- Update README when user workflows change.
- Inline comments only when logic is non-obvious (e.g., explaining model skipping).
- Prefer docstrings for public functions; keep them concise and imperative.
- When adding CLI options, document them in README and examples.
- Maintain this `AGENTS.md` as authoritative for automation guidelines.

## Tooling Notes
- No pre-commit hooks or task runners are configured; add them cautiously and document usage.
- Keep scripts portable; rely on `python -m` invocations instead of `pytest` binaries when scripting.
- For ad hoc linting, `python -m compileall resize.py` can catch syntax errors pre-commit.
- Consider `pip-tools` or `uv` only after stakeholder alignment.

## External Integrations
- The tool relies on Hugging Face model IDs (`eugenesiow/...`); do not hardcode tokens in code or config.
- Avoid embedding API keys or credentials; use env vars if integration becomes necessary.
- Network calls should be wrapped in error handling and accompanied by retries if added later.
- Keep sample assets out of the repo unless cleared for redistribution.

## Cursor and Copilot Rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` files exist as of 2026-01-19.
- If you add such rule files, mirror key guidance in this document to keep AI agents aligned.

## Troubleshooting
- `ModuleNotFoundError: super_image` -> install requirements or stub as tests do.
- `OSError: cannot identify image file` -> validate input extensions and attempt `Image.open` manually.
- GPU memory errors -> lower `--scale` or switch models (`mdsr` vs `edsr`).
- Permission errors when writing outputs -> ensure target directory exists and is writable.
- For path issues on Windows, normalize using raw strings or escape backslashes.

## Performance Tips
- Batch processing loops use Python iteration; avoid micro-optimizations unless profiling shows need.
- When extending, consider concurrency carefully; model objects may not be thread-safe.
- Cache expensive operations (model loads) but release GPU memory when done.
- Keep logging lightweight to avoid I/O bottlenecks on large directories.

## Final Notes
- Keep changes minimal and observable; run tests before exiting.
- Update this guide whenever workflows or conventions change.
- When uncertain, open an issue or request clarification rather than guessing.
- Agents should log their actions in PR descriptions for traceability.
