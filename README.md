# Stewart Filmscreen Home Assistant Integration

Home Assistant integration for Stewart Filmscreen CVM controllers.

This integration uses the `stewart-filmscreen` Python client and follows a coordinator-based, push-first architecture.

## Features

- Cover entities for motors A/B/C/D
- `recall_preset` service
- `store_preset` service
- Automatic reconnect and push updates

## Protocol Reference

- https://www.stewartfilmscreen.com/Files/files/Support%20Material/Controls/CVM.pdf

## Installation (HACS)

1. Add this repository as a custom integration in HACS.
2. Install the integration.
3. Restart Home Assistant.
4. Add `Stewart Filmscreen` from Settings > Devices & Services.

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
