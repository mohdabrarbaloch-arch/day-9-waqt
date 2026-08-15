"""Tests for calculation-method presets."""

from app.services.methods import DEFAULT_METHOD_ID, METHODS, get_method


def test_default_method_is_karachi():
    assert DEFAULT_METHOD_ID == 1
    assert METHODS[1].name == "University of Karachi"


def test_all_methods_valid():
    for m in METHODS.values():
        assert 0 < m.fajr_angle <= 25
        assert 0 <= m.isha_angle <= 25 or m.isha_interval is not None
        assert m.asr_factor in (1, 2)


def test_get_method_fallback():
    assert get_method(999).id == DEFAULT_METHOD_ID


def test_ummalqura_uses_interval():
    m = METHODS[4]
    assert m.isha_angle == 0.0
    assert m.isha_interval == 90


def test_karachi_is_default():
    assert METHODS[DEFAULT_METHOD_ID].region == "PK/IN"
