# Architecture assessment

## Scope

This assessment treats the repository as an API foundation, not as a request to invent
new product behavior. The only domain route currently present is the companies
placeholder; its `200 null` response is preserved until a company-listing contract and
persistence behavior are explicitly agreed.

## Current fit for a real service

The feature-first layout is appropriate for the current codebase. Splitting this service
into controllers, repositories, services, domain entities, and infrastructure adapters
now would create abstractions without use cases to justify their boundaries. Router
composition, typed response schemas, centralized settings, and a single database session
dependency provide enough separation at this stage.

The runtime foundation now follows deployable-service conventions:

- configuration comes from process environment or an untracked local `.env`, rather
  than loading the example file as runtime configuration;
- database credentials and debug logging are configurable rather than hard-coded in the
  database module;
- the application has an explicit factory/composition root and disposes its connection
  pool on shutdown;
- settings validate and normalize the versioned route prefix;
- dependency and tool configuration are reproducible and test discovery is explicit.

## Boundaries to preserve

- HTTP parsing and response models belong in the owning feature.
- Database sessions are obtained through `db.get_db`; feature code must not construct
  engines or sessions.
- `common` is only for contracts used by more than one feature. Feature-specific models
  should not be moved there preemptively.
- `api/router.py` remains the versioned composition point. Business rules do not belong
  in it.
- Health is a liveness probe. A future readiness probe may check dependencies, but only
  when operations require that distinction.

## Decisions deferred until business behavior exists

The following are intentionally **not** implemented:

- company CRUD semantics, fields, validation, filtering, or pagination;
- ORM models, migrations, repositories, transaction policies, or a service layer;
- authentication, authorization, ownership, and tenant boundaries;
- a global response/error envelope beyond the existing success contract;
- queues, caching, observability vendors, containers, and deployment manifests.

Each of these requires a product or operational requirement. When the first real company
use case is specified, implement one vertical slice and introduce only the abstractions
that are shared by demonstrated use cases.

## Next product questions (not implementation tasks)

Before implementing the companies endpoint, establish:

1. whether a company is global data or belongs to a user;
2. the minimum identity and uniqueness rules (for example, display name versus domain);
3. whether deletion is allowed when applications reference a company;
4. expected list size and therefore whether pagination is part of the first contract;
5. the authentication boundary that determines who can read or mutate records.

These decisions prevent accidental schema and API commitments while keeping engineering
work aligned with the already-defined business scope.
