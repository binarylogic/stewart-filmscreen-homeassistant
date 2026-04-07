"""Test Stewart Filmscreen preset buttons."""

from __future__ import annotations


async def test_preset_buttons_are_exposed_and_recall_presets(
    hass, mock_config_entry, mock_setup_entry, mock_stewart_client
) -> None:
    """Test preset buttons call through to recall_preset."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("button.recall_preset_1")
    assert state

    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": "button.recall_preset_1"},
        blocking=True,
    )

    mock_stewart_client.recall_preset.assert_awaited_once_with(1)
