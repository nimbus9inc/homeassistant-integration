import logging

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity

from .const import (
    CONF_N9_ACCESS_TOKEN,
    CONF_N9_ACCOUNT_ID,
    CONF_N9_API,
    CONF_N9_LOCATION_ID,
    N9_API_AREA_URI,
)
from .coordinator import LightDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = LightDataCoordinator(
        hass,
        n9_api=config_entry.data[CONF_N9_API],
        n9_access_token=config_entry.data[CONF_N9_ACCESS_TOKEN],
        n9_account=config_entry.data[CONF_N9_ACCOUNT_ID],
        n9_location=config_entry.data[CONF_N9_LOCATION_ID],
    )
    await coordinator.async_config_entry_first_refresh()

    lights = coordinator.data
    entities = [
        N9APIArea(
            coordinator=coordinator,
            light_id=light["id"],
            name=light["name"],
            supported_color_modes={ColorMode.BRIGHTNESS},
        )
        for light in lights
    ]
    async_add_entities(entities)


class N9APIArea(LightEntity):
    def __init__(
        self,
        coordinator: LightDataCoordinator,
        light_id: str,
        name: str,
        supported_color_modes: set[ColorMode] | None,
    ):
        self.coordinator = coordinator
        self._light_id = light_id
        self._name = name
        self._supported_color_modes = supported_color_modes

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"n9_api_light_{self._light_id}"

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        light_data = self._get_light_data()
        return light_data and light_data["state"].get("power") == "ON"

    @property
    def brightness(self):
        light_data = self._get_light_data()
        return int(light_data["state"].get("dimlevel", 1) * 255) if light_data else 255

    @property
    def color_mode(self):
        return ColorMode.BRIGHTNESS

    @property
    def supported_color_modes(self):
        return self._supported_color_modes

    def _get_light_data(self):
        return next(
            (light for light in self.coordinator.data if light["id"] == self._light_id),
            None,
        )

    async def async_turn_on(self, **kwargs):
        url = N9_API_AREA_URI.format(
            api=self.coordinator.n9_api,
            account=self.coordinator.n9_account,
            location=self.coordinator.n9_location,
            area=self._light_id,
        )
        payload = {"state": {"power": "ON"}}
        if ATTR_BRIGHTNESS in kwargs:
            payload["state"]["dimlevel"] = kwargs[ATTR_BRIGHTNESS] / 255

        try:
            async with self.coordinator.session.patch(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.coordinator.n9_access_token}"},
            ) as resp:
                if resp.status == 200:
                    await self.coordinator.async_request_refresh()
                else:
                    _LOGGER.error(
                        "Failed to turn on %s: %s", self._name, await resp.text()
                    )
        except Exception as e:
            _LOGGER.error("Exception turning on %s: %s", self._name, e)

    async def async_turn_off(self, **kwargs):
        url = N9_API_AREA_URI.format(
            api=self.coordinator.n9_api,
            account=self.coordinator.n9_account,
            location=self.coordinator.n9_location,
            area=self._light_id,
        )
        payload = {"state": {"power": "OFF"}}
        if ATTR_BRIGHTNESS in kwargs:
            payload["state"]["dimlevel"] = kwargs[ATTR_BRIGHTNESS]

        try:
            async with self.coordinator.session.patch(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {self.coordinator.n9_access_token}"},
            ) as resp:
                if resp.status == 200:
                    await self.coordinator.async_request_refresh()
                else:
                    _LOGGER.error(
                        "Failed to turn on %s: %s", self._name, await resp.text()
                    )
        except Exception as e:
            _LOGGER.error("Exception turning on %s: %s", self._name, e)

    async def async_update(self):
        await self.coordinator.async_request_refresh()
