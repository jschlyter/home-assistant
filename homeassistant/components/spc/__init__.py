"""Support for Vanderbilt (formerly Siemens) SPC alarm systems."""

import functools

from pyspcwebgw import SpcWebGateway
from pyspcwebgw.area import Area
from pyspcwebgw.zone import Zone

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_API_URL,
    CONF_WS_URL,
    DOMAIN,
    SIGNAL_UPDATE_ALARM,
    SIGNAL_UPDATE_SENSOR,
)

PLATFORMS = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
]


async def async_update_callback(hass, spc_object):

    if isinstance(spc_object, Area):
        async_dispatcher_send(hass, SIGNAL_UPDATE_ALARM.format(spc_object.id))
    elif isinstance(spc_object, Zone):
        async_dispatcher_send(hass, SIGNAL_UPDATE_SENSOR.format(spc_object.id))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPC component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    spc = SpcWebGateway(
        loop=hass.loop,
        session=async_get_clientsession(hass),
        api_url=entry.data[CONF_API_URL],
        ws_url=entry.data[CONF_WS_URL],
        async_callback=functools.partial(async_update_callback, hass),
    )

    if not await spc.async_load_parameters():
        raise ConfigEntryNotReady("Failed to load area/zone information from SPC")

    hass.data[DOMAIN] = spc

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    # start listening for incoming events over websocket
    spc.start()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        api = hass.data.pop(DOMAIN)
        # api.stop()

    return unload_ok
