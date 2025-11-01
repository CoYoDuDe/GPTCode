import importlib.util
from pathlib import Path

import pytest


def load_gptcode_module():
    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("gptcode", root / "gptcode.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


gptcode = load_gptcode_module()


class DummyResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_parse_cli_args_supports_overrides():
    args = gptcode.parse_cli_args([
        "--headless",
        "--auto",
        "--goal",
        "Do stuff",
        "--model",
        "gpt-test",
        "--dryrun",
        "on",
    ])
    assert args.headless is True
    assert args.auto is True
    assert args.goal == "Do stuff"
    assert args.model == "gpt-test"
    assert args.dryrun == "on"


def test_determine_session_settings_override_priority():
    cfg = {"model": "cfg-model", "dryrun": False}
    model, dryrun = gptcode.determine_session_settings(cfg, model_override="override", dryrun_override=True)
    assert model == "override"
    assert dryrun is True


def test_determine_session_settings_defaults():
    cfg = {}
    model, dryrun = gptcode.determine_session_settings(cfg)
    assert model == gptcode.DEFAULT_MODEL
    assert dryrun is False


@pytest.mark.parametrize(
    "scenario",
    (
        "plugin",
        "legacy",
    ),
)
def test_docker_compose_resolves_variants(monkeypatch, scenario):
    monkeypatch.delenv("GPTCODE_DOCKER_COMPOSE_LEGACY", raising=False)
    gptcode._DOCKER_COMPOSE_CMD = None
    calls = []

    def fake_run(cmd, stdout=None, stderr=None, text=None, **kwargs):
        calls.append(cmd)
        if scenario == "plugin" and len(cmd) >= 3 and cmd[:3] == ["docker", "compose", "version"]:
            return DummyResult(returncode=0, stdout="Docker Compose version v2.24.0", stderr="")
        return DummyResult(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(gptcode.subprocess, "run", fake_run)

    if scenario == "plugin":
        monkeypatch.setattr(gptcode.shutil, "which", lambda name: None)
        result = gptcode.docker_compose("logs", "web")
        assert calls[0][:3] == ["docker", "compose", "version"]
        assert calls[1][:2] == ["docker", "compose"]
    else:
        candidate = "/usr/local/bin/docker-compose"
        monkeypatch.setenv("GPTCODE_DOCKER_COMPOSE_LEGACY", candidate)

        def fake_which(name):
            return candidate if name == candidate else None

        monkeypatch.setattr(gptcode.shutil, "which", fake_which)
        result = gptcode.docker_compose("up", "web")
        assert len(calls) == 1
        assert calls[0][0] == candidate
        assert "up" in calls[0]

    assert "[docker] rc=0" in result
