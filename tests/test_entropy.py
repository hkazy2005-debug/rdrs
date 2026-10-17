import os

from app.core.entropy import file_entropy, shannon_entropy


def test_empty_data_is_zero():
    assert shannon_entropy(b"") == 0.0


def test_text_has_low_entropy():
    text = b"the quick brown fox jumps over the lazy dog " * 50
    assert 0 < shannon_entropy(text) < 5


def test_random_bytes_near_eight():
    assert shannon_entropy(os.urandom(65536)) > 7.9


def test_same_byte_repeated_is_zero():
    assert shannon_entropy(b"\x00" * 1000) == 0.0


def test_file_entropy_of_random_file(tmp_path):
    f = tmp_path / "enc.bin"
    f.write_bytes(os.urandom(20000))
    assert file_entropy(f) > 7.5


def test_missing_file_is_zero(tmp_path):
    assert file_entropy(tmp_path / "nope.txt") == 0.0

    