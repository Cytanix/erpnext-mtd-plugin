# Contributing to ERPNext MTD

Thanks for your interest in contributing to ERPNext MTD.

ERPNext MTD is an open-source Making Tax Digital integration for ERPNext,
developed by Cytanix Ltd.

## Development Status

The project is currently pre-1.0 and under active development.

Breaking changes may occur between pre-release versions while the architecture,
configuration, and data model are still being stabilised.

## Development Requirements

- Frappe Framework v16
- ERPNext v16
- Python 3.14 or later
- Bench
- uv

## Development Setup

Install the app into a development Bench:

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/Cytanix/erpnext-mtd-plugin.git
bench --site your-site install-app erpnext_mtd
```

Install development dependencies:

```bash
cd apps/erpnext_mtd
uv sync --group dev
```

## Tests

Standalone tests can be run with:

```bash
uv run pytest
```

Tests that depend on Frappe should be run using the Bench environment, for
example:

```bash
cd /path/to/frappe-bench
./env/bin/pytest apps/erpnext_mtd/tests/
```

## Formatting and Linting

The project uses Ruff for Python formatting and linting.

Run:

```bash
uv run ruff check .
uv run ruff format --check .
```

To automatically format Python code:

```bash
uv run ruff format .
```

## Commit Messages

ERPNext MTD uses Conventional Commit-style messages.

Examples:

```text
feat: add VAT obligation retrieval
fix: reject invalid HMRC OAuth state
test: add fraud prevention proxy tests
docs: document sandbox configuration
refactor: separate VAT calculation from HMRC payload
```

Commit scopes are not currently required.

## Pull Requests

Before opening a pull request:

- Ensure relevant tests pass.
- Add or update tests for behavioural changes.
- Keep changes focused where practical.
- Avoid unrelated formatting or refactoring.
- Document new configuration or user-facing behaviour.

For substantial architectural changes, please open an issue first so the design
can be discussed before implementation begins.

## Security-Sensitive Changes

Changes affecting authentication, OAuth, HMRC credentials, fraud prevention
headers, permissions, or tax submission behaviour should include appropriate
tests and should avoid weakening validation or trust boundaries.

Security vulnerabilities should not be reported through public issues. See
`SECURITY.md`.

## Licence

By contributing, you agree that your contributions will be licensed under the
GNU General Public License v3.0.