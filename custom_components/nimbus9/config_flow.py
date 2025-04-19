"""Config flow for the Unifi Control integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import (
    CONF_N9_ACCOUNT_ID,
    CONF_N9_API_URL,
    CONF_N9_LOCATION_ID,
    CONF_N9_SSO_CLIENT_ID,
    CONF_N9_SSO_CLIENT_SECRET,
    CONF_N9_SSO_REALM,
    CONF_N9_SSO_URL,
    DEFAULT_N9_API_URL,
    DEFAULT_N9_SSO_URL,
    DOMAIN,
    N9_API_OAUTH_AUTHORIZATION_URL,
    N9_API_OAUTH_TOKEN_URL,
    N9_SSO_SCOPES,
)
from .scoped_oauth_impl import ScopedOAuth2Implementation

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_N9_ACCOUNT_ID): str,
        vol.Required(CONF_N9_LOCATION_ID): str,
        vol.Required(CONF_N9_SSO_REALM): str,
        vol.Required(CONF_N9_SSO_CLIENT_ID): str,
        vol.Required(CONF_N9_SSO_CLIENT_SECRET): str,
        vol.Optional(CONF_N9_API_URL, default=DEFAULT_N9_API_URL): str,
        vol.Optional(CONF_N9_SSO_URL, default=DEFAULT_N9_SSO_URL): str,
    }
)


class Nimbus9ConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a config flow for Unifi Control."""

    VERSION = 1
    DOMAIN = DOMAIN

    def __init__(self) -> None:
        #     """Create a new instance of the flow handler."""
        super().__init__()

    @property
    def logger(self) -> logging.Logger:
        """Return the logger for this flow."""
        return _LOGGER

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Abort if we've already made an identical config
            #
            self._async_abort_entries_match(
                {
                    CONF_N9_API_URL: user_input[CONF_N9_API_URL],
                    CONF_N9_SSO_URL: user_input[CONF_N9_SSO_URL],
                    CONF_N9_ACCOUNT_ID: user_input[CONF_N9_ACCOUNT_ID],
                    CONF_N9_LOCATION_ID: user_input[CONF_N9_LOCATION_ID],
                    CONF_N9_SSO_REALM: user_input[CONF_N9_SSO_REALM],
                }
            )

            # Store the user input for later use
            #
            self.context.update(user_input)

            self.flow_impl = ScopedOAuth2Implementation(
                self.hass,
                domain=f"{DOMAIN}-config_flow",
                client_id=user_input[CONF_N9_SSO_CLIENT_ID],
                client_secret=user_input[CONF_N9_SSO_CLIENT_SECRET],
                authorize_url=N9_API_OAUTH_AUTHORIZATION_URL.format(
                    sso_url=user_input[CONF_N9_SSO_URL],
                    realm=user_input[CONF_N9_SSO_REALM],
                ),
                token_url=N9_API_OAUTH_TOKEN_URL.format(
                    sso_url=user_input[CONF_N9_SSO_URL],
                    realm=user_input[CONF_N9_SSO_REALM],
                ),
                scopes=N9_SSO_SCOPES,
            )

            # Proceed to OAuth step
            #
            return await self.async_step_auth()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_oauth_create_entry(
        self, data: dict
    ) -> config_entries.ConfigFlowResult:
        """Create an entry for the flow."""
        data.update(
            {
                "title": f"SSO Realm {self.context[CONF_N9_SSO_REALM]}",
                CONF_N9_API_URL: self.context[CONF_N9_API_URL],
                CONF_N9_SSO_URL: self.context[CONF_N9_SSO_URL],
                CONF_N9_ACCOUNT_ID: self.context[CONF_N9_ACCOUNT_ID],
                CONF_N9_LOCATION_ID: self.context[CONF_N9_LOCATION_ID],
                CONF_N9_SSO_REALM: self.context[CONF_N9_SSO_REALM],
                CONF_N9_SSO_CLIENT_ID: self.context[CONF_N9_SSO_CLIENT_ID],
                CONF_N9_SSO_CLIENT_SECRET: self.context[CONF_N9_SSO_CLIENT_SECRET],
            }
        )
        return await super().async_oauth_create_entry(data)
