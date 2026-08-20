# JWT Bearer Token Lifecycle

!!! note "Legacy page path"
    This file keeps its historical `sessions.md` path so existing documentation
    links continue to work. API authentication is now bearer-only; only the
    separate SQLAdmin UI uses a cookie session.

## Architecture

`infrastructure/auth/setup.py` configures one crudauth `BearerTransport`:

```python
bearer_transport = BearerTransport(
    access_ttl=settings.JWT_ACCESS_TOKEN_TTL_SECONDS,
    refresh_ttl_days=settings.JWT_REFRESH_TOKEN_TTL_DAYS,
    refresh="body",
)

auth = CRUDAuth(
    session=async_session,
    user_model=User,
    SECRET_KEY=settings.SECRET_KEY,
    transports=[bearer_transport],
    algorithm=settings.JWT_ALGORITHM,
)
```

The `session=` argument above is the SQLAlchemy database dependency expected by
crudauth; it does not enable browser sessions. `transports` contains only the
bearer transport.

## Access tokens

Access tokens are short-lived JWTs. The bearer transport verifies:

1. Signature and expiry.
2. The `token_type=access` claim.
3. The subject maps to an active, non-deleted user.
4. The token's `ver` claim equals the user's current `token_version`.

Protected requests send the token explicitly:

```http
Authorization: Bearer eyJ...
```

Missing, expired, revoked, or invalid credentials produce 401 on required-auth
routes. Optional-auth routes resolve to an anonymous caller when no valid token
is present.

## Refresh tokens

Refresh JWTs have `token_type=refresh` and a longer lifetime. They cannot be used
as access credentials. `POST /api/v1/auth/refresh` verifies the token and returns
a new pair:

```json
{"refresh_token":"<refresh-jwt>"}
```

The current crudauth bearer transport is stateless and does not keep a per-token
refresh blacklist. Keep refresh tokens protected and use a suitably short
lifetime for the application.

## Revocation and logout

The `user.token_version` column is a credential epoch embedded in both token
types. `POST /api/v1/auth/logout` increments it. Every older access and refresh
token for that account then fails validation without maintaining a token table.

This means logout is account-wide rather than device-specific. Per-device
revocation would require a server-side refresh-token registry and rotation,
which this bearer-only implementation intentionally does not add.

## CSRF boundary

The API no longer accepts an automatically attached authentication cookie, so it
does not check `X-CSRF-Token`. The client must explicitly attach its access token
to the `Authorization` header. The SQLAdmin browser session remains a separate
surface under `/admin`.

## OAuth state is not an API session

`AUTH_STATE_BACKEND` selects Redis or memory for short-lived OAuth state,
one-time OAuth exchange codes, and login-lockout counters. This state does not
authenticate ordinary API requests and does not make JWTs stateful.

Use Redis for multi-worker production deployments:

```env
AUTH_STATE_BACKEND=redis
AUTH_STATE_REDIS_HOST=redis
AUTH_STATE_REDIS_DB=2
JWT_ACCESS_TOKEN_TTL_SECONDS=900
JWT_REFRESH_TOKEN_TTL_DAYS=30
```

## Route dependencies

`get_current_principal` deliberately narrows crudauth to
`transport="bearer"`. An `OAuth2PasswordBearer` dependency declares the same
flow in OpenAPI, which is why Swagger UI can log in and attach the header.

The business-facing dependency remains unchanged:

```python
CurrentUserDep = Annotated[dict[str, Any], Depends(get_current_user)]
```

`get_current_user` re-loads the full active user row after JWT validation, so
services continue to receive the same user dictionary they used before the auth
transport migration.

## Operational checklist

- Run `uv run alembic upgrade head` to add `token_version`.
- Use a strong, private `SECRET_KEY` and HTTPS.
- Keep access tokens short-lived.
- Treat refresh tokens as credentials, never log them or place them in URLs.
- Use `AUTH_STATE_BACKEND=redis` when running multiple API workers.
- Send no `X-CSRF-Token`; send `Authorization: Bearer <access_token>`.

See the [Authentication Overview](index.md) for endpoint and client examples.
