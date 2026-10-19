# CLAUDE.md

## Project

find-a-job — an MCP server that fetches LinkedIn job offers through the Apify API, stores the
full data on the server and returns only short summaries to the model. See `README.md`; the
working spec is in `.internal/linkedin-jobs-mcp-spec.md` (local only, gitignored).

- Package sources: `src/find_a_job/` (src-layout)
- Entry point: `find_a_job.cli:main` (`src/find_a_job/cli.py`); also runs as `uv run python -m find_a_job`
- `cli.py` is a thin layer: it parses arguments, calls other modules and prints results.
  Functionality lives in separate modules in `src/find_a_job/`, not in `cli.py`.
- CLI commands are argparse subcommands (`find-a-job <command>`). Exit codes: 0 success,
  1 runtime error, 2 usage or config error.
- Errors: expected failures raise a subclass of `FindAJobError` (`src/find_a_job/errors.py`)
  with a user-facing message and an `exit_code`. Modules raise them; `cli.main` alone catches
  `FindAJobError` and prints `find-a-job: error: ...`. Wrap library errors (Apify client, HTTP,
  OS, JSON, SQLite) in a `FindAJobError` subclass at the module boundary; don't catch them in
  `cli.py`. Any other exception is a bug and should surface with its traceback.
- Logs and diagnostics go to stderr, never stdout: over the stdio transport, stdout carries
  MCP protocol messages only.

## Git conventions

- **Branch names** use Conventional Commits types as a prefix: `<type>/<short-description>`,
  e.g. `feat/show-commands`, `fix/ssh-reconnect`, `docs/readme`, `chore/ci-setup`.
  Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `perf`, `style`.
- **Commit messages** do not follow Conventional Commits — write plain, descriptive messages
  (e.g. "Add README with setup instructions").
- **Atomic commits**: each commit covers one logical change (a single feature, fix, or
  refactor). Split unrelated changes into separate commits rather than bundling them.
- **No AI attribution**: never add `Co-Authored-By: Claude` (or any other AI co-author) trailers
  to commits, and no "Generated with Claude Code" footer in PR descriptions.
- **Merging PRs** uses a merge commit (no squash). The subject is the PR title followed by the PR
  number, with an empty body: `gh pr merge <N> --merge --subject "<PR title> (#<N>)" --body ""`.

## Pull requests

- **Title**: brief, a few words in the imperative that name the purpose of the PR, not a list of
  what changed; the details go in the description. No type prefix.
  E.g. "Bootstrap the project", "Add show command tool", "Fix SSH reconnect".
- **Description** uses this template, with all four sections in this order:

  ```markdown
  ## 📌 What
  One or two sentences: what this PR does and where it fits in the project.

  ## 🤔 Why
  The need behind the change, as a short lead-in followed by a list:
  - the problem it solves or what it enables
  - ...

  ## 🛠️ Changes
  - Added/Changed/Removed `path/or/name` – what it is or does
  - ...

  ## 🧪 How to test
  1. A step the reviewer runs, e.g. `uv sync`
  2. The command that shows the change working, and what to expect, e.g. `uv run <command>`
  ```

- **Changes** has one bullet per file or component, starting with Added / Changed / Removed,
  then an en dash and a short description. Group closely related files in one bullet
  (e.g. `uv.lock` and `.python-version`).
- **How to test** lists concrete steps a reviewer can run, in order, with the expected result.
- Keep it short and scannable: no long paragraphs, concrete names in backticks.
- **Before opening a PR**, review the changed code and suggest test cases for it (what to test,
  with which inputs, and the expected outcome). Do not write any tests without explicit approval
  or a direct instruction.

## Python tooling: uv only

Always use `uv`. Never call `pip`, `pip install`, bare `python`, or activate `.venv` by hand.

| Task | Command |
|---|---|
| Run the CLI | `uv run find-a-job <command>` (`--help` lists them) |
| Run as module | `uv run python -m find_a_job` |
| Run any script/command in the env | `uv run <cmd>` |
| Add dependency | `uv add <pkg>` |
| Add dev dependency | `uv add --dev <pkg>` |
| Remove dependency | `uv remove <pkg>` |
| Install / sync env from lockfile | `uv sync` |
| One-off tool (not a dependency) | `uvx <tool>` |
| Lint (with autofix) | `uv run ruff check --fix` |
| Format | `uv run ruff format` |
| Type check | `uv run ty check` |

Never edit dependency lists in `pyproject.toml` or `uv.lock` by hand — always go through
`uv add` / `uv remove`.

After editing Python code, run all three before committing:

```sh
uv run ruff check --fix && uv run ruff format && uv run ty check
```

Git hooks (pre-commit) run ruff check and ruff format on commit and ty check on push; enable with
`uv run pre-commit install`. A Claude Code hook (`.claude/hooks/ruff.sh`) also runs ruff format
and ruff check after every Python edit and reports any remaining errors back to Claude.

## Typing and docstrings

- Every function in `src/` must have full annotations: all arguments and the return type (`-> None` included). One exception: `__init__` may omit `-> None` when at least one argument is annotated (`mypy-init-return`). Ruff's `ANN` rules enforce this.
- Don't use `Any` (`ANN401`) — use a concrete type, a `Protocol`, or `object`.
- Use modern syntax: `list[str]`, `X | None`, not `List` / `Optional`.
- ty warnings fail the check (`error-on-warning`). Don't silence a diagnostic with `# ty: ignore` without a comment explaining why.
- Every module, class and public function in `src/` has a docstring: what it does, plus what it returns or raises when that isn't obvious. Ruff's `D1` rules enforce this; `__init__` is covered by the class docstring (`D107` ignored).

## Secrets

Credentials and keys go in `.env`, which is gitignored. Never commit `.env` or hardcode secrets.
`.env.example` lists every setting with placeholder values; keep it in sync when adding one.
Nothing loads `.env` automatically — the code must load it explicitly. Never put the Apify token
in URLs, logs, saved run files or MCP tool responses.
