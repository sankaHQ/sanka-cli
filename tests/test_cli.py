from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from sanka_cli import config as cli_config
from sanka_cli.main import cli


class _FakeKeyring:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self.values.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self.values[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        self.values.pop((service, username), None)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fake_keyring(monkeypatch) -> _FakeKeyring:
    from sanka_cli import config as cli_config

    keyring = _FakeKeyring()
    monkeypatch.setattr(cli_config, "keyring", keyring)
    return keyring


def test_auth_login_status_and_logout(
    runner: CliRunner,
    fake_keyring: _FakeKeyring,
    monkeypatch,
    tmp_path,
) -> None:
    env = {"XDG_CONFIG_HOME": str(tmp_path)}

    login_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "auth",
            "login",
            "--access-token",
            "access-1",
            "--refresh-token",
            "refresh-1",
            "--base-url",
            "https://cli.example.com",
        ],
        env=env,
    )
    assert login_result.exit_code == 0, login_result.output
    assert fake_keyring.values[("sanka-cli", "default:access_token")] == "access-1"
    assert fake_keyring.values[("sanka-cli", "default:refresh_token")] == "refresh-1"

    monkeypatch.setattr(
        "sanka_cli.runtime.request_json",
        lambda *_args, **_kwargs: {
            "data": {
                "auth_mode": "developer_api_token",
                "token_name": "CLI",
            }
        },
    )
    status_result = runner.invoke(
        cli,
        ["--output", "json", "auth", "status"],
        env=env,
    )
    assert status_result.exit_code == 0, status_result.output
    status_payload = json.loads(status_result.output)
    assert status_payload["auth_mode"] == "developer_api_token"
    assert status_payload["profile"] == "default"
    assert status_payload["base_url"] == "https://cli.example.com"

    logout_result = runner.invoke(
        cli,
        ["--output", "json", "auth", "logout"],
        env=env,
    )
    assert logout_result.exit_code == 0, logout_result.output
    assert ("sanka-cli", "default:access_token") not in fake_keyring.values
    assert ("sanka-cli", "default:refresh_token") not in fake_keyring.values


def test_resolve_runtime_prefers_env_access_token_without_keyring(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("SANKA_ACCESS_TOKEN", "env-access")

    def _unexpected_get_tokens(profile_name: str) -> dict[str, str | None]:
        raise AssertionError(f"get_tokens should not run for {profile_name}")

    monkeypatch.setattr(cli_config, "get_tokens", _unexpected_get_tokens)
    resolved = cli_config.resolve_runtime()
    assert resolved["access_token"] == "env-access"
    assert resolved["refresh_token"] is None
    assert resolved["token_source"] == "env"


def test_auth_status_surfaces_keychain_error_cleanly(
    runner: CliRunner,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "sanka_cli.runtime.resolve_runtime",
        lambda **_kwargs: (_ for _ in ()).throw(
            cli_config.CredentialStoreError("Keychain access is blocked")
        ),
    )

    result = runner.invoke(cli, ["auth", "status"])
    assert result.exit_code == 1
    assert "Keychain access is blocked" in result.output


def test_profiles_list_and_use(
    runner: CliRunner,
    fake_keyring: _FakeKeyring,
    tmp_path,
) -> None:
    _ = fake_keyring
    env = {"XDG_CONFIG_HOME": str(tmp_path)}

    result_default = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "auth",
            "login",
            "--access-token",
            "access-default",
        ],
        env=env,
    )
    assert result_default.exit_code == 0, result_default.output

    result_prod = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "auth",
            "login",
            "--profile",
            "prod",
            "--access-token",
            "access-prod",
            "--refresh-token",
            "refresh-prod",
            "--base-url",
            "https://prod.example.com",
        ],
        env=env,
    )
    assert result_prod.exit_code == 0, result_prod.output

    list_result = runner.invoke(
        cli,
        ["--output", "json", "profiles", "list"],
        env=env,
    )
    assert list_result.exit_code == 0, list_result.output
    profiles_payload = json.loads(list_result.output)["data"]
    assert {row["name"] for row in profiles_payload} == {"default", "prod"}

    use_result = runner.invoke(
        cli,
        ["--output", "json", "profiles", "use", "prod"],
        env=env,
    )
    assert use_result.exit_code == 0, use_result.output
    use_payload = json.loads(use_result.output)
    assert use_payload["active_profile"] == "prod"


