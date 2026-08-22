"""Deprecated entry point directing callers to schema migrations."""

import sys


def main() -> None:
    """Prevent untracked schema creation alongside Alembic migrations."""
    print("This project manages its database schema with Alembic. Run `uv run alembic upgrade head` instead.")
    sys.exit(2)


if __name__ == "__main__":
    main()
