# User Management

User management covers the full lifecycle: registration, authentication, profile updates, and deletion. This page documents the endpoints and patterns the project ships with.

## Endpoints at a Glance

All under `/api/v1/users/` (defined in `modules/user/routes.py`):

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/v1/users/` | Create a new user | Open |
| `GET` | `/api/v1/users/` | Paginated list of users | Superuser |
| `GET` | `/api/v1/users/me` | Current user's profile | Bearer |
| `GET` | `/api/v1/users/{username}` | Get a user by username (active only) | Open |
| `GET` | `/api/v1/users/active-and-inactive/{username}` | Same as above, includes soft-deleted | Superuser |
| `PATCH` | `/api/v1/users/{username}` | Update profile (own or admin) | Bearer |
| `DELETE` | `/api/v1/users/{username}` | Soft-delete a user (own or admin) | Bearer |
| `DELETE` | `/api/v1/users/db/{username}` | GDPR anonymize (admin) | Superuser |
| `GET` | `/api/v1/users/{username}/rate-limits` | User's rate limits via tier | Bearer |
| `GET` | `/api/v1/users/{username}/tier` | User's tier details | Bearer |
| `PATCH` | `/api/v1/users/{username}/tier` | Change a user's tier | Superuser |

Plus the auth endpoints under `/api/v1/auth/` documented in [Bearer Tokens](sessions.md).

## Registration

`POST /api/v1/users/` is open — no auth required. Anyone can create an account.

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "password": "Str1ngst!"
  }'
```

The route delegates to `UserService.create`, which:

1. Checks `email` is unique → raises `UserExistsError` if not (→ 409)
2. Checks `username` is unique → raises `UserExistsError` if not (→ 409)
3. Hashes the password with bcrypt via `get_password_hash`
4. Builds a `UserCreateInternal` (schema with `hashed_password` instead of `password`)
5. Persists via `crud_users.create`

```python
# modules/user/service.py
async def create(self, user: UserCreate, db: AsyncSession) -> dict[str, Any]:
    if await crud_users.exists(db=db, email=user.email):
        raise UserExistsError("Email already registered")
    if await crud_users.exists(db=db, username=user.username):
        raise UserExistsError("Username already taken")

    payload = user.model_dump()
    payload["hashed_password"] = get_password_hash(payload.pop("password"))
    user_internal = UserCreateInternal(**payload)

    return await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)
```

The `UserCreate` schema enforces input validation:

```python
class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[
        str,
        Field(
            min_length=8,
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["Str1ngst!"],
        ),
    ]
    # OAuth fields (filled when user signs up via Google)
    google_id: str | None = None
    github_id: str | None = None
    oauth_provider: str | None = None
```

`extra="forbid"` rejects any unknown fields the client tries to send — useful to keep clients honest.

## Authentication

Authentication happens via `POST /api/v1/auth/login`. See [Bearer Tokens](sessions.md) for the full flow. The login route delegates credential verification to the `crudauth` singleton and returns an access/refresh JWT pair. The project no longer ships an `authenticate_user` helper.

Two things to note about the login behavior:

- **Email login** — put the email address in OAuth2's `username` form field
- **Soft-deleted users can't log in** — crudauth reads `User.is_active` (defined as `not is_deleted`), so deactivated accounts are rejected before the password is even checked

### Password Hashing (bcrypt)

Password hashing helpers come from `crudauth`:

```python
from crudauth import get_password_hash, verify_password

hashed = get_password_hash("plaintext")          # bcrypt, salt generated automatically
ok = await verify_password("plaintext", hashed)  # constant-time compare
```

