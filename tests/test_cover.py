"""Test Stewart Filmscreen cover state mapping."""

from __future__ import annotations

from homeassistant.components.cover import CoverEntityFeature
from stewart_filmscreen.const import (
    COMMAND_DOWN,
    COMMAND_UP,
    MOTOR_A,
    STATUS_EXTENDING,
    STATUS_RETRACTING,
)
from stewart_filmscreen.models import ProtocolMessage


async def test_cover_reports_non_inverted_position_and_motion(
    hass, mock_config_entry, mock_setup_entry, mock_stewart_client
) -> None:
    """Test default motor mapping matches HA open/close semantics."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    callback = mock_stewart_client.register_callback.call_args.args[0]
    await callback(
        ProtocolMessage(
            kind="event",
            motor=MOTOR_A,
            name="POSITION",
            value="25",
            raw="!1.1.1.MOTOR.POSITION=25;",
        )
    )
    await callback(
        ProtocolMessage(
            kind="event",
            motor=MOTOR_A,
            name="STATUS",
            value=STATUS_RETRACTING,
            raw="!1.1.1.MOTOR.STATUS=RETRACTING;",
        )
    )
    await hass.async_block_till_done()

    state = hass.states.get("cover.screen_motor_1")
    assert state
    assert state.attributes["current_position"] == 75
    assert state.state == "opening"
    assert state.attributes["supported_features"] == int(
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )


async def test_cover_reports_inverted_position_and_motion(
    hass, mock_config_entry, mock_setup_entry, mock_stewart_client
) -> None:
    """Test inverted motor mapping flips both state and commands."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, options={"invert_a": True})

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    callback = mock_stewart_client.register_callback.call_args.args[0]
    await callback(
        ProtocolMessage(
            kind="event",
            motor=MOTOR_A,
            name="POSITION",
            value="25",
            raw="!1.1.1.MOTOR.POSITION=25;",
        )
    )
    await callback(
        ProtocolMessage(
            kind="event",
            motor=MOTOR_A,
            name="STATUS",
            value=STATUS_EXTENDING,
            raw="!1.1.1.MOTOR.STATUS=EXTENDING;",
        )
    )
    await hass.async_block_till_done()

    state = hass.states.get("cover.screen_motor_1")
    assert state
    assert state.attributes["current_position"] == 25
    assert state.state == "opening"

    await hass.services.async_call(
        "cover",
        "open_cover",
        {"entity_id": state.entity_id},
        blocking=True,
    )
    await hass.services.async_call(
        "cover",
        "close_cover",
        {"entity_id": state.entity_id},
        blocking=True,
    )

    assert mock_stewart_client.send_command.await_args_list[-2].args == (
        MOTOR_A,
        COMMAND_DOWN,
    )
    assert mock_stewart_client.send_command.await_args_list[-1].args == (
        MOTOR_A,
        COMMAND_UP,
    )
