from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from stewart_filmscreen.client import StewartFilmscreenClient
from stewart_filmscreen.const import DEFAULT_PORT

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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
