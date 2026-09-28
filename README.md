# ERPNext MTD

Open-source Making Tax Digital integration for ERPNext with direct HMRC API support.

> [!WARNING]
> ERPNext MTD is currently under active development and has not yet reached its
> first beta release. Do not use it to submit production VAT returns.

## About

ERPNext MTD aims to provide a native, open-source integration between ERPNext
and HMRC's Making Tax Digital APIs without requiring a third-party MTD service.

The project is developed by Cytanix Ltd and is intended to support the complete
VAT return workflow from ERPNext, including:

- HMRC OAuth authorisation
- HMRC fraud prevention headers
- VAT obligation retrieval
- VAT return calculation from ERPNext accounting data
- VAT return submission
- VAT return and submission history

## Requirements

- Frappe Framework v16
- ERPNext v16
- Python 3.14 or later

## Installation

ERPNext MTD has not yet reached a public release. For development and testing,
it can be installed using Bench:

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/Cytanix/erpnext-mtd-plugin.git
bench --site your-site install-app erpnext_mtd
bench --site your-site migrate
```

## Development

Install the development dependencies:

```bash
cd apps/erpnext_mtd
uv sync --group dev
```

Run the standalone tests with:

```bash
uv run pytest
```

Tests that require the Frappe environment should be run using the Bench
environment.

## Release Status

The current codebase is pre-release.

The first planned public beta will provide the minimum complete workflow needed
to prepare and submit an HMRC VAT return from ERPNext.

Pre-1.0 releases may introduce breaking changes to configuration, APIs, and
stored data.

## Contributing

Contributions, testing, and security reviews are welcome while the project is
under development.

Please open an issue before beginning substantial changes so implementation
details can be discussed first.

## License

ERPNext MTD is licensed under the GNU General Public License v3.0.

See `license.txt` for the full licence text.
