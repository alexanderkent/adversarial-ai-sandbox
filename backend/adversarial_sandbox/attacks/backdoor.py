import torch
from ..registry import register_attack
from ..base import AttackModule
from ..schema import Knob, AttackDescription, RunResult, Figure, Metric, SweepSpec
from ..adapters import mnist
from ..source import snippet
from ..atlas import technique


def _clean_accuracy(model, xs, ys):
    with torch.no_grad():
        return float((model(xs).argmax(dim=1) == ys).float().mean())


def _attack_success_rate(model, xs, ys, target):
    mask = ys != target
    if int(mask.sum()) == 0:
        return 0.0
    with torch.no_grad():
        pred = model(mnist.apply_trigger(xs[mask])).argmax(dim=1)
    return float((pred == target).float().mean())


@register_attack
class BackdoorAttack(AttackModule):
    id = "backdoor"
    name = "Backdoor (BadNets trigger)"
    group = "Backdoor"

    def describe(self):
        return AttackDescription(
            id=self.id, name=self.name, group=self.group,
            summary=(
                "A **backdoor** is planted during *training*: a fraction of images are "
                "stamped with a small **trigger** and relabeled to a target class. The "
                "model behaves normally on clean inputs but classifies **any** triggered "
                f"image as the target ({mnist.BACKDOOR_TARGET}) — stealthy and hard to detect."
            ),
            formula=r"\text{train on } \mathcal{D} \cup \{(x + \tau,\ t)\}; \quad f(x + \tau) = t",
            threat_model="Attacker controls part of the training data (outsourced or "
                         "supply-chain training) and implants a trigger->target rule; "
                         "clean accuracy stays high so the backdoor is hard to notice.",
            code=[
                snippet(mnist.apply_trigger, "Applying the trigger"),
                snippet(mnist.fine_prune, "Fine-pruning (defense)"),
            ],
            knobs=[
                Knob(name="sample_index", label="Digit sample", type="slider",
                     min=0, max=9, step=1, default=1,
                     help="Which held-out digit to show (clean vs triggered)."),
                Knob(name="prune_fraction", label="Fine-pruning fraction", type="slider",
                     min=0.0, max=0.9, step=0.05, default=0.7,
                     help="Defense: fraction of channels to prune before a clean fine-tune. "
                          "More pruning removes more of the backdoor, at some clean-accuracy cost."),
            ],
            sweep=SweepSpec(
                x_knob="prune_fraction",
                x_values=[0.0, 0.3, 0.5, 0.7, 0.9],
                x_label="Fine-pruning fraction",
                y_label="Attack success rate",
                attacked_metric="Attack success rate",
                defended_metric="Attack success rate (pruned)",
            ),
            atlas=[technique("AML.T0018", "Backdoor ML Model", "ML Attack Staging")],
        )

    def _sample_figure(self, model, xs, idx):
        x = xs[idx:idx + 1]
        x_trig = mnist.apply_trigger(x)
        clean_label, clean_conf = mnist.predict(model, x)
        trig_label, trig_conf = mnist.predict(model, x_trig)
        fig = mnist.render_attack_figure(
            x, x_trig, (clean_label, clean_conf), (trig_label, trig_conf), "Trigger",
        )
        return clean_label, trig_label, fig

    def run(self, params):
        p = self.clean_params(params)
        model = mnist.load_model(mnist.BACKDOOR_PATH)
        xs, ys = mnist.load_eval()
        samples, _ = mnist.load_samples()
        clean_acc = _clean_accuracy(model, xs, ys)
        asr = _attack_success_rate(model, xs, ys, mnist.BACKDOOR_TARGET)
        clean_label, trig_label, fig = self._sample_figure(model, samples, int(p["sample_index"]))
        return RunResult(
            figure=Figure(png_base64=fig, caption=f"The trigger forces class {mnist.BACKDOOR_TARGET}"),
            metrics=[
                Metric(label="Clean accuracy", value=clean_acc, display=f"{clean_acc:.0%}"),
                Metric(label="Attack success rate", value=asr, display=f"{asr:.0%}"),
            ],
            narrative=(
                f"The backdoored model predicts {clean_label} on the clean digit but "
                f"{trig_label} once the trigger is added. Clean accuracy stays {clean_acc:.0%} "
                f"while the trigger reaches the target {mnist.BACKDOOR_TARGET} on {asr:.0%} of inputs."
            ),
        )

    def defend(self, params):
        p = self.clean_params(params)
        model = mnist.load_model(mnist.BACKDOOR_PATH)
        xs, ys = mnist.load_eval()
        samples, _ = mnist.load_samples()
        asr_before = _attack_success_rate(model, xs, ys, mnist.BACKDOOR_TARGET)
        ft_x, ft_y = mnist.load_finetune()
        pruned = mnist.fine_prune(model, ft_x, ft_y, float(p["prune_fraction"]))
        clean_acc = _clean_accuracy(pruned, xs, ys)
        asr_after = _attack_success_rate(pruned, xs, ys, mnist.BACKDOOR_TARGET)
        clean_label, trig_label, fig = self._sample_figure(pruned, samples, int(p["sample_index"]))
        return RunResult(
            figure=Figure(png_base64=fig,
                          caption=f"After fine-pruning {p['prune_fraction']:.0%} of channels"),
            metrics=[
                Metric(label="Clean accuracy (pruned)", value=clean_acc, display=f"{clean_acc:.0%}"),
                Metric(label="Attack success rate (pruned)", value=asr_after, display=f"{asr_after:.0%}"),
            ],
            narrative=(
                f"Fine-pruning {p['prune_fraction']:.0%} of dormant channels cut the attack "
                f"success rate from {asr_before:.0%} to {asr_after:.0%}, while clean accuracy is "
                f"{clean_acc:.0%}. The triggered digit now reads {trig_label}."
            ),
        )
