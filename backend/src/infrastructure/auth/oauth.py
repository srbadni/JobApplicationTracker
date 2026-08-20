"""crudauth OAuth building blocks for the project's own OAuth routes.

Runs the existing ``/oauth/google`` routes on crudauth's hardened OAuth
(PKCE + signed state + verified-email account linking) without mounting crudauth's
own oauth router - which would change the URLs. We construct the provider, a
per-request state store, and the account-linking service here and drive them from
the route handlers in ``routes.py``.
"""

from crudauth.oauth import OAuthAccountService, OAuthProviderFactory
from crudauth.storage import get_session_storage

from ..config.settings import settings
from .setup import _auth_state_redis_url, _use_redis_state, auth

OAUTH_STATE_TTL_SECONDS = 1800
OAUTH_EXCHANGE_TTL_SECONDS = 60

_redirect_base = settings.OAUTH_REDIRECT_BASE_URL.rstrip("/")


def _build_provider(name: str, client_id: str, client_secret: str):
    return OAuthProviderFactory.create_provider(
        name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{_redirect_base}/api/v1/auth/oauth/callback/{name}",
    )


# Only Google has a wired route; add a "github" entry here (and its routes) to enable it.
oauth_providers = {
    "google": _build_provider("google", settings.OAUTH_GOOGLE_CLIENT_ID, settings.OAUTH_GOOGLE_CLIENT_SECRET),
}

oauth_state_storage = get_session_storage(
    "redis" if _use_redis_state else "memory",
    prefix="oauth_state:",
    expiration=OAUTH_STATE_TTL_SECONDS,
    redis_url=_auth_state_redis_url if _use_redis_state else None,
)

oauth_exchange_storage = get_session_storage(
    "redis" if _use_redis_state else "memory",
    prefix="oauth_exchange:",
    expiration=OAUTH_EXCHANGE_TTL_SECONDS,
    redis_url=_auth_state_redis_url if _use_redis_state else None,
)

oauth_account_service = OAuthAccountService(
    repo=auth.repo,
    new_user_fields=lambda ctx: {"name": ctx.suggested_name},
)


async def initialize_oauth_storage() -> None:
    """Open connections used by OAuth state and exchange-code storage."""
    await oauth_state_storage.initialize()
    await oauth_exchange_storage.initialize()


async def close_oauth_storage() -> None:
    """Close OAuth state and exchange-code storage connections."""
    await oauth_exchange_storage.close()
    await oauth_state_storage.close()
