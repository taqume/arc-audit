# ArcAudit

ArcAudit is a local-first security, compatibility, and conformance toolkit for Arc projects. It is being built as an open-source CLI, Python SDK, and local MCP server backed by one deterministic analysis core.

> ArcAudit is pre-alpha software. A clean report does not prove that a project is secure or production-ready.

## Development status

The current `0.1.0.dev0` foundation provides the shared report model, versioned Arc profile loading, project discovery, read-only network probes, and the first fixture-backed Slither rules.

## Local development

```shell
uv sync
uv run arcaudit --version
uv run pytest
```

Project compilation is an explicit trust boundary. Run semantic Solidity rules only after reviewing the target project:

```shell
uv run arcaudit scan ./path/to/project --allow-build
```

The evolving product and architecture decisions are documented under [`docs/`](docs/README.md).

## License

ArcAudit is licensed under [`AGPL-3.0-only`](LICENSES/AGPL-3.0-only.txt). See the third-party notices before redistribution.
