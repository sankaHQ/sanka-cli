from __future__ import annotations

import os
import shutil
import subprocess

import click

# Top-level migration verbs delegated to sanka-migrate (the Sanka migration
# engine). Kept flat — the two command surfaces are disjoint by design, so
# `sanka scan` and `sanka companies list` coexist in one binary.
MIGRATION_COMMANDS: dict[str, str] = {
    "scan": "inspect a source application and write its semantic scan artifact",
    "plan": "inspect source/target and produce a reviewable plan",
    "validate": "validate sampled source records against the plan without writing",
    "apply": "execute the reviewed plan (resumable)",
    "verify": "verify the target against the source and ledger",
    "status": "show run status and ledger counts",
    "migrate": "plan + apply + verify in one go",
    "connect": "select a built-in provider and show its supported migration roles",
    "research": "query cited Sanka lifecycle, cost, and comparison research",
    "assess": "submit a free migration assessment",
}

INSTALL_HINT = (
    "Migration commands are provided by sanka-migrate. Install it with "
    "`uv tool install sanka-migrate`, then retry — sanka delegates to it "
    "automatically."
)


def _load_migrate_main():
    """Return sanka-migrate's CLI entry point when it shares this environment."""
    try:
        from sanka.cli import main
    except ImportError:
        return None
    return main


def register_migration_passthroughs(cli: click.Group) -> None:
    for name, help_text in MIGRATION_COMMANDS.items():
        cli.add_command(_build_passthrough(name, help_text))


def _build_passthrough(name: str, help_text: str) -> click.Command:
    @click.command(
        name,
        help=f"{help_text} (via sanka-migrate)",
        # Forward everything verbatim, including --help, so sanka-migrate
        # renders its own usage for its own commands.
        context_settings={
            "ignore_unknown_options": True,
            "allow_extra_args": True,
            "help_option_names": [],
        },
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def passthrough(args: tuple[str, ...]) -> None:
        argv = [name, *args]
        migrate_main = _load_migrate_main()
        if migrate_main is not None:
            raise SystemExit(migrate_main(argv))
        executable = shutil.which("sanka-migrate")
        if executable:
            if os.name == "nt":
                raise SystemExit(subprocess.call([executable, *argv]))
            os.execv(executable, [executable, *argv])
        raise click.ClickException(INSTALL_HINT)

    return passthrough
