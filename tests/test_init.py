"""Test Stewart Filmscreen integration setup lifecycle."""

from __future__ import annotations

from unittest.mock import AsyncMock

from stewart_filmscreen.const import DEFAULT_PORT

from custom_components.stewart_filmscreen.const import (
    DOMAIN,
    SERVICE_RECALL_PRESET,
    SERVICE_STORE_PRESET,
)


async def test_setup_and_unload_entry(
    hass, mock_config_entry, mock_setup_entry, mock_stewart_client
):
    """Test startup registers services and unload removes them."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_setup_entry.assert_called_once_with(
        host="192.168.1.50",
        port=DEFAULT_PORT,
        username="installer",
        password="secret",
    )
    mock_stewart_client.register_callback.assert_called_once()
    mock_stewart_client.register_connection_callback.assert_called_once()
    mock_stewart_client.start.assert_called_once()
    mock_stewart_client.wait_authenticated.assert_called_once()
    assert hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_stewart_client.deregister_callback.assert_called_once()
    mock_stewart_client.deregister_connection_callback.assert_called_once()
    mock_stewart_client.stop_client.assert_called_once()
    assert DOMAIN not in hass.data
    assert not hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert not hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)


async def test_reload_entry_re_registers_services(
    hass, mock_config_entry, mock_setup_entry
):
    """Test reload path restores both domain services."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    hass.services.async_remove(DOMAIN, SERVICE_STORE_PRESET)
    assert hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert not hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)

    await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)


async def test_setup_failure_stops_client(hass, mock_config_entry, mock_setup_entry):
    """Test offline startup keeps the entry loaded and services registered."""
    mock_stewart_client = mock_setup_entry.return_value
    mock_stewart_client.wait_authenticated = AsyncMock(side_effect=TimeoutError)
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_stewart_client.start.assert_called_once()
    mock_stewart_client.stop_client.assert_not_called()
    assert hass.services.has_service(DOMAIN, SERVICE_RECALL_PRESET)
    assert hass.services.has_service(DOMAIN, SERVICE_STORE_PRESET)

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()


async def test_connection_callbacks_refresh_entity_availability(
    hass, mock_config_entry, mock_setup_entry
):
    """Test pure connection state changes still refresh entity availability."""
    mock_stewart_client = mock_setup_entry.return_value
    mock_stewart_client.connected = False
    mock_stewart_client.wait_authenticated = AsyncMock(side_effect=TimeoutError)
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("cover.screen_motor_1")
    assert state
    assert state.state == "unavailable"

    callback = mock_stewart_client.register_connection_callback.call_args.args[0]
    mock_stewart_client.connected = True
    await callback("connected")
    await hass.async_block_till_done()

    state = hass.states.get("cover.screen_motor_1")
    assert state
    assert state.state != "unavailable"

    mock_stewart_client.connected = False
    await callback("disconnected")
    await hass.async_block_till_done()

    state = hass.states.get("cover.screen_motor_1")
    assert state
    assert state.state == "unavailable"
