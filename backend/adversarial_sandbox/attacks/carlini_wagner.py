import torch
import torch.nn.functional as F
from ..registry import register_attack
from ..base import AttackModule
from ..schema import Knob, AttackDescription, RunResult, Figure, Metric
from ..adapters import mnist
from ..adapters.attacks_torch import cw_l2_targeted


def _target_conf(model, x, target_label):
    with torch.no_grad():
        probs = F.softmax(model(x), dim=1)[0]
    return float(probs[target_label])


@register_attack
class CarliniWagnerAttack(AttackModule):
    id = "carlini_wagner"
    name = "Carlini & Wagner (targeted L2)"
    group = "Perturbation"

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group,
            summary=(
                "The **Carlini & Wagner** L2 attack solves an *optimization*: find the "
                "smallest perturbation (in L2) that forces the model to output a chosen "
                "**target** class. It is far stronger than FGSM/PGD and finds tiny, "
                "hard-to-detect perturbations. (This demo fixes the trade-off constant "
                "and iteration count for interactivity.)"
            ),
            formula="minimize ||x_adv - x||_2^2 + c * f(x_adv),  "
                    "f = max(max_{i != t} Z(x_adv)_i - Z(x_adv)_t, -kappa)",
            threat_model="White-box attacker optimizing an input to be classified as a "
                         "chosen target class while minimizing the L2 perturbation.",
            knobs=[
                Knob(name="sample_index", label="Digit sample", type="slider",
                     min=0, max=9, step=1, default=0, help="Which held-out digit to perturb."),
                Knob(name="target", label="Target digit", type="select",
                     options=[str(d) for d in range(10)], default="8",
                     help="The class the attacker forces the model to predict."),
                Knob(name="confidence", label="Confidence (kappa)", type="slider",
                     min=0, max=20, step=1, default=0,
                     help="Higher pushes the target logit further above the rest "
                          "(more robust adversarial, larger perturbation)."),
                Knob(name="steps", label="Optimization steps", type="slider",
                     min=20, max=200, step=10, default=100,
                     help="Adam iterations; more = stronger attack but slower."),
            ],
        )

    def _evaluate(self, model_path, p):
        model = mnist.load_model(model_path)
        xs, ys = mnist.load_samples()
        idx = int(p["sample_index"])
        x = xs[idx:idx + 1]
        true_label = int(ys[idx].item())
        target = int(p["target"])

        x_adv = cw_l2_targeted(
            model, x, torch.tensor([target]),
            steps=int(p["steps"]), confidence=float(p["confidence"]), lr=0.1,
        )
        clean_label, clean_pconf = mnist.predict(model, x)
        adv_label, adv_pconf = mnist.predict(model, x_adv)
        clean_tconf = _target_conf(model, x, target)
        adv_tconf = _target_conf(model, x_adv, target)
        l2 = float(((x_adv - x) ** 2).sum().sqrt())
        fig = mnist.render_attack_figure(
            x, x_adv, (clean_label, clean_pconf), (adv_label, adv_pconf), "C&W",
        )
        return {
            "true_label": true_label, "target": target, "adv_label": adv_label,
            "clean_tconf": clean_tconf, "adv_tconf": adv_tconf, "l2": l2, "fig": fig,
        }

    def _result(self, e, caption, model_desc):
        reached = e["adv_label"] == e["target"]
        if e["true_label"] == e["target"]:
            story = f"the sample is already a {e['target']}, so the target is trivially satisfied"
        elif reached:
            story = f"the {model_desc} model was driven to predict the target {e['target']}"
        else:
            story = (f"the {model_desc} model resisted — it predicts {e['adv_label']}, "
                     f"not the target {e['target']}")
        return RunResult(
            figure=Figure(png_base64=e["fig"], caption=caption),
            metrics=[
                Metric(label="Target-class confidence (clean)",
                       value=e["clean_tconf"], display=f"{e['clean_tconf']:.0%}"),
                Metric(label="Target-class confidence (adversarial)",
                       value=e["adv_tconf"], display=f"{e['adv_tconf']:.0%}"),
            ],
            narrative=(
                f"True digit {e['true_label']}, target {e['target']}: {story}. "
                f"L2 perturbation = {e['l2']:.2f}; target-class confidence "
                f"{e['clean_tconf']:.0%} → {e['adv_tconf']:.0%}."
            ),
        )

    def run(self, params):
        p = self.clean_params(params)
        e = self._evaluate(mnist.STANDARD_PATH, p)
        return self._result(e, "Standard (undefended) model", "standard")

    def defend(self, params):
        p = self.clean_params(params)
        e = self._evaluate(mnist.ROBUST_PATH, p)
        return self._result(e, "Adversarially-trained (robust) model", "adversarially-trained")
