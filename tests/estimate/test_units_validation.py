import pytest
from pydantic import ValidationError
from backend.app.schemas.estimate import Material


def test_invalid_unit_price():
    with pytest.raises(ValidationError):
        Material(name='Wood', quantity=10, unit='pcs', unit_price=-5)


def test_invalid_unit():
    with pytest.raises(ValidationError):
        Material(name='Wood', quantity=10, unit='kg')


def test_valid_material():
    material = Material(name='Wood', quantity=10, unit='pcs', unit_price=5)
    assert material.unit_price == 5
    assert material.unit == 'pcs'


def test_negative_quantity():
    with pytest.raises(ValidationError):
        Material(name='Wood', quantity=-10, unit='pcs', unit_price=5)