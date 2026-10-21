import pytest

from app.core.entropy import file_entropy
from simulator.attack_simulator import run


def test_refuses_folder_not_named_sandbox(tmp_path):
    with pytest.raises(SystemExit):
        run(tmp_path / "real_documents", count=3)


def test_simulated_attack_locks_files_with_high_entropy(tmp_path):
    sandbox = tmp_path / "sandbox"
    run(sandbox, count=5)
    locked = list(sandbox.glob("*.locked"))
    assert len(locked) == 5
    assert all(file_entropy(f) > 7.5 for f in locked)
    assert (sandbox / "README_DECRYPT.txt").exists()
    assert not list(sandbox.glob("file_*.txt"))



def test_can_run_twice_in_same_sandbox(tmp_path):
    sandbox = tmp_path / "sandbox"
    run(sandbox, count=5)
    run(sandbox, count=5)  # leftover .locked files must not break a second run
    assert len(list(sandbox.glob("*.locked"))) == 5
    
    