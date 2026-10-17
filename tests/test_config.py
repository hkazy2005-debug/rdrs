from app.core.config import load_settings


def test_project_config_loads():
    s = load_settings("config.yaml")
    assert s.response.simulation_mode is True
    assert s.scoring.weights.rapid_encryption == 40
    assert s.scoring.levels.critical == 70


def test_missing_file_uses_safe_defaults(tmp_path):
    s = load_settings(tmp_path / "missing.yaml")
    assert s.response.simulation_mode is True
    assert s.response.terminate_process is False

    

    