# Job Application Tracker API

A minimal FastAPI service for the Job Application Tracker project.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
```

The application reads `.env.example` by default, so creating `.env` is optional. If `.env` exists, its values override `.env.example`.

## Run

```bash
uvicorn main:app --reload
```

The health endpoint is available at:

```text
GET /api/v1/health
```

## Test

Tests live next to their related features instead of in a separate `tests` directory.

```bash
pytest
```

## Lint

```bash
ruff check .
```
