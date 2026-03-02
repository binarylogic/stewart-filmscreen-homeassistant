from __future__ import annotations

import asyncio

import pytest
from stewart_filmscreen.client import StewartFilmscreenClient


@pytest.mark.integration_real
@pytest.mark.asyncio
async def test_real_device_auth_smoke(real_client: StewartFilmscreenClient) -> None:
    assert real_client.connected is True


@pytest.mark.integration_real
@pytest.mark.asyncio
async def test_real_device_position_query_smoke(
    real_client: StewartFilmscreenClient,
) -> None:
    # Read-only command only. Avoid mutating movement/preset operations here.
    await real_client.query_position("1.1.1.MOTOR")
    await asyncio.sleep(0.5)
