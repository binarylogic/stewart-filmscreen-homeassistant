from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry
from stewart_filmscreen.client import StewartFilmscreenClient
from stewart_filmscreen.const import DEFAULT_PORT

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DOMAIN = "stewart_filmscreen"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Stewart Filmscreen",
        data={
            CONF_HOST: "192.168.1.50",
            CONF_PORT: DEFAULT_PORT,
            CONF_USERNAME: "installer",
            CONF_PASSWORD: "secret",
        },
        options={},
        unique_id="stewart_192.168.1.50",
    )


@pytest.fixture
def mock_stewart_client() -> MagicMock:
    """Return a mocked Stewart client."""
    client = MagicMock()
    client.host = "192.168.1.50"
    client.port = DEFAULT_PORT
    client.connected = True
    client.start = AsyncMock()
    client.wait_authenticated = AsyncMock()
    client.stop_client = AsyncMock()
    client.register_callback = MagicMock()
    client.deregister_callback = MagicMock()
    client.send_command = AsyncMock()
    client.recall_preset = AsyncMock()
    client.store_preset = AsyncMock()
    return client


@pytest.fixture
def mock_setup_entry(mock_stewart_client):
    """Patch the Stewart client used during config entry setup."""
    with patch(
        "custom_components.stewart_filmscreen.StewartFilmscreenClient",
        return_value=mock_stewart_client,
    ) as mock_class:
        yield mock_class


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _get_required_real_target() -> tuple[str, int, str, str]:
    if not _env_flag("STEWART_ITEST"):
        pytest.skip("real integration tests are disabled (set STEWART_ITEST=1)")

    host = os.getenv("STEWART_HOST")
    if not host:
        pytest.skip("STEWART_HOST is not set")

    username = os.getenv("STEWART_USERNAME")
    if not username:
        pytest.skip("STEWART_USERNAME is not set")

    password = os.getenv("STEWART_PASSWORD")
    if not password:
        pytest.skip("STEWART_PASSWORD is not set")

    port = int(os.getenv("STEWART_PORT", str(DEFAULT_PORT)))
    return host, port, username, password


async def _is_reachable(host: str, port: int, timeout: float) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host=host, port=port), timeout=timeout
        )
    except (TimeoutError, OSError):
        return False

    writer.close()
    await writer.wait_closed()
    return True


@pytest_asyncio.fixture
async def real_client() -> AsyncGenerator[StewartFilmscreenClient, None]:
    host, port, username, password = _get_required_real_target()

    if not await _is_reachable(host, port, timeout=1.0):
        pytest.skip(f"Stewart CVM target {host}:{port} is unreachable")

    client = StewartFilmscreenClient(
        host=host,
        port=port,
        username=username,
        password=password,
        reconnect_seconds=2.0,
        command_throttle_seconds=0.1,
    )

    await client.start()
    try:
        await client.wait_authenticated(timeout=10.0)
        yield client
    finally:
        await client.stop_client()
