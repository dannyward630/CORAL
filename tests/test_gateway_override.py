"""Tests for gateway URL environment overrides."""

import logging

import pytest

from coral.workspace.repo import _set_gateway_base_url


@pytest.mark.parametrize(
    ("inherited_url", "should_warn"),
    [
        (None, False),
        ("https://gateway.example/v1", False),
        ("https://inherited.example/v1", True),
    ],
    ids=["absent", "matching", "conflicting"],
)
def test_gateway_override_warns_only_for_conflicting_inherited_url(
    inherited_url: str | None,
    should_warn: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    env = {} if inherited_url is None else {"ANTHROPIC_BASE_URL": inherited_url}
    gateway_url = "https://gateway.example/v1"

    with caplog.at_level(logging.WARNING, logger="coral.workspace.repo"):
        _set_gateway_base_url(
            env,
            "ANTHROPIC_BASE_URL",
            gateway_url,
            context="Claude Code settings",
        )

    assert env["ANTHROPIC_BASE_URL"] == gateway_url
    if should_warn:
        assert "Claude Code settings" in caplog.text
        assert "ANTHROPIC_BASE_URL" in caplog.text
        assert "overrides a pre-existing" in caplog.text
        assert inherited_url not in caplog.text
        assert gateway_url not in caplog.text
    else:
        assert not caplog.records
