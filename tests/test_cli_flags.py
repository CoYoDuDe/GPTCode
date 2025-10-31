import importlib.util
from pathlib import Path


def load_gptcode_module():
    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("gptcode", root / "gptcode.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


gptcode = load_gptcode_module()


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