@pytest.mark.parametrize(
    (
        "resource",
        "command_args",
        "expected_method",
        "expected_path",
        "expected_params",
        "expected_json",
    ),
    [
        (
            "companies",
            ["list", "--page", "2", "--limit", "10"],
            "GET",
            "/v2/public/companies",
            {"page": 2, "limit": 10},
            None,
        ),
        (
            "companies",
            ["get", "company-1", "--external-id", "COMP-1"],
            "GET",
            "/v2/public/companies/company-1",
            {"external_id": "COMP-1"},
            None,
        ),
        (
            "companies",
            ["create", "--data", '{"name":"Acme"}'],
            "POST",
            "/v2/public/companies",
            None,
            {"name": "Acme"},
        ),
        (
            "companies",
            [
                "update",
                "company-1",
                "--data",
                '{"name":"Acme 2"}',
                "--external-id",
                "COMP-1",
            ],
            "PUT",
            "/v2/public/companies/company-1",
            {"external_id": "COMP-1"},
            {"name": "Acme 2"},
        ),
        (
            "companies",
            ["delete", "company-1", "--external-id", "COMP-1"],
            "DELETE",
            "/v2/public/companies/company-1",
            {"external_id": "COMP-1"},
            None,
        ),
        (
            "contacts",
            ["list"],
            "GET",
            "/v2/public/contacts",
            {"page": 1, "limit": 50},
            None,
        ),
        (
            "contacts",
            ["get", "contact-1"],
            "GET",
            "/v2/public/contacts/contact-1",
            None,
            None,
        ),
        (
            "contacts",
            ["create", "--data", '{"first_name":"Ada"}'],
            "POST",
            "/v2/public/contacts",
            None,
            {"first_name": "Ada"},
        ),
        (
            "contacts",
            ["update", "contact-1", "--data", '{"first_name":"Ada 2"}'],
            "PUT",
            "/v2/public/contacts/contact-1",
            None,
            {"first_name": "Ada 2"},
        ),
        (
            "contacts",
            ["delete", "contact-1"],
            "DELETE",
            "/v2/public/contacts/contact-1",
            None,
            None,
        ),
        ("deals", ["list"], "GET", "/v2/public/deals", {"page": 1, "limit": 50}, None),
        ("deals", ["get", "deal-1"], "GET", "/v2/public/deals/deal-1", None, None),
        (
            "deals",
            ["create", "--data", '{"title":"Deal"}'],
            "POST",
            "/v2/public/deals",
            None,
            {"title": "Deal"},
        ),
        (
            "deals",
            ["update", "deal-1", "--data", '{"title":"Deal 2"}'],
            "PUT",
            "/v2/public/deals/deal-1",
            None,
            {"title": "Deal 2"},
        ),
        (
            "deals",
            ["delete", "deal-1"],
            "DELETE",
            "/v2/public/deals/deal-1",
            None,
            None,
        ),
        (
            "tickets",
            ["list"],
            "GET",
            "/v2/public/tickets",
            {"page": 1, "limit": 50},
            None,
        ),
        (
            "tickets",
            ["get", "ticket-1"],
            "GET",
            "/v2/public/tickets/ticket-1",
            None,
            None,
        ),
        (
            "tickets",
            ["create", "--data", '{"external_id":"T-1","title":"Ticket"}'],
            "POST",
            "/v2/public/tickets",
            None,
            {"external_id": "T-1", "title": "Ticket"},
        ),
        (
            "tickets",
            ["update", "ticket-1", "--data", '{"title":"Ticket 2"}'],
            "PUT",
            "/v2/public/tickets/ticket-1",
            None,
            {"title": "Ticket 2"},
        ),
        (
            "tickets",
            ["delete", "ticket-1"],
            "DELETE",
            "/v2/public/tickets/ticket-1",
            None,
            None,
        ),
    ],
)
def test_resource_commands_route_expected_requests(
    runner: CliRunner,
    monkeypatch,
    resource: str,
    command_args: list[str],
    expected_method: str,
    expected_path: str,
    expected_params: dict | None,
    expected_json: dict | None,
) -> None:
    captured: dict[str, object] = {}

    def _fake_request(_state, method, path, *, params=None, json_body=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json_body"] = json_body
        return {"ok": True}

    monkeypatch.setattr("sanka_cli.runtime.request_json", _fake_request)
    result = runner.invoke(
        cli,
        ["--output", "json", resource, *command_args],
    )

    assert result.exit_code == 0, result.output
    assert captured == {
        "method": expected_method,
        "path": expected_path,
        "params": expected_params,
        "json_body": expected_json,
    }


def test_workflow_commands_route_expected_requests_and_wait(
    runner: CliRunner,
    monkeypatch,
) -> None:
    calls: list[tuple[str, str]] = []
    responses = [
        {"data": {"run_id": "run-1", "status": "running"}},
        {"data": {"run_id": "run-1", "status": "running"}},
        {"data": {"run_id": "run-1", "status": "success"}},
    ]

    def _fake_request(_state, method, path, *, params=None, json_body=None):
        del params, json_body
        calls.append((method, path))
        if path == "/v2/public/workflows":
            return {"ok": True}
        return responses.pop(0)

    monkeypatch.setattr("sanka_cli.runtime.request_json", _fake_request)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    create_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "workflows",
            "create",
            "--data",
            '{"external_id":"WF-1","name":"Workflow"}',
        ],
    )
    assert create_result.exit_code == 0, create_result.output

    update_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "workflows",
            "update",
            "--data",
            '{"external_id":"WF-1","name":"Workflow 2"}',
        ],
    )
    assert update_result.exit_code == 0, update_result.output

    run_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "workflows",
            "run",
            "WF-1",
            "--wait",
            "--poll-interval",
            "0.01",
            "--timeout",
            "1",
        ],
    )
    assert run_result.exit_code == 0, run_result.output
    assert calls == [
        ("POST", "/v2/public/workflows"),
        ("POST", "/v2/public/workflows"),
        ("POST", "/v2/public/workflows/WF-1/run"),
        ("GET", "/v2/public/workflow-runs/run-1"),
        ("GET", "/v2/public/workflow-runs/run-1"),
    ]


