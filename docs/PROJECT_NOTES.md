# Adversarial Sandbox — Design & Findings Notes

> **Scope of this document.** These are *technical* notes on what the sandbox is,
> how it is built, and what was empirically observed while building it. They are
> engineering documentation and a starting point for your own analysis — **not** a
> substitute for the academic report. Per the CNIT 573 AI-use policy, the core
> analysis, interpretation, and write-up must be your own, and AI assistance in
> producing this codebase should be disclosed in your report's AI-usage section.

## 1. What it is

An interactive web sandbox for learning adversarial ML. A student picks an attack,
reads a short guided lesson (plain-English explainer, the formula, the threat model),
tunes the attack's parameters, runs it, and sees the resulting artifact (a decision
boundary or a perturbed image) plus metrics and a plain-English narrative — then
toggles the paired **defense** and re-runs to see the countermeasure.

Three attack families, spanning the two "worlds" of the course:

| Module | Substrate | Attack | Defense | Course module |
|---|---|---|---|---|
| Data Poisoning | scikit-learn, 2D | label flip + concentrated poison blob | super-majority label cleaning | M2 Poisoning |
| Perturbation | PyTorch, MNIST | FGSM / PGD (evasion) | adversarial training | M3 Perturbations / M5 Evasion |
| Carlini & Wagner | PyTorch, MNIST | targeted C&W-L2 (optimization) | adversarial training | M3 / M6 defenses |

## 2. Architecture (and why)

- **Backend (FastAPI) owns all ML; frontend (React) is a thin renderer.** The backend
  returns plain JSON with figures as base64 PNGs, so the UI never touches ML.
- **Plugin registry of self-describing modules.** Each attack subclasses `AttackModule`
  and self-registers via a `@register_attack` decorator. Its `describe()` returns both
  the lesson content *and* a knob schema (each control's type/range/default). `run()`
  and `defend()` return a typed `RunResult`.
- **Schema-driven UI.** The React control panel renders whatever knobs `describe()`
  returns; the sidebar and artifact panel are attack-agnostic.

**The payoff — extensibility:** adding a new attack is *one backend module file + one
import line*. Nothing else changes. This was validated twice: the perturbation and,
later, the **Carlini & Wagner** module each appeared in the UI — new sidebar entry, new
`target` select knob, new lesson, rendered artifact — with **zero frontend changes** and
**zero contract-test edits** (a parametrized test auto-covers every registered module).
For a course that will add attacks in future iterations, this is the central design win.

## 3. The three attacks in one paragraph each

**Data poisoning.** On a 2D toy dataset, flip a fraction of training labels and inject a
tight cluster of mislabeled points ("poison blob") deep inside the opposite class, then
train a label-noise-*sensitive* (high-C) SVM so the boundary visibly contorts. The
defense removes points whose label disagrees with a super-majority of their neighbors
(Edited-Nearest-Neighbors), keeping honest boundary points.

**FGSM / PGD.** On MNIST, add a small L∞-bounded perturbation along the sign of the loss
gradient (FGSM, one step; PGD, iterated) so the classifier is fooled. The defense is a
second network trained on adversarial examples (adversarial training).

**Carlini & Wagner (targeted L2).** On MNIST, *optimize* a minimal-L2 perturbation that
forces a chosen **target** class, using the tanh change-of-variables, Adam, and the C&W
margin objective with a confidence parameter κ. E.g. a **7 forced to read as 8** with
L2 ≈ 2.5. (For interactivity the demo fixes the trade-off constant `c` and bounds the
iteration count — the classic binary search over `c` is omitted; noted in the lesson.)

## 4. Empirical findings worth analyzing in the report

These came out of actually building and testing the tool — they are good material for
your own critical analysis (verify and extend them yourself).

### 4.1 Label-cleaning defenses are surprisingly weak on a soft-margin SVM
The first poisoning defense paired a plain-majority k-NN label cleaner with a standard
(soft-margin) SVM. A parameter sweep over dataset, separation, flip rate, and injection
size (20 random seeds each) found **no regime** where the defense reliably recovered
accuracy *per run* — it only helped on average. Two compounding reasons:

1. A soft-margin SVM already absorbs moderate label noise as slack, so removing that
   noise barely moves the boundary — until the noise is heavy.
2. At heavy flip rates, a corrupted point's *neighborhood* is itself ~40–50% corrupted,
   so a neighbor-vote cleaner has little signal and prunes honest boundary points about
   as often as poison.

**What made it robust** (final design): (a) a label-noise-*sensitive* high-C SVM, so
poison genuinely bends the boundary and there is something to recover; (b) a
*concentrated* poison blob (detectable, damaging) rather than scattered flips; and
(c) a *super-majority* cleaner that only removes points deep in enemy territory,
preserving the ambiguous boundary. This cleared a strict bar (defended ≥ poisoned on
all 20 seeds, with a real gap). *Analysis hook:* this is a concrete illustration of the
course's Module 6 theme — defenses have limits, and their effectiveness is entangled
with the model and the attacker's strategy.

### 4.2 C&W at zero confidence lands on the decision boundary
With κ = 0, the C&W objective's optimum sits exactly where the target logit ties the
best other logit — i.e. right on the decision boundary. The attack therefore *reaches*
the target (it becomes the argmax) but with modest confidence (≈36–50% on the examples
tried), and on a poorly-conditioned model can stall just short. Raising κ pushes the
target logit further above the rest — more robust/transferable adversarial examples at
the cost of a larger perturbation. *Analysis hook:* κ is a clean knob for discussing the
robustness-vs-distortion trade-off, and for comparing C&W's minimal L2 against the
larger, cruder perturbations of FGSM/PGD.

### 4.3 Optimizer settings matter for interactive C&W
On MNIST, C&W needed a larger Adam learning rate to reach the target within an
interactive iteration budget (~100 steps) rather than ~400 at a textbook-small rate.
A practical note on deploying optimization-based attacks in a responsive tool.

## 5. Verification

- Backend: 42 automated tests (pytest), including per-attack tests that assert the
  attack measurably degrades the model and the defense measurably recovers/resists, plus
  a parametrized contract test over every registered module.
- Frontend: 24 component tests (Vitest + React Testing Library); clean TypeScript build.
- End-to-end: all three attacks were driven live in a browser against the running
  backend (poisoning boundary shift, FGSM confidence drop, C&W 7→8 targeted flip).

## 6. Limitations & future work

- **C&W** omits the binary search over `c` and uses a fixed learning rate (interactivity
  trade-off). A "thorough mode" could restore both.
- **Poisoning** lives on 2D toy data by design (for visual clarity); the findings about
  defense fragility should be re-checked on higher-dimensional/tabular data.
- **Substrate coverage**: backdoor attacks (M4) and additional defenses (gradient
  masking, defensive distillation, M6) are natural next modules — each is one new file.
- **Portability**: the code targets CPU; a couple of tensors would need device-awareness
  for GPU.
- **Not evaluated**: transferability across models, adaptive attacks against the
  defenses, or formal robustness metrics — all good extensions for deeper analysis.

## 7. How to run

```bash
# backend
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
pip install torchvision && python scripts/train_mnist.py   # one-time, downloads MNIST
uvicorn adversarial_sandbox.api:app --port 8000
# frontend (separate terminal)
cd frontend && npm install && npm run dev                  # http://localhost:5173
```
