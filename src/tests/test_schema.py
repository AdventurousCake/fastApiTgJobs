from pydantic import ValidationError

from src.tests.gen_test_data import generate_model_vd


def test_valid_vd():
    s = generate_model_vd(dump=True, text_len=4096)
    assert s

def test_invalid_vd():
    try:
        s = generate_model_vd(dump=True, text_len=4097)
    except Exception as e:
        assert isinstance(e, ValidationError)