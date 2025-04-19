"""The Unifi Control integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_entry_oauth2_flow

from .const import (
    CONF_N9_ACCOUNT_ID,
    CONF_N9_API_URL,
    CONF_N9_LOCATION_ID,
    CONF_N9_SSO_CLIENT_ID,
    CONF_N9_SSO_CLIENT_SECRET,
    CONF_N9_SSO_REALM,
    CONF_N9_SSO_URL,
    DOMAIN,
    N9_API_OAUTH_AUTHORIZATION_URL,
    N9_API_OAUTH_TOKEN_URL,
    N9_SSO_SCOPES,
)
from .coordinator import N9LightDataCoordinator
from .scoped_oauth_impl import ScopedOAuth2Implementation

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.LIGHT]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unifi Control from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    try:
        # Gotta do this ourselves instead of using `application_credentials` since we need to
        # dynamically generate SSO auth URLs
        #
        oauth_implementation = ScopedOAuth2Implementation(
            hass,
            domain=DOMAIN,
            client_id=entry.data.get(CONF_N9_SSO_CLIENT_ID),
            client_secret=entry.data.get(CONF_N9_SSO_CLIENT_SECRET),
            authorize_url=N9_API_OAUTH_AUTHORIZATION_URL.format(
                sso_url=entry.data.get(CONF_N9_SSO_URL),
                realm=entry.data.get(CONF_N9_SSO_REALM),
            ),
            token_url=N9_API_OAUTH_TOKEN_URL.format(
                sso_url=entry.data.get(CONF_N9_SSO_URL),
                realm=entry.data.get(CONF_N9_SSO_REALM),
            ),
            scopes=N9_SSO_SCOPES,
        )
        oauth_session = config_entry_oauth2_flow.OAuth2Session(
            hass, entry, oauth_implementation
        )

        # Create and initialize the coordinator
        #
        coordinator = N9LightDataCoordinator(
            hass,
            n9_oauth_session=oauth_session,
            n9_api_url=entry.data[CONF_N9_API_URL],
            n9_account=entry.data[CONF_N9_ACCOUNT_ID],
            n9_location=entry.data[CONF_N9_LOCATION_ID],
        )
        await coordinator.async_config_entry_first_refresh()

        # Store the coordinator for platform access
        #
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    except Exception as err:
        # Log the error and raise ConfigEntryNotReady for temporary failures
        hass.data.setdefault(DOMAIN, {}).pop(entry.entry_id, None)
        raise ConfigEntryNotReady from err

    # Forward the entry setup to the supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
