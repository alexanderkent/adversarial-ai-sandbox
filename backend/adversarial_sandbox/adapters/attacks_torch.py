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


def cw_l2_targeted(model, x, target, steps=100, confidence=0.0, c=1.0, lr=0.01):
    """Targeted Carlini-Wagner L2 attack. Finds a small-L2 perturbation that makes
    `model` classify each input in `x` (a [B,1,H,W] batch in [0,1]) as `target`
    (a [B] long tensor). Uses the tanh change of variables so the adversarial image
    stays in [0,1], Adam over the latent, and the C&W margin objective with
    confidence `kappa`. Returns, per sample, the lowest-L2 perturbation that reached
    the target, or the final iterate if the target was never reached."""
    x = x.clone().detach()
    target = target.clone().detach()
    n_classes = model(x).shape[1]

    x_clamped = x.clamp(1e-6, 1 - 1e-6)
    w = torch.atanh(2 * x_clamped - 1).detach().requires_grad_(True)
    optimizer = torch.optim.Adam([w], lr=lr)

    onehot = F.one_hot(target, n_classes).bool()
    best_adv = x.clone().detach()
    best_l2 = torch.full((x.shape[0],), float("inf"), device=x.device)
    final_adv = x.clone().detach()

    for _ in range(steps):
        x_adv = 0.5 * (torch.tanh(w) + 1)
        logits = model(x_adv)
        target_logit = logits[onehot]
        other_max = logits.masked_fill(onehot, float("-inf")).max(dim=1).values
        f = torch.clamp(other_max - target_logit + confidence, min=0.0)
        l2 = ((x_adv - x) ** 2).flatten(1).sum(dim=1)
        loss = (l2 + c * f).sum()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            final_adv = x_adv.detach()
            # reuse the logits already computed for this x_adv (the model is in
            # eval mode with no stochastic layers, so a second forward is redundant).
            reached = logits.detach().argmax(dim=1) == target
            improved = reached & (l2.detach() < best_l2)
            for i in range(x.shape[0]):
                if improved[i]:
                    best_l2[i] = l2[i].detach()
                    best_adv[i] = final_adv[i]

    for i in range(x.shape[0]):
        if torch.isinf(best_l2[i]):
            best_adv[i] = final_adv[i]
    return best_adv
