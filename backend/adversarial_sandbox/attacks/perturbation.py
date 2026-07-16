import torch
import torch.nn.functional as F
from ..registry import register_attack
from ..base import AttackModule
from ..schema import Knob, AttackDescription, RunResult, Figure, Metric, SweepSpec
from ..adapters import mnist
from ..adapters.attacks_torch import fgsm, pgd
from ..source import snippet


def _true_class_conf(model, x, true_label):
    with torch.no_grad():
        probs = F.softmax(model(x), dim=1)[0]
    return float(probs[true_label])


@register_attack
class PerturbationAttack(AttackModule):
    id = "perturbation"
    name = "Adversarial Perturbation (FGSM/PGD)"
    group = "Perturbation"

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group,
            summary=(
                "Evasion attacks add a tiny, near-invisible perturbation to an "
                "**input** so a trained model misclassifies it. FGSM takes one step "
                "along the sign of the loss gradient; PGD iterates."
            ),
            formula=r"x_{adv} = x + \epsilon\,\operatorname{sign}\!\big(\nabla_x\, \mathcal{L}(f(x), y)\big)",
            threat_model="Attacker has white-box access to gradients and can perturb "
                         "the test input within an L-inf budget epsilon.",
            code=[snippet(fgsm, "FGSM"), snippet(pgd, "PGD (iterated)")],
            knobs=[
                Knob(name="sample_index", label="Digit sample", type="slider",
                     min=0, max=9, step=1, default=0, help="Which held-out digit."),
                Knob(name="epsilon", label="Epsilon (L-inf budget)", type="slider",
                     min=0.0, max=0.3, step=0.01, default=0.15,
                     help="Perturbation size; larger = stronger but more visible."),
                Knob(name="mode", label="Attack", type="select",
                     options=["fgsm", "pgd"], default="fgsm",
                     help="Single-step (FGSM) vs iterative (PGD)."),
                Knob(name="pgd_steps", label="PGD steps", type="slider",
                     min=1, max=20, step=1, default=10,
                     help="Iterations (only used when Attack = pgd)."),
            ],
            sweep=SweepSpec(
                x_knob="epsilon",
                x_values=[0.0, 0.05, 0.1, 0.15, 0.2, 0.3],
                x_label="Epsilon (L-inf budget)",
                y_label="True-class confidence under attack",
                attacked_metric="Adversarial confidence",
                defended_metric="Adversarial confidence",
            ),
        )

    def _attack(self, model, x, y, p):
        if p["mode"] == "pgd":
            return pgd(model, x, y, p["epsilon"], steps=int(p["pgd_steps"]))
        return fgsm(model, x, y, p["epsilon"])

    def _evaluate(self, model_path, p, panel_title):
        model = mnist.load_model(model_path)
        xs, ys = mnist.load_samples()
        idx = int(p["sample_index"])
        x = xs[idx:idx + 1]
        y = ys[idx:idx + 1]
        true_label = int(y.item())

        x_adv = self._attack(model, x, y, p)
        clean_label, clean_pred_conf = mnist.predict(model, x)
        adv_label, adv_pred_conf = mnist.predict(model, x_adv)
        clean_conf = _true_class_conf(model, x, true_label)
        adv_conf = _true_class_conf(model, x_adv, true_label)

        fig = mnist.render_attack_figure(
            x, x_adv, (clean_label, clean_pred_conf), (adv_label, adv_pred_conf),
            p["mode"].upper(),
        )
        return true_label, clean_label, adv_label, clean_conf, adv_conf, fig, panel_title

    def run(self, params):
        p = self.clean_params(params)
        true_l, clean_l, adv_l, clean_c, adv_c, fig, _ = self._evaluate(
            mnist.STANDARD_PATH, p, "Standard model")
        return RunResult(
            figure=Figure(png_base64=fig, caption="Standard (undefended) model"),
            metrics=[
                Metric(label="Clean confidence", value=clean_c, display=f"{clean_c:.0%}"),
                Metric(label="Adversarial confidence", value=adv_c, display=f"{adv_c:.0%}"),
            ],
            narrative=(
                f"True digit {true_l}. Model saw {clean_l} on the clean image and "
                f"{adv_l} after the {p['mode'].upper()} attack "
                f"(confidence in the true class {clean_c:.0%} → {adv_c:.0%})."
            ),
        )

    def defend(self, params):
        p = self.clean_params(params)
        true_l, clean_l, adv_l, clean_c, adv_c, fig, _ = self._evaluate(
            mnist.ROBUST_PATH, p, "Adversarially-trained model")
        held = adv_l == true_l
        return RunResult(
            figure=Figure(png_base64=fig, caption="Adversarially-trained (robust) model"),
            metrics=[
                Metric(label="Clean confidence", value=clean_c, display=f"{clean_c:.0%}"),
                Metric(label="Adversarial confidence", value=adv_c, display=f"{adv_c:.0%}"),
            ],
            narrative=(
                f"The adversarially-trained model {'kept' if held else 'lost'} the "
                f"correct label {true_l} under the same {p['mode'].upper()} attack "
                f"(true-class confidence {adv_c:.0%})."
            ),
        )
