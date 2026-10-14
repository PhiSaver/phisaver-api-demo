# AGENTS.md

## Git
- Never write to git: no `git add`, `rm`, `mv`, `commit`, `stash`, `checkout`, `reset`, `push`, or anything else that changes the index, history, or remote. Read-only commands (`status`, `diff`, `log`) are fine.
- Use plain `mv`/`rm` for file changes; the user stages and commits.

## Environment
- Credentials live in `phisaver-api.env` (gitignored), loaded by `.envrc` (direnv). Create it from `phisaver-api-example.env`. Never commit it or echo its contents.
- CI supplies `PS_API_USERNAME` / `PS_API_PASSWORD` from GitHub secrets.

## Workflow
- `just` recipes are the entry points (`just --list`). Dependencies go in `.venv` via `just install`.
- `update-schema` uses HTTPie only, not phisaver-client.
