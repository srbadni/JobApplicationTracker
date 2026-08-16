"""job-tracker — the job-tracker command-line tool.

The CLI is a Typer application with two extension points:

- `job_tracker.commands` entry-point group: third-party packages can register
  top-level Typer sub-apps that mount under `job-tracker <name>`.
- `job_tracker.features` entry-point group: third-party packages can register
  ``Feature`` instances that ``job-tracker feature`` can list, install, and remove.

In-tree commands and features live alongside this package and follow
the same contracts as plugins.
"""
