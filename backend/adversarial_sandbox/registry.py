REGISTRY: dict[str, object] = {}


def register_attack(cls):
    instance = cls()
    if instance.id in REGISTRY:
        raise ValueError(f"Duplicate attack id: {instance.id!r}")
    REGISTRY[instance.id] = instance
    return cls


def list_attacks() -> list:
    return [REGISTRY[k] for k in sorted(REGISTRY)]


def get_attack(attack_id: str):
    return REGISTRY[attack_id]
