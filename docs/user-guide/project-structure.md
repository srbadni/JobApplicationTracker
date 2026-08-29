# Clean Architecture

The backend uses Clean Architecture. Source dependencies point toward business rules; the domain does not know FastAPI, SQLAlchemy, Pydantic, Redis, or any delivery mechanism.

```text
backend/src/
├── domain/                         # Enterprise entities and domain errors
├── use_cases/                      # Application rules and ports (Protocols)
├── interface_adapters/
│   ├── api/                        # HTTP router/controller composition
│   ├── admin/                      # SQLAdmin controllers
│   ├── repositories/               # Port implementations and data mapping
│   └── modules/                    # HTTP schemas, controllers, ORM records
└── frameworks/                     # FastAPI, SQLAlchemy, storage, cache, queues
```

## Dependency rule

The permitted direction is:

```text
frameworks & drivers → interface adapters → use cases → domain
```

- **Domain** contains plain Python entities, value objects, policies, and domain exceptions. It imports no outer layer.
- **Use cases** coordinate domain behavior. Database and external-service requirements are declared as `Protocol` ports here, not as SQLAlchemy sessions.
- **Interface adapters** translate HTTP requests and persistence records to and from use-case/domain values. FastAPI controllers and SQLAlchemy repository adapters belong here.
- **Frameworks and drivers** contain replaceable technical details and the composition root: application setup, database sessions, authentication, cache, storage, rate limiting, and Taskiq.

The company lookup is the reference implementation: `domain/company` defines the entity, `use_cases/company/get_company.py` owns the input use case and output port, `interface_adapters/repositories/company.py` implements that port, and the company dependency module wires it into the HTTP controller.

## Adding a feature

1. Model business vocabulary in `domain/<feature>/` using standard-library Python only.
2. Add interactors and required output ports in `use_cases/<feature>/`.
3. Implement repository/gateway ports in `interface_adapters/repositories/`.
4. Put request/response schemas and controllers in `interface_adapters/modules/<feature>/`.
5. Wire concrete adapters at a FastAPI dependency/composition point.
6. Put only reusable technology details in `frameworks/`.

Never import `interface_adapters` or `frameworks` from `domain` or `use_cases`. Pass dependencies through constructors and translate framework records at adapter boundaries.

## Running the application

From `backend/`:

```bash
uv run fastapi dev src/interface_adapters/main.py
```

Database migrations remain in `backend/migrations/`; operational scripts remain in `backend/scripts/`.
