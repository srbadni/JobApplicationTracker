"""job-tracker — root Typer application and entry point.

Mounts in-tree command sub-apps and discovers third-party plugins.
The shipped console script (``[project.scripts] job-tracker``) targets
``app`` directly.
"""

from __future__ import annotations

import typer

from . import plugins as _plugins
from .commands import deploy as _deploy_cmd
from .commands import env as _env_cmd

app = typer.Typer(
    name="job-tracker",
    help="job-tracker command-line tool.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

# In-tree commands. Mounted before plugin discovery so a plugin can't
# silently shadow a built-in by registering the same name.
app.add_typer(_deploy_cmd.app, name="deploy", help="Generate deployment artifacts (Dockerfile, compose, nginx config).")
app.add_typer(_env_cmd.app, name="env", help="Inspect and prepare the runtime environment.")


def _mount_command_plugins() -> None:
    """Mount external Typer sub-apps registered under ``job_tracker.commands``."""
    builtin_names = {"deploy", "env", "feature"}
    for name, sub_app in _plugins.discover_command_plugins().items():
        if name in builtin_names:
            typer.secho(
                f"warning: plugin command '{name}' shadows a built-in; ignoring.",
                fg=typer.colors.YELLOW,
                err=True,
            )
            continue
        app.add_typer(sub_app, name=name)


_mount_command_plugins()


@app.callback()
def _root() -> None:
    """job-tracker — job-tracker command-line tool."""
    # Typer uses this docstring as the root help text. The body is
    # intentionally empty: the callback exists so options like
    # ``--install-completion`` work without arguments.


if __name__ == "__main__":  # pragma: no cover
    app()
