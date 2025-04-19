from datetime import timedelta
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import N9_API_AREAS_URI

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


class LightDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self, hass, n9_api: str, n9_access_token: str, n9_account: str, n9_location: str
    ):
        self.n9_api = n9_api
        self.n9_access_token = n9_access_token
        self.n9_account = n9_account
        self.n9_location = n9_location
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name="Nimbus 9 API Light Coordinator",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            url = N9_API_AREAS_URI.format(
                api=self.n9_api, account=self.n9_account, location=self.n9_location
            )
            async with self.session.get(
                url,
                headers={"Authorization": f"Bearer {self.n9_access_token}"},
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(
                        f"API error: {url} [{resp.status}] - {await resp.text()}"
                    )
                return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch lights: {err}")
