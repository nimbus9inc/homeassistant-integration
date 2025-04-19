import logging

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, N9_API_AREA_URL
from .coordinator import N9LightDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Nimbus9 lights from a config entry."""
    # Fetch the existing coordinator from hass.data
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Ensure the coordinator has been refreshed
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


class N9APIArea(CoordinatorEntity, LightEntity):
    def __init__(
        self,
        coordinator: N9LightDataCoordinator,
        light_id: str,
        name: str,
        supported_color_modes: set[ColorMode] | None,
    ):
        super().__init__(coordinator, context=light_id)
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
        url = N9_API_AREA_URL.format(
            api_url=self.coordinator.n9_api_url,
            account=self.coordinator.n9_account_id,
            location=self.coordinator.n9_location_id,
            area=self._light_id,
        )
        payload = {"state": {"power": "ON"}}
        if ATTR_BRIGHTNESS in kwargs:
            payload["state"]["dimlevel"] = kwargs[ATTR_BRIGHTNESS] / 255

        try:
            resp = await self.coordinator.n9_oauth_session.async_request(
                "PATCH",
                url,
                json=payload,
            )
            if resp.status == 200:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to turn on %s: %s", self._name, await resp.text())
        except Exception as e:
            _LOGGER.error("Exception turning on %s: %s", self._name, e)

    async def async_turn_off(self, **kwargs):
        url = N9_API_AREA_URL.format(
            api_url=self.coordinator.n9_api_url,
            account=self.coordinator.n9_account_id,
            location=self.coordinator.n9_location_id,
            area=self._light_id,
        )
        payload = {"state": {"power": "OFF"}}
        if ATTR_BRIGHTNESS in kwargs:
            payload["state"]["dimlevel"] = kwargs[ATTR_BRIGHTNESS]

        try:
            resp = await self.coordinator.n9_oauth_session.async_request(
                "PATCH",
                url,
                json=payload,
            )
            if resp.status == 200:
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error(
                    "Failed to turn off %s: %s", self._name, await resp.text()
                )
        except Exception as e:
            _LOGGER.error("Exception turning on %s: %s", self._name, e)

    async def async_update(self):
        await self.coordinator.async_request_refresh()
