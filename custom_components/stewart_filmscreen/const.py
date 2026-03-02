"""Constants for Stewart Filmscreen integration."""

from __future__ import annotations

DOMAIN = "stewart_filmscreen"
CLIENT_ID = "homeassistant"

CONF_INVERT_A = "invert_a"
CONF_INVERT_B = "invert_b"
CONF_INVERT_C = "invert_c"
CONF_INVERT_D = "invert_d"

SERVICE_RECALL_PRESET = "recall_preset"
SERVICE_STORE_PRESET = "store_preset"

ATTR_PRESET_NUMBER = "preset_number"
ATTR_MANUFACTURER = "Stewart Filmscreen"
ATTR_MODEL = "CVM"

PLATFORMS = ["cover"]
