import logging
import click
import sys

from meltano.core.project import Project, ProjectNotFound
from meltano.core.permissions import grant_permissions, SpecLoadingError
from meltano.core.tracking import GoogleAnalyticsTracker
from . import cli


@cli.group()
def permissions():
    """Database permission related commands."""
    pass


@permissions.command()
@click.argument("spec")
@click.option(
    "--db",
    help="The type of the target DB the specifications file is for.",
    type=click.Choice(["postgres", "snowflake"]),
    required=True,
)
@click.option("--dry", help="Do not actually run, just check.", is_flag=True)
def grant(db, spec, dry):
    """Grant the permissions provided in the provided specification file."""
    try:
        if not dry:
            click.secho("Error: Only dry runs are supported at the moment", fg="red")
            sys.exit(1)

        sql_commands = grant_permissions(db, spec, dry_run=dry)

        try:
            project = Project.find()
            tracker = GoogleAnalyticsTracker(project)
            tracker.track_meltano_permissions_grant(db=db, dry=dry)
        except ProjectNotFound as e:
            pass

        click.secho()
        click.secho("SQL Commands generated for given spec file:")

        for command in sql_commands:
            if command["already_granted"]:
                fg = "cyan"
            else:
                fg = "green"

            click.secho(f"{command['sql']};", fg=fg)
            click.secho()
    except SpecLoadingError as exc:
        for line in str(exc).splitlines():
            click.secho(line, fg="red")
        sys.exit(1)
