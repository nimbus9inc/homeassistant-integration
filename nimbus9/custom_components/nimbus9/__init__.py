"""The Unifi Control integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import LightDataCoordinator

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.LIGHT]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up Unifi Control from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    try:
        # Create and initialize the coordinator
        coordinator = LightDataCoordinator(
            hass,
            n9_api=entry.data["n9_api"],
            n9_access_token=entry.data["n9_access_token"],
            n9_account=entry.data["n9_account_id"],
            n9_location=entry.data["n9_location_id"],
        )
        await coordinator.async_config_entry_first_refresh()

        # Store the coordinator for platform access
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    except Exception as err:
        # Log the error and raise ConfigEntryNotReady for temporary failures
        hass.data.setdefault(DOMAIN, {}).pop(entry.entry_id, None)
        raise ConfigEntryNotReady from err

    # Forward the entry setup to the supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
