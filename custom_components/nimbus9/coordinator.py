from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import N9_API_AREAS_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


class N9LightDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        n9_oauth_session: config_entry_oauth2_flow.OAuth2Session,
        n9_api_url: str,
        n9_account: str,
        n9_location: str,
    ):
        self.n9_oauth_session = n9_oauth_session
        self.n9_api_url = n9_api_url
        self.n9_account_id = n9_account
        self.n9_location_id = n9_location

        super().__init__(
            hass,
            _LOGGER,
            name="Nimbus 9 API Light Coordinator",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            url = N9_API_AREAS_URL.format(
                api_url=self.n9_api_url,
                account=self.n9_account_id,
                location=self.n9_location_id,
            )
            resp = await self.n9_oauth_session.async_request(
                "GET",
                url,
            )
            if resp.status != 200:
                raise UpdateFailed(
                    f"API error: {url} [{resp.status}] - {await resp.text()}"
                )
            return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch areas: {err}")
