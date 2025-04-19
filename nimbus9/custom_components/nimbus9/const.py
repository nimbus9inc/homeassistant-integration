"""Constants for the Unifi Control integration."""

DOMAIN = "nimbus9"

CONF_N9_API = "n9_api"
CONF_N9_ACCESS_TOKEN = "n9_access_token"
CONF_N9_ACCOUNT_ID = "n9_account_id"
CONF_N9_LOCATION_ID = "n9_location_id"

DEFAULT_N9_API = "https://api.nimbus9.io"

N9_API_AUTH_URI = "{api}/v2/auth/account/{account}"
N9_API_AREAS_URI = "{api}/v2/control/account/{account}/location/{location}/area"
N9_API_AREA_URI = N9_API_AREAS_URI + "/{area}"
