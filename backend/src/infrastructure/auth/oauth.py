"""crudauth OAuth building blocks for the project's own OAuth routes.

Runs the existing ``/oauth/google`` routes on crudauth's hardened OAuth
(PKCE + signed state + verified-email account linking) without mounting crudauth's
own oauth router - which would change the URLs. We construct the provider, a
per-request state store, and the account-linking service here and drive them from
the route handlers in ``routes.py``.
"""

from crudauth.oauth import OAuthAccountService, OAuthProviderFactory
from crudauth.provisioning import NewUserContext
from crudauth.storage import get_session_storage
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import settings
from .setup import _session_redis_url, _use_redis, auth

OAUTH_STATE_TTL_SECONDS = 1800
OAUTH_PLACEHOLDER_PHONE_NUMBER = "09000000000"

_redirect_base = settings.OAUTH_REDIRECT_BASE_URL.rstrip("/")


def _build_provider(name: str, client_id: str, client_secret: str):
    return OAuthProviderFactory.create_provider(
        name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=f"{_redirect_base}/api/v1/auth/oauth/callback/{name}",
    )


class PhoneNumberOAuthAccountService(OAuthAccountService):
    """Provision OAuth users when the application has no ``username`` column.

    crudauth 0.6 still generates and queries a username while creating an OAuth
    account, even when email is the only configured login identity. The project
    removed that column, so skip only the obsolete availability lookup. The
    returned compatibility value is ignored by ``UserRepository.create`` because
    the model has no username attribute; the base class keeps ownership of the
    remaining OAuth linking and provisioning flow.
    """

    async def _unique_username(self, db: AsyncSession, base: str) -> str:
        return base


def _oauth_new_user_fields(context: NewUserContext) -> dict[str, str]:
    """Fill application-required fields that OAuth providers do not guarantee."""
    display_name = context.suggested_name.strip()
    if len(display_name) < 2:
        display_name = "OAuth User"
    return {
        "name": display_name[:30],
        "phone_number": OAUTH_PLACEHOLDER_PHONE_NUMBER,
    }


# Only Google has a wired route; add a "github" entry here (and its routes) to enable it.
oauth_providers = {
    "google": _build_provider("google", settings.OAUTH_GOOGLE_CLIENT_ID, settings.OAUTH_GOOGLE_CLIENT_SECRET),
}

oauth_state_storage = get_session_storage(
    "redis" if _use_redis else "memory",
    prefix="oauth_state:",
    expiration=OAUTH_STATE_TTL_SECONDS,
    redis_url=_session_redis_url if _use_redis else None,
)

oauth_account_service = PhoneNumberOAuthAccountService(
    repo=auth.repo,
    new_user_fields=_oauth_new_user_fields,
)
