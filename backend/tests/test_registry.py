import pytest
from adversarial_sandbox import registry


@pytest.fixture(autouse=True)
def clean_registry():
    saved = dict(registry.REGISTRY)
    registry.REGISTRY.clear()
    yield
    registry.REGISTRY.clear()
    registry.REGISTRY.update(saved)


def test_register_and_get():
    @registry.register_attack
    class Dummy:
        id = "dummy"

    assert registry.get_attack("dummy").id == "dummy"
    assert [m.id for m in registry.list_attacks()] == ["dummy"]


def test_duplicate_id_raises():
    @registry.register_attack
    class A:
        id = "same"

    with pytest.raises(ValueError):
        @registry.register_attack
        class B:
            id = "same"


def test_missing_id_raises_keyerror():
    with pytest.raises(KeyError):
        registry.get_attack("nope")
