"""Constants for Vanderbilt (formerly Siemens) SPC alarm systems."""

import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "spc"
ATTRIBUTION = "Data provided by SPC Web Gateway"

SIGNAL_UPDATE_ALARM = "spc_update_alarm_{}"
SIGNAL_UPDATE_SENSOR = "spc_update_sensor_{}"

CONF_WS_URL = "ws_url"
CONF_API_URL = "api_url"
