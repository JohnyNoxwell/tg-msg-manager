# Package Identity And Version Policy

This document records the current package identity surfaces and version source. It does not rename the project, change runtime behavior, or define a release plan.

## Current Identity

- Distribution/package project name: `tg-msg-manager`
- Import package/module root: `tg_msg_manager`
- Console script: `tg-msg-manager`
- Console script mapping: `tg-msg-manager = tg_msg_manager.cli:main`
- Primary Python entrypoint: `python3 -m tg_msg_manager.cli`
- README display name: `TG_MSG_MNGR`
- Current package version: `0.1.0`
- Current package description source: `pyproject.toml` `[project].description`

These names are intentionally different where Python packaging conventions require it: the distribution and console script use hyphens, while the import package uses underscores.

## Version Source

`pyproject.toml` `[project].version` is the single packaging version source.

Current code does not expose `tg_msg_manager.__version__`. Do not add a runtime version API unless an active stage explicitly scopes the import contract, tests, and docs update.

## License

The project uses the MIT License. Package license metadata uses the root
`LICENSE` file as its source.

## Public Entrypoints

The supported public command entrypoints are:

- `tg-msg-manager`
- `python3 -m tg_msg_manager.cli`

The root module `tg_msg_manager` re-exports selected runtime/config/i18n helpers for existing imports. It is not the version source.

## Change Policy

Do not rename these without explicit active stage scope:

- `tg-msg-manager`
- `tg_msg_manager`
- `tg-msg-manager = tg_msg_manager.cli:main`

Do not change command names, flags, parser defaults, aliases, output formats, packaging dependencies, or release metadata as part of identity documentation cleanup.

Version bumps require a separate release/version stage. Publishing, tagging, and building release artifacts are outside this policy document.
