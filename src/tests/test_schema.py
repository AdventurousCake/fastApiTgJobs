import pytest
from pydantic import ValidationError

from src.tests.gen_test_data import generate_fake_model_vd


def test_valid_vd():
    s = generate_fake_model_vd(dump=True, text_len=4096)
    assert s

def test_invalid_vd():
    with pytest.raises(ValidationError):
        s = generate_fake_model_vd(dump=True, text_len=4097)