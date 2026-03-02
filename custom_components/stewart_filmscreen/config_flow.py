"""Config flow for Stewart Filmscreen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from stewart_filmscreen.client import StewartFilmscreenClient
from stewart_filmscreen.const import DEFAULT_PORT
from stewart_filmscreen.exceptions import AuthenticationError, ConnectionFailedError

from .const import CONF_INVERT_A, CONF_INVERT_B, CONF_INVERT_C, CONF_INVERT_D, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_INVERT_A, default=False): bool,
        vol.Optional(CONF_INVERT_B, default=True): bool,
        vol.Optional(CONF_INVERT_C, default=False): bool,
        vol.Optional(CONF_INVERT_D, default=True): bool,
    }
)


async def _validate_input(data: dict[str, Any]) -> None:
    client = StewartFilmscreenClient(
        host=str(data[CONF_HOST]).strip(),
        port=int(data[CONF_PORT]),
        username=str(data[CONF_USERNAME]),
        password=str(data[CONF_PASSWORD]),
    )
    try:
        await client.start()
        await client.wait_authenticated(timeout=8)
    finally:
        await client.stop_client()


class StewartFilmscreenConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _validate_input(user_input)
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ConnectionFailedError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                host = str(user_input[CONF_HOST]).strip()
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Stewart Filmscreen ({host})", data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry):
        return OptionsFlow(config_entry)


class OptionsFlow(OptionsFlowWithConfigEntry):
    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__(config_entry)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA)
