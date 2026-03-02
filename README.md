# Stewart Filmscreen Home Assistant Integration

Home Assistant integration for Stewart Filmscreen CVM controllers.

This integration uses the `stewart-filmscreen` Python client and follows a coordinator-based, push-first architecture.

## Project Status

This repository is the canonical and maintained Stewart Filmscreen integration for Home Assistant.

This project is intentionally maintained as a high-quality custom integration instead of targeting Home Assistant Core. That allows faster iteration and tighter domain-specific behavior for high-end theater workflows.

Release notes and compatibility updates are tracked in this repository.

## Features

- Cover entities for motors A/B/C/D
- `recall_preset` service
- `store_preset` service
- Automatic reconnect and push updates

## Protocol Reference

- https://www.stewartfilmscreen.com/Files/files/Support%20Material/Controls/CVM.pdf

## Installation (HACS)

1. Open HACS in Home Assistant.
2. Go to `Integrations`.
3. Search for `Stewart Filmscreen`.
4. Open it and click `Download`.
5. Restart Home Assistant.
6. Add `Stewart Filmscreen` from Settings > Devices & Services.

If HACS has not synced the default index update yet, temporarily add it as a custom repository:

1. In HACS, open the top-right menu (three dots) and choose `Custom repositories`.
2. Add `https://github.com/binarylogic/stewart-filmscreen-homeassistant` as category `Integration`.
3. Refresh HACS and install as above.

## Real Device Integration Tests (Read-Only)

Use this when you want to validate against a real CVM that may or may not be online.

- Marker: `integration_real`
- Opt-in gate: `STEWART_ITEST=1`
- Target: `STEWART_HOST`, optional `STEWART_PORT`
- Credentials: `STEWART_USERNAME`, `STEWART_PASSWORD`
- If the device is offline/unreachable, tests are skipped.

Local setup:

```bash
cp .env.example .env
```

Run:

```bash
set -a && source .env && set +a && uv run pytest -v -m integration_real
```
