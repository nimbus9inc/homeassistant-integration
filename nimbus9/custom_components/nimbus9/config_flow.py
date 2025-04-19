"""Config flow for the Unifi Control integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_N9_ACCESS_TOKEN,
    CONF_N9_ACCOUNT_ID,
    CONF_N9_API,
    CONF_N9_LOCATION_ID,
    DEFAULT_N9_API,
    DOMAIN,
    N9_API_AUTH_URI,
)

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_N9_ACCOUNT_ID): str,
        vol.Required(CONF_N9_LOCATION_ID): str,
        vol.Required(CONF_N9_ACCESS_TOKEN): str,
        vol.Optional(CONF_N9_API, default=DEFAULT_N9_API): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, n9_api: str, n9_access_token: str, n9_account_id: str) -> None:
        """Initialize."""
        self._n9_api_host = n9_api
        self._n9_access_token = n9_access_token
        self._n9_account_id = n9_account_id

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        session = aiohttp.ClientSession()
        try:
            async with session.get(
                N9_API_AUTH_URI.format(
                    api=self._n9_api_host, account=self._n9_account_id
                ),
                headers={"Authorization": f"Bearer {self._n9_access_token}"},
            ) as response:
                _LOGGER.warning(response)
                return response.ok
        except Exception:
            _LOGGER.exception("Error authenticating against Nimbus9 API")
            return False
        finally:
            await session.close()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = PlaceholderHub(
        data[CONF_N9_API], data[CONF_N9_ACCESS_TOKEN], data[CONF_N9_ACCOUNT_ID]
    )

    if not await hub.authenticate():
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Nimbus9 Areas"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unifi Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
