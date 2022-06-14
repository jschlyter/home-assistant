"""Support for Lutron Caseta scenes."""
from typing import Any

from pylutron_caseta.smartbridge import Smartbridge

from homeassistant.components.scene import Scene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import _area_and_name_from_name
from .const import BRIDGE_DEVICE, BRIDGE_LEAP, DOMAIN as CASETA_DOMAIN
from .util import serial_to_unique_id


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lutron Caseta scene platform.

    Adds scenes from the Caseta bridge associated with the config_entry as
    scene entities.
    """
    data = hass.data[CASETA_DOMAIN][config_entry.entry_id]
    bridge: Smartbridge = data[BRIDGE_LEAP]
    bridge_device = data[BRIDGE_DEVICE]
    scenes = bridge.get_scenes()
    async_add_entities(
        LutronCasetaScene(scenes[scene], bridge, bridge_device) for scene in scenes
    )


class LutronCasetaScene(Scene):
    """Representation of a Lutron Caseta scene."""

    def __init__(self, scene, bridge, bridge_device):
        """Initialize the Lutron Caseta scene."""
        self._scene_id = scene["scene_id"]
        self._bridge: Smartbridge = bridge
        bridge_unique_id = serial_to_unique_id(bridge_device["serial"])
        self._attr_device_info = DeviceInfo(
            identifiers={(CASETA_DOMAIN, bridge_device["serial"])},
        )
        self._attr_name = _area_and_name_from_name(scene["name"])[1]
        self._attr_unique_id = f"scene_{bridge_unique_id}_{self._scene_id}"

    async def async_activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        await self._bridge.activate_scene(self._scene_id)
