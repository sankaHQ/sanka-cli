from __future__ import annotations

import click

import sanka_cli.runtime as runtime
from sanka_cli.config import DEFAULT_BASE_URL
from sanka_cli.state import CLIState


@click.group()
def auth() -> None:
    """Authentication commands."""


@auth.command("login")
@click.option("--access-token", required=True, help="Developer API access token.")
@click.option(
    "--refresh-token",
    default=None,
    help="Deprecated legacy refresh token. V2 public API uses bearer tokens.",
)
@click.option("--profile", "profile_name", default=None, help="Profile name to save.")
@click.option("--base-url", default=None, help="API base URL to store for the profile.")
@click.pass_obj
def auth_login(
    state: CLIState,
    access_token: str,
    refresh_token: str | None,
    profile_name: str | None,
    base_url: str | None,
) -> None:
    resolved_profile_name = profile_name or state.profile or "default"
    resolved_base_url = (base_url or state.base_url or DEFAULT_BASE_URL).rstrip("/")
    runtime.upsert_profile(resolved_profile_name, base_url=resolved_base_url)
    try:
        runtime.store_tokens(
            resolved_profile_name,
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except runtime.CredentialStoreError as exc:
        raise click.ClickException(str(exc)) from exc
    runtime.emit_payload(
        {
            "message": "saved",
            "profile": resolved_profile_name,
            "base_url": resolved_base_url,
        },
        state,
    )


@auth.command("status")
@click.pass_obj
def auth_status(state: CLIState) -> None:
    try:
        resolved = runtime.resolve_runtime(
            profile_name=state.profile,
            base_url_override=state.base_url,
        )
    except runtime.CredentialStoreError as exc:
        raise click.ClickException(str(exc)) from exc
    payload = runtime.request_json(state, "GET", "/v2/public/auth/whoami")
    data = payload.get("data", payload)
    data["profile"] = resolved["profile_name"]
    data["base_url"] = resolved["base_url"]
    runtime.emit_payload(data, state)


@auth.command("logout")
@click.option("--profile", "profile_name", default=None, help="Profile name to clear.")
@click.pass_obj
def auth_logout(state: CLIState, profile_name: str | None) -> None:
    resolved_profile_name = profile_name or state.profile or "default"
    runtime.clear_tokens(resolved_profile_name)
    runtime.emit_payload(
        {
            "message": "logged_out",
            "profile": resolved_profile_name,
        },
        state,
    )
