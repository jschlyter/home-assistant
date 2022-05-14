"""Config flow to configure Vanderbilt (formerly Siemens) SPC alarm systems."""

from __future__ import annotations

from typing import Any

from pyspcwebgw import SpcWebGateway
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import CONF_API_URL, CONF_WS_URL, DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WS_URL): cv.string,
        vol.Required(CONF_API_URL): cv.string,
    }
)


class SpcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vanderbilt SPC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}

        try:
            spc = SpcWebGateway(
                loop=self.hass.loop,
                session=async_get_clientsession(self.hass),
                api_url=user_input[CONF_API_URL],
                ws_url=user_input[CONF_WS_URL],
                async_callback=None,
            )

            if not await spc.async_load_parameters():
                errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        await self.async_set_unique_id(spc.info["sn"])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Vanderbilt SPC", data=user_input)
