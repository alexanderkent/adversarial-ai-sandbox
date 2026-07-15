import torch
import torch.nn.functional as F


def fgsm(model, x, y, epsilon):
    x = x.clone().detach().requires_grad_(True)
    loss = F.cross_entropy(model(x), y)
    model.zero_grad(set_to_none=True)
    loss.backward()
    x_adv = x + epsilon * x.grad.sign()
    return x_adv.clamp(0, 1).detach()


def pgd(model, x, y, epsilon, steps=10, alpha=None):
    if alpha is None:
        alpha = 2.5 * epsilon / max(steps, 1)
    x_orig = x.clone().detach()
    x_adv = x_orig.clone().detach()
    for _ in range(steps):
        x_adv.requires_grad_(True)
        loss = F.cross_entropy(model(x_adv), y)
        model.zero_grad(set_to_none=True)
        loss.backward()
        with torch.no_grad():
            x_adv = x_adv + alpha * x_adv.grad.sign()
            x_adv = x_orig + torch.clamp(x_adv - x_orig, -epsilon, epsilon)
            x_adv = x_adv.clamp(0, 1)
        x_adv = x_adv.detach()
    return x_adv
