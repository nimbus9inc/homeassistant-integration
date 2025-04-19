"""Constants for the Unifi Control integration."""

DOMAIN = "nimbus9"

N9_SSO_SCOPES = ["openid", "offline_access"]

CONF_N9_API_URL = "n9_api_url"
CONF_N9_SSO_URL = "n9_sso_url"
CONF_N9_SSO_REALM = "n9_sso_realm"
CONF_N9_SSO_CLIENT_ID = "n9_sso_client_id"
CONF_N9_SSO_CLIENT_SECRET = "n9_sso_client_secret"
CONF_N9_ACCOUNT_ID = "n9_account_id"
CONF_N9_LOCATION_ID = "n9_location_id"

DEFAULT_N9_API_URL = "https://api.nimbus9.io"
DEFAULT_N9_SSO_URL = "https://sso.nimbus9.io"

N9_API_OAUTH_AUTHORIZATION_URL = (
    "{sso_url}/auth/realms/{realm}/protocol/openid-connect/auth"
)
N9_API_OAUTH_TOKEN_URL = "{sso_url}/auth/realms/{realm}/protocol/openid-connect/token"
N9_API_AREAS_URL = "{api_url}/v2/control/account/{account}/location/{location}/area"
N9_API_AREA_URL = N9_API_AREAS_URL + "/{area}"