@pytest.mark.parametrize(
    ("command_args", "expected_body"),
    [
        (
            ["ai", "score", "company", "company-1"],
            {"object_type": "company", "record_id": "company-1"},
        ),
        (
            ["ai", "score", "deal", "deal-1", "--score-model-id", "model-1"],
            {"object_type": "deal", "record_id": "deal-1", "score_model_id": "model-1"},
        ),
    ],
)
def test_ai_score_commands_build_payloads(
    runner: CliRunner,
    monkeypatch,
    command_args: list[str],
    expected_body: dict,
) -> None:
    captured: dict[str, object] = {}

    def _fake_request(_state, method, path, *, params=None, json_body=None):
        del params
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = json_body
        return {"ok": True}

    monkeypatch.setattr("sanka_cli.runtime.request_json", _fake_request)
    result = runner.invoke(cli, ["--output", "json", *command_args])

    assert result.exit_code == 0, result.output
    assert captured == {
        "method": "POST",
        "path": "/v2/score",
        "json_body": expected_body,
    }


def test_ai_enrich_company_builds_record_and_seed_payloads(
    runner: CliRunner,
    monkeypatch,
    tmp_path,
) -> None:
    custom_field_map_path = tmp_path / "custom-field-map.json"
    custom_field_map_path.write_text('{"segment":"field_1"}', encoding="utf-8")
    captured_bodies: list[dict] = []

    def _fake_request(_state, method, path, *, params=None, json_body=None):
        del params
        assert method == "POST"
        assert path == "/v2/enrich"
        captured_bodies.append(json_body or {})
        return {"ok": True}

    monkeypatch.setattr("sanka_cli.runtime.request_json", _fake_request)

    record_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "ai",
            "enrich",
            "company",
            "company-1",
            "--force-refresh",
            "--custom-field-map",
            f"@{custom_field_map_path}",
        ],
    )
    assert record_result.exit_code == 0, record_result.output

    seed_result = runner.invoke(
        cli,
        [
            "--output",
            "json",
            "ai",
            "enrich",
            "company",
            "--seed-name",
            "Acme",
            "--seed-url",
            "https://acme.example.com",
            "--seed-external-id",
            "seed-1",
            "--dry-run",
        ],
    )
    assert seed_result.exit_code == 0, seed_result.output

    assert captured_bodies == [
        {
            "object_type": "company",
            "dry_run": False,
            "force_refresh": True,
            "record_id": "company-1",
            "custom_field_map": {"segment": "field_1"},
        },
        {
            "object_type": "company",
            "dry_run": True,
            "force_refresh": False,
            "seed": {
                "name": "Acme",
                "url": "https://acme.example.com",
                "external_id": "seed-1",
            },
        },
    ]
