import torch
import torch.nn as nn
from adversarial_sandbox.adapters.attacks_torch import cw_l2_targeted


def _toy_model():
    torch.manual_seed(0)
    return nn.Sequential(nn.Flatten(), nn.Linear(16, 3))


def test_cw_reaches_target_and_stays_in_range():
    model = _toy_model()
    torch.manual_seed(1)
    x = torch.rand(1, 1, 4, 4)
    clean_pred = int(model(x).argmax(dim=1).item())
    target = torch.tensor([(clean_pred + 1) % 3])  # a class other than the clean prediction

    x_adv = cw_l2_targeted(model, x, target, steps=300, c=1.0, lr=0.5)

    assert int(model(x_adv).argmax(dim=1).item()) == int(target.item())
    assert x_adv.shape == x.shape
    assert x_adv.min() >= 0.0 and x_adv.max() <= 1.0


def test_cw_perturbs_the_input():
    model = _toy_model()
    torch.manual_seed(2)
    x = torch.rand(1, 1, 4, 4)
    clean_pred = int(model(x).argmax(dim=1).item())
    target = torch.tensor([(clean_pred + 2) % 3])
    x_adv = cw_l2_targeted(model, x, target, steps=300, c=1.0, lr=0.05)
    assert (x_adv - x).abs().sum() > 0  # a real, nonzero perturbation
