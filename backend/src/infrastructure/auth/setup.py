"""crudauth composition root for bearer-only API authentication.

The module-level ``auth`` singleton is constructed at import time because route
dependencies reference it directly. The application lifespan only initializes
and shuts it down.

API credentials are JWTs accepted exclusively through ``Authorization: Bearer``.
The optional Redis backend is used only for authentication state that must remain
server-side (login lockout counters and OAuth state/exchange codes); it does not
store API sessions.
"""

from crudauth import BearerTransport, CRUDAuth
from crudauth.identity import IdentityConfig
from crudauth.ratelimit import redis_rate_limiter

from ...modules.user.models import User
from ..config.settings import settings
from ..database.session import async_session

_redis_password = settings.AUTH_STATE_REDIS_PASSWORD
_redis_auth = f":{_redis_password}@" if _redis_password else ""
_auth_state_redis_url = (
    f"redis://{_redis_auth}{settings.AUTH_STATE_REDIS_HOST}:{settings.AUTH_STATE_REDIS_PORT}/{settings.AUTH_STATE_REDIS_DB}"
)

_use_redis_state = settings.AUTH_STATE_BACKEND == "redis"

bearer_transport = BearerTransport(
    access_ttl=settings.JWT_ACCESS_TOKEN_TTL_SECONDS,
    refresh_ttl_days=settings.JWT_REFRESH_TOKEN_TTL_DAYS,
    refresh="body",
)

auth = CRUDAuth(
    session=async_session,
    user_model=User,
    SECRET_KEY=settings.SECRET_KEY,
    identity=IdentityConfig(login=["email"], recovery="email"),
    algorithm=settings.JWT_ALGORITHM,
    transports=[bearer_transport],
    rate_limiter=(redis_rate_limiter(redis_url=_auth_state_redis_url) if _use_redis_state else None),
    trusted_proxy_hops=settings.TRUSTED_PROXY_HOPS,
    # crudauth's generic warning assumes an absent SessionTransport means an
    # in-memory session store. This API is intentionally bearer-only; the actual
    # OAuth/lockout state backend is validated by ProductionSecurityValidator.
    warn_on_memory_backend=False,
)
