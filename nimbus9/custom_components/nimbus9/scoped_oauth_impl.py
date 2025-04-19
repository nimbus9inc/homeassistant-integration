import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation

_LOGGER = logging.getLogger(__name__)


class ScopedOAuth2Implementation(LocalOAuth2Implementation):
    """Oauth implementation to add scope."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        scopes: list[str],
    ) -> None:
        super().__init__(
            hass=hass,
            domain=domain,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=authorize_url,
            token_url=token_url,
        )
        self._scopes = scopes

    @property
    def extra_authorize_data(self) -> dict[str, str]:
        """Extra scope(s) to be appended to the authorize url."""
        return {"scope": " ".join(self._scopes)}