bcrypt handles salt generation automatically and is computationally expensive enough to defeat brute force at scale. `UserService.create` uses `get_password_hash` when persisting a new account (see [Registration](#registration)).

## Profile Operations

### Get Current User

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

Trivial route — `get_current_user` already returns the user dict:

```python
@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    return current_user
```

### Get User by Username

Public endpoint — no auth required. Filters out soft-deleted users.

```bash
curl http://localhost:8000/api/v1/users/johndoe
```

Returns 404 if not found or soft-deleted. The admin-only `/active-and-inactive/{username}` variant returns soft-deleted users too.

### Update Profile

Users can update their own profile; superusers can update anyone's. Tier updates are gated on a separate endpoint (see [Permissions](permissions.md)).

```bash
curl -X PATCH http://localhost:8000/api/v1/users/john@example.com \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'
```

The service enforces the ownership rule:

```python
# modules/user/service.py
async def verify_user_permission(
    self, current_user: dict[str, Any], target_username: str, action: str,
) -> None:
    if current_user["username"] != target_username and not current_user["is_superuser"]:
        raise PermissionDeniedError(f"Cannot {action} for another user")
```

If the body changes `username` or `email`, the service also re-checks uniqueness.

The `UserUpdate` schema makes every field optional so clients can send partial updates:

```python
class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=30, default=None)]
    username: Annotated[
        str | None,
        Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", default=None),
    ]
    email: Annotated[EmailStr | None, Field(default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", default=None),
    ]
```

## Deletion

The project distinguishes three deletion modes — pick based on what the request actually wants.

### Soft Delete

`DELETE /api/v1/users/{username}` — sets `is_deleted=True` and `deleted_at=now()`. The row stays in the database; the user can no longer log in but their data is preserved.

```bash
curl -X DELETE http://localhost:8000/api/v1/users/john@example.com \
  -H "Authorization: Bearer <access_token>"
```

Permission rules:

- A user can soft-delete their own account
- A superuser can soft-delete anyone

### Hard Delete (database)

There's no public hard-delete endpoint by design — deleting rows from `user` would orphan all related data (sessions, API keys, etc.). If you really need it, use FastCRUD's `crud_users.db_delete(...)` from a script or admin task with full understanding of the foreign-key impact.

### GDPR Anonymization

`DELETE /api/v1/users/db/{username}` — superuser only. Replaces PII with neutral values while keeping the row (and therefore foreign-key relationships) intact.

```bash
curl -X DELETE http://localhost:8000/api/v1/users/db/john@example.com \
  -H "Authorization: Bearer <superuser_access_token>"
```

Service implementation:

```python
async def anonymize_user(self, user_id: int, db: AsyncSession) -> None:
    anonymize_data = UserAnonymize(
        name="[DELETED]",
        username=f"del_{user_id}_{timestamp % 10000}",
        hashed_password="DELETED_INVALID_HASH",
        profile_image_url="https://deleted.com/deleted.jpg",
        tier_id=None,
        is_superuser=False,
        google_id=None,
        github_id=None,
        oauth_provider=None,
        email_verified=False,
        oauth_created_at=None,
        oauth_updated_at=None,
    )
    # anonymize the row, then soft-delete it
    await crud_users.update(db=db, object=anonymize_data, commit=False, id=user_id)
    await crud_users.delete(db=db, id=user_id)
```

Email is intentionally retained for legal compliance purposes (audit trail, "right to be forgotten" doesn't always apply if the platform is required to keep records).

## Administrative Operations

### List All Users

`GET /api/v1/users/` — superuser only, paginated.

```bash
curl "http://localhost:8000/api/v1/users/?page=1&items_per_page=10" \
  -b superuser_cookies.txt
```

Response shape (via `paginated_response`):

```json
{
  "data": [
    { "id": 1, "name": "Admin User", "username": "admin", "email": "admin@example.com", ... }
  ],
  "total_count": 42,
  "has_more": true,
  "page": 1,
  "items_per_page": 10
}
```

See [Pagination](../api/pagination.md) for the full pattern.

### View a User's Tier

```bash
curl http://localhost:8000/api/v1/users/john@example.com/tier \
  -H "Authorization: Bearer <access_token>"
```

Returns the user record joined with their tier. Permission: own profile or superuser.

### Change a User's Tier

`PATCH /api/v1/users/{username}/tier` — superuser only.

```bash
curl -X PATCH http://localhost:8000/api/v1/users/john@example.com/tier \
  -H "Authorization: Bearer <superuser_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"tier_id": 2}'
```

The service verifies the tier exists before assigning it.

### View a User's Rate Limits

```bash
curl http://localhost:8000/api/v1/users/johndoe/rate-limits -b cookies.txt
```

Returns the rate limits configured for the user's tier. Permission: own profile or superuser.

## User Model Reference

The actual model lives in `modules/user/models.py`. Trimmed:

```python
class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True,
        primary_key=True, init=False,
    )
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    profile_image_url: Mapped[str] = mapped_column(
        String, default="https://profileimageurl.com",
    )

    tier_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tiers.id"), index=True, default=None,
    )
    tier: Mapped["Tier | None"] = relationship(
        "Tier", back_populates="users", lazy="selectin", init=False,
    )

    is_superuser: Mapped[bool] = mapped_column(default=False)

    # OAuth (filled when user signs in via Google/GitHub)
    google_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, default=None)
    github_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, default=None)
    oauth_provider: Mapped[str | None] = mapped_column(String(20), default=None)
    email_verified: Mapped[bool] = mapped_column(default=False)

    @property
    def is_active(self) -> bool:
        # Derived, not stored. is_deleted stays the single source of truth.
        return not self.is_deleted
```

Mixins from `infrastructure/database/models`:

- `TimestampMixin` — `created_at`, `updated_at`
- `SoftDeleteMixin` — `is_deleted`, `deleted_at`

The `is_active` property is **derived** from `not is_deleted` — there's no separate column. `crudauth` reads it during login so a soft-deleted user can't authenticate; `is_deleted` remains the single source of truth.

Table name is **`user`** (singular).

## Common CRUD Tasks

The same FastCRUD operations described in [CRUD Operations](../database/crud.md) work on users:

```python
from src.modules.user.crud import crud_users

# Existence checks
await crud_users.exists(db=db, email="user@example.com")
await crud_users.exists(db=db, username="johndoe")

# Counts
total_active = await crud_users.count(db=db, is_deleted=False)
admin_count = await crud_users.count(db=db, is_superuser=True)

# Filtered queries
result = await crud_users.get_multi(db=db, tier_id=1, is_deleted=False, limit=20)

# Search by username substring
result = await crud_users.get_multi(db=db, username__icontains="ad")
```

## Frontend Integration

Store the access token according to your frontend threat model and explicitly attach it as a Bearer header:

```javascript
class UserClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
        this.accessToken = null;
        this.refreshToken = null;
    }

    async register(userData) {
        const res = await fetch(`${this.baseUrl}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        return await res.json();
    }

    async login(email, password) {
        const res = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ username: email, password }),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        const tokens = await res.json();
        this.accessToken = tokens.access_token;
        this.refreshToken = tokens.refresh_token;
        return tokens;
    }

    authHeaders() {
        return { Authorization: `Bearer ${this.accessToken}` };
    }

    async getProfile() {
        const res = await fetch(`${this.baseUrl}/users/me`, {
            headers: this.authHeaders(),
        });
        if (!res.ok) throw new Error('Failed to get profile');
        return await res.json();
    }

    async updateProfile(email, updates) {
        const res = await fetch(`${this.baseUrl}/users/${email}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...this.authHeaders(),
            },
            body: JSON.stringify(updates),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        return await res.json();
    }

    async deleteAccount(email) {
        const res = await fetch(`${this.baseUrl}/users/${email}`, {
            method: 'DELETE',
            headers: this.authHeaders(),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        this.accessToken = null;
        this.refreshToken = null;
        return await res.json();
    }

    async logout() {
        await fetch(`${this.baseUrl}/auth/logout`, {
            method: 'POST',
            headers: this.authHeaders(),
        });
        this.accessToken = null;
        this.refreshToken = null;
    }
}
```

The API does not use authentication cookies or `X-CSRF-Token`; every protected request must carry the access token explicitly.

## Security Considerations

### Server-side validation

All input validation runs server-side via Pydantic schemas. Client-side checks are nice for UX but don't replace server validation.

### Login lockout

The login endpoint is automatically throttled by `crudauth` — an escalating per-IP / per-identifier lockout that returns `429` with a `Retry-After` header.

### Generic auth error messages

`POST /api/v1/auth/login` returns "Incorrect username or password" for both wrong username and wrong password — never reveal which one was wrong.

### Soft delete for accounts

The default `DELETE /api/v1/users/{username}` is a soft delete. Hard deletion only for GDPR-style requests, with anonymization preserving FK integrity.

## Next Steps

1. **[Permissions](permissions.md)** — Role-based access control patterns
2. **[Bearer Tokens](sessions.md)** — Access, refresh, and revocation lifecycle
3. **[Production Guide](../production.md)** — Hardening checklist
