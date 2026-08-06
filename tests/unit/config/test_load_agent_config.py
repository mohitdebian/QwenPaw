# -*- coding: utf-8 -*-
"""Tests for load_agent_config error handling and robustness."""

from threading import Lock
import pytest

from qwenpaw.config import utils as config_utils
from qwenpaw.config.config import (
    AgentProfileRef,
    AgentsConfig,
    Config,
    ConfigurationException,
    load_agent_config,
)


def test_load_agent_config_invalid_json_raises_configuration_exception(
    tmp_path,
    monkeypatch,
):
    workspace_dir = tmp_path / "workspaces" / "test_agent"
    workspace_dir.mkdir(parents=True)
    agent_config_path = workspace_dir / "agent.json"
    agent_config_path.write_text("{corrupted_json: true,", encoding="utf-8")

    root_config = Config(
        agents=AgentsConfig(
            active_agent="test_agent",
            profiles={
                "test_agent": AgentProfileRef(
                    id="test_agent",
                    workspace_dir=str(workspace_dir),
                ),
            },
        ),
    )
    monkeypatch.setattr(config_utils, "load_config", lambda: root_config)
    monkeypatch.setattr(config_utils, "_agent_config_cache", {})
    monkeypatch.setattr(config_utils, "_agent_config_lock", Lock())

    with pytest.raises(ConfigurationException) as exc_info:
        load_agent_config("test_agent")

    assert "invalid JSON" in str(exc_info.value)
    assert str(agent_config_path) in str(exc_info.value)


def test_load_agent_config_corrupted_utf8_raises_configuration_exception(
    tmp_path,
    monkeypatch,
):
    workspace_dir = tmp_path / "workspaces" / "test_agent"
    workspace_dir.mkdir(parents=True)
    agent_config_path = workspace_dir / "agent.json"
    agent_config_path.write_bytes(b"\x80\x81\x82\xff")

    root_config = Config(
        agents=AgentsConfig(
            active_agent="test_agent",
            profiles={
                "test_agent": AgentProfileRef(
                    id="test_agent",
                    workspace_dir=str(workspace_dir),
                ),
            },
        ),
    )
    monkeypatch.setattr(config_utils, "load_config", lambda: root_config)
    monkeypatch.setattr(config_utils, "_agent_config_cache", {})
    monkeypatch.setattr(config_utils, "_agent_config_lock", Lock())

    with pytest.raises(ConfigurationException) as exc_info:
        load_agent_config("test_agent")

    assert "invalid UTF-8 encoding" in str(exc_info.value)
    assert str(agent_config_path) in str(exc_info.value)
