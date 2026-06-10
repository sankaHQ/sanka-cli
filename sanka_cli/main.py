from __future__ import annotations

import click

from sanka_cli.commands.ai import ai
from sanka_cli.commands.auth import auth
from sanka_cli.commands.profiles import profiles
from sanka_cli.commands.resources import attach_resource_group
from sanka_cli.commands.workflows import workflows
from sanka_cli.output import print_error
from sanka_cli.state import CLIState


@click.group()
@click.option("--profile", default=None, help="Profile name to use.")
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--output",
    type=click.Choice(["table", "json"]),
    default=None,
    help="Output format. Defaults to table on TTY and JSON otherwise.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    profile: str | None,
    base_url: str | None,
    output: str | None,
) -> None:
    ctx.obj = CLIState(profile=profile, base_url=base_url, output=output)


cli.add_command(auth)
cli.add_command(profiles)
cli.add_command(workflows)
cli.add_command(ai)

attach_resource_group(cli, "companies", "/v2/public/companies")
attach_resource_group(cli, "contacts", "/v2/public/contacts")
attach_resource_group(cli, "deals", "/v2/public/deals")
attach_resource_group(cli, "tickets", "/v2/public/tickets")


def main() -> None:
    try:
        cli(standalone_mode=False)
    except click.ClickException as exc:
        print_error(f"Error: {exc.format_message()}")
        raise SystemExit(exc.exit_code) from exc
