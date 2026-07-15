import torch
import torch.nn as nn
import torch.nn.functional as F
from adversarial_sandbox.adapters.attacks_torch import fgsm, pgd


def _toy_model():
    torch.manual_seed(0)
    model = nn.Sequential(nn.Flatten(), nn.Linear(16, 2))
    return model


def _batch():
    torch.manual_seed(1)
    x = torch.rand(8, 1, 4, 4)
    y = torch.randint(0, 2, (8,))
    return x, y


def test_fgsm_increases_loss_and_bounded():
    model, (x, y) = _toy_model(), _batch()
    x_adv = fgsm(model, x, y, epsilon=0.1)
    clean = F.cross_entropy(model(x), y)
    adv = F.cross_entropy(model(x_adv), y)
    assert adv > clean
    assert (x_adv - x).abs().max() <= 0.1 + 1e-6
    assert x_adv.min() >= 0 and x_adv.max() <= 1


def test_pgd_stronger_than_fgsm_and_bounded():
    model, (x, y) = _toy_model(), _batch()
    adv_fgsm = F.cross_entropy(model(fgsm(model, x, y, 0.1)), y)
    adv_pgd = F.cross_entropy(model(pgd(model, x, y, 0.1, steps=10)), y)
    assert adv_pgd >= adv_fgsm
    x_adv = pgd(model, x, y, 0.1, steps=10)
    assert (x_adv - x).abs().max() <= 0.1 + 1e-6
