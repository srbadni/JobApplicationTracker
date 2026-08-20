# Authentication & Security

The API uses **JWT bearer authentication**. A client obtains an access/refresh
token pair from the login endpoint and explicitly sends the access token in the
`Authorization` header. API authentication does not use cookies or CSRF tokens.

The SQLAdmin UI still uses Starlette's `SessionMiddleware`; that is an isolated
admin-browser session and is not accepted by API routes.

## Authentication mechanisms

| Mechanism | Intended client | Credential |
|---|---|---|
| JWT bearer | Browser SPA, mobile app, CLI | `Authorization: Bearer <access_token>` |
| Google OAuth | Interactive user login | Produces the same JWT token pair |
| API key | Machine-to-machine integration | API key header and key permissions |
| Admin session | SQLAdmin UI only | Starlette session cookie |

## Password login

`POST /api/v1/auth/login` accepts OAuth2 form data. The `username` form field
contains the user's email address.

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

Response:

```json
{
  "access_token": "<short-lived-jwt>",
  "refresh_token": "<long-lived-jwt>",
  "token_type": "bearer"
}
```

Use the access token on protected requests:

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

Swagger UI declares an OAuth2 password flow whose token URL is
`/api/v1/auth/login`. The **Authorize** dialog logs in and automatically adds the
Bearer header to protected operations.

## Refresh and logout

Exchange a refresh token for a new pair:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

Logout requires the current access token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

JWTs are stateless, so logout advances the user's `token_version`. That revokes
all access and refresh tokens previously issued to that user. The
`a1c4e7f9b203` Alembic migration adds this credential-epoch column.

## Why API requests do not need CSRF tokens

Browsers automatically attach cookies, which creates the classic CSRF attack
surface. They do not automatically invent and attach an
`Authorization: Bearer` header. Because this API's credential must be explicitly
read and placed in that header by the client, the old `X-CSRF-Token` dependency
and `/auth/refresh-csrf` endpoint are not part of the bearer flow.

This does not make client-side token storage risk-free. Avoid exposing tokens to
third-party scripts, never put them in query strings, and always use HTTPS in
production.

## Dependencies used by routes

All dependencies live in `src/infrastructure/auth/dependencies.py`:

- `get_current_user` returns the authenticated user dict or raises 401.
- `get_optional_user` returns the user dict or `None`.
- `get_current_superuser` additionally requires `is_superuser=True`, otherwise 403.
- `get_current_principal` returns crudauth's bearer `Principal`.

The public `CurrentUserDep`, `CurrentSuperUserDep`, and `OptionalUserDep` aliases
remain in `src/infrastructure/dependencies.py`, so business routes do not need to
know how JWT validation works.

```python
@router.post("")
async def create_item(
    item: ItemCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    return await service.create(db=db, owner_id=current_user["id"], item=item)
```

## Google OAuth

Start the provider flow with `GET /api/v1/auth/oauth/google`.

- `response_format=json` on the callback returns user data plus the JWT pair.
- Redirect mode sends the frontend a short-lived `oauth_code` query parameter.
  Exchange it once at `POST /api/v1/auth/oauth/exchange` with
  `{"code":"..."}` to receive the JWT pair.

The one-time exchange avoids placing access or refresh tokens in a redirect URL.
OAuth state, PKCE, and exchange codes are kept in Redis in production and memory
in tests.

## Configuration

```env
SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_TTL_SECONDS=900
JWT_REFRESH_TOKEN_TTL_DAYS=30

# Redis in production; memory only for local development/tests.
# This stores OAuth/lockout state, not JWT sessions.
AUTH_STATE_BACKEND=redis
AUTH_STATE_REDIS_HOST=redis
AUTH_STATE_REDIS_PORT=6379
AUTH_STATE_REDIS_DB=2
AUTH_STATE_REDIS_PASSWORD=

TRUSTED_PROXY_HOPS=0
OAUTH_REDIRECT_BASE_URL=http://localhost:8000
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GOOGLE_CLIENT_SECRET=
```

Run `uv run alembic upgrade head` after deploying the change.

## Minimal browser client

```javascript
class AuthClient {
    accessToken = null;
    refreshToken = null;

    async login(email, password) {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({username: email, password}),
        });
        if (!response.ok) throw new Error('Login failed');
        const tokens = await response.json();
        this.accessToken = tokens.access_token;
        this.refreshToken = tokens.refresh_token;
    }

    request(url, options = {}) {
        return fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                Authorization: `Bearer ${this.accessToken}`,
            },
        });
    }
}
```

The example keeps tokens in memory. A production frontend should define its
storage and refresh strategy explicitly according to its threat model.

## Key files

| Component | Location |
|---|---|
| crudauth bearer composition | `backend/src/infrastructure/auth/setup.py` |
| FastAPI auth dependencies | `backend/src/infrastructure/auth/dependencies.py` |
| Login, refresh, logout, OAuth routes | `backend/src/infrastructure/auth/routes.py` |
| JWT lifecycle helpers | `backend/src/infrastructure/auth/tokens.py` |
| OAuth state/exchange storage | `backend/src/infrastructure/auth/oauth.py` |
| Token schemas | `backend/src/infrastructure/auth/schemas.py` |
| Auth configuration | `backend/src/infrastructure/config/settings.py` |

Continue with [Bearer token lifecycle](sessions.md),
[User Management](user-management.md), and [Permissions](permissions.md).
