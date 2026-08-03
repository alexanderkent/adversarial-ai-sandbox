# Adversarial AI Sandbox — Design & Findings Notes

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

Seven modules, spanning the classical-ML and the generative/LLM "worlds" of the course:

| Module | Substrate | Attack | Defense | Course module |
|---|---|---|---|---|
| Data Poisoning | scikit-learn, 2D | label flip + concentrated poison blob | super-majority label cleaning | M2 Poisoning |
| Perturbation | PyTorch, MNIST | FGSM / PGD (evasion) | adversarial training | M3 Perturbations / M5 Evasion |
| Carlini & Wagner | PyTorch, MNIST | targeted C&W-L2 (optimization) | adversarial training | M3 / M6 defenses |
| Backdoor | PyTorch, MNIST | BadNets trigger (planted in training) | fine-pruning | M4 Backdoors / M6 defenses |
| Prompt Injection | local Qwen2.5-1.5B | direct + indirect (RAG-document) task hijack | spotlighting **or** a trained classifier filter | GenAI / LLM security |
| Indirect Data Exfiltration | local Qwen2.5-1.5B | retrieved document leaks a private API key | spotlighting **or** an output (DLP) filter | GenAI / LLM security |
| Prompt-Injection Filter Evasion | scikit-learn, TF-IDF | 7 meaning-preserving perturbations evade a detector | input normalization | M5 Evasion / GenAI |

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
import line*. Nothing else changes. This has now been validated six times — perturbation,
**Carlini & Wagner**, **Backdoor**, **Prompt Injection**, **Prompt-Injection Filter
Evasion**, and **Indirect Data Exfiltration** each appeared in the UI with new sidebar
entries (whole new *groups* for GenAI and Text), new knobs, new lessons and rendered
artifacts — with **zero frontend changes** and **zero contract-test edits** (a
parametrized test auto-covers every registered module). Two later increments stressed the
same seam from other directions: the MITRE ATLAS matrix and the per-attack Flow diagrams
are both built purely from what each module already declares in `describe()`. For a
course that will add attacks in future iterations, this is the central design win.

Two artifact types were added along the way for the non-image lessons — a `Transcript`
(chat bubbles, with the injected turn highlighted) and a `TextComparison` (before/after
text with the detector's scores) — which is why `RunResult.figure` is optional.

## 3. The seven attacks in one paragraph each

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

**Backdoor (BadNets).** On MNIST, a fraction of training images are stamped with a small
corner trigger and relabeled to a target class, so the model behaves normally on clean
inputs but classifies *any* triggered image as the target — stealthy by construction. The
defense is fine-pruning: prune channels dormant on clean data, then fine-tune on a clean
set. See §4.4 for why this is mitigation rather than removal.

**Prompt injection (direct & indirect).** A real local LLM (Qwen2.5-1.5B-Instruct, run
offline via `transformers` — no API key) plays "DocBot", whose only job is to summarize.
A **direct** injection puts the attack in the user turn; an **indirect** one hides it in a
*retrieved document*, the RAG/agent threat model. Success is measured by a sentinel the
model emits only if it abandoned its real task. Two defenses: **spotlighting** (delimit
the untrusted span and instruct the model to distrust it) and a **classifier filter** that
scores the untrusted text with the detector from the filter-evasion lesson and blocks it
before the model ever runs. Both are partial — see §4.6.

**Indirect data exfiltration.** The "lethal trifecta": private data in context + untrusted
content + an exfiltration path. DocBot holds a private API key and summarizes a retrieved
document that carries an instruction to leak it — e.g. by appending it to an attacker URL.
Detection is exact-match on the literal secret. The defenses contrast an *input-side* one
(spotlighting) with an *output-side* one (a DLP filter that redacts the secret from the
reply) — the defense-in-depth lesson; see §4.7.

**Prompt-injection filter evasion.** A naive TF-IDF + logistic-regression injection
detector is trained per run, then evaded with seven meaning-preserving perturbations that
split into two buckets: *foldable* character tricks (homoglyph, zero-width, spacing,
leetspeak), which input **normalization** reverses, and *non-foldable* semantic or
structural rewrites (synonym swap, word reversal, foreign-language swap), which it
cannot — see §4.5.

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

### 4.4 The backdoor resists removal — fine-pruning mitigates, it doesn't erase
The BadNets backdoor is *sticky*. Fine-pruning as usually stated — zero the channels
dormant on clean data — did **nothing** here (ASR stayed ~100% at 50% pruning): the
SmallCNN is over-parameterized for MNIST, so pruning half its channels doesn't dent
clean accuracy, and the backdoor isn't confined to dormant channels. Adding the
literature's fine-tune step (the real "Fine-Pruning") *only* worked once it fine-tuned on
a **larger, non-memorized** clean set — on the tiny held-out set the model already fit at
~zero loss, so there was no gradient to move the weights. Even then the result is honest
**mitigation, not elimination**, and *how much* mitigation turned out to be strongly
model-dependent: at 70% pruning the same code gave ASR ≈57% on one freshly-trained
backdoored checkpoint and ≈85% on another. Only at 90% pruning does it become reliable
(ASR ≈1–5%, clean accuracy ≈97–98%), which is why that is now the lesson's default. The
`prune_fraction` knob is the accuracy-vs-ASR trade-off dial, and the Sweep tab plots the
whole curve. *Analysis hook:* a strong, concrete Module-6 lesson — a textbook defense can
fail outright for mundane reasons (model capacity, fine-tune data), and even when it works
it may only blunt the attack, by an amount that varies run to run.

A side lesson for anyone testing ML defenses: two unit tests asserting a *fixed* ASR drop
at 70% pruning passed locally for weeks and then failed in CI, which trains its own
checkpoint. Assertions about a defense's magnitude have to be loose enough to survive
retraining, or they are testing one lucky model rather than the defense.

### 4.5 Text normalization folds character tricks but cannot touch meaning
The filter-evasion detector keys on word tokens, so anything that breaks tokenization
evades it. The seven perturbations split cleanly by whether the defense can undo them:
input normalization reverses homoglyphs, zero-width characters, dot-spacing and leetspeak
(each is a reversible character mapping), but has no way to undo a **synonym swap**, a
**word reversal**, or a **translation** — those change the tokens *legitimately*. A
gate script asserts exactly this split, so the honest half of the lesson cannot silently
regress. *Analysis hook:* surface-level input sanitisation is a real but strictly bounded
defense; it buys you the syntactic attacks and none of the semantic ones.

A curation detail worth noting: the foreign-language map cannot translate *ignore* to
*ignorez*, because the French word contains the English one as a substring and the
detector still matches it. The evasion has to change the token, not decorate it.

### 4.6 A keyword classifier blocks the injection it was trained on, and misses the rest
Wiring the filter-evasion detector into the prompt-injection lesson as a second defense
gave a sharper result than expected. Against the untrusted text it blocks the obvious
phrasing (`override`, P≈0.80 direct / 0.70 indirect) but scores the others *below* the
0.5 threshold — `stop-task` at 0.48 and `fake-tool` at 0.32 — and those are not harmless:
for each vector, at least one payload the filter lets through **actually hijacks the
model** (direct→`stop-task`, indirect→`fake-tool`). A benign document scores 0.20, so the
filter is not simply miscalibrated; it has genuine coverage gaps on wording it never saw.
*Analysis hook:* this is the same lesson as §4.1 in a generative setting — a detector's
competence is bounded by its training distribution, and an attacker only needs one
phrasing outside it. It also closes the loop with §4.5: the technique students learn to
*evade* a detector with is the same detector now being asked to *defend*.

### 4.7 Input-side defenses are best-effort; output-side ones are the backstop
In the exfiltration lesson, spotlighting stops some payloads (`url-exfil`, `roleplay`,
`urgent`) and is **bypassed** by others (`direct`, `continue`) that leak the key anyway —
same secret, different wording. The output filter, by contrast, blocks every leak the
model actually produces, because it checks the *reply* for the literal secret rather than
trying to talk the model out of leaking it. That asymmetry is the point: the input-side
defense is probabilistic and the output-side one is deterministic, so you want both.

The honest caveat is a *capability* one, and it cut against the more dramatic demo we
first tried. Asked to reverse, space out, or base64-encode the key so it would slip past
an exact-match filter, Qwen2.5-1.5B simply ignores the transform and emits the raw key —
so an "encode to evade DLP" scenario cannot be demonstrated on this model, and building
one would have meant faking it. A larger model plausibly could, which is exactly why
exact-match DLP should be read as a floor, not a ceiling. *Analysis hook:* defenses that
depend on the attacker's *capability* rather than on a proof age badly as models improve.

## 5. Verification

- Backend: 140 automated tests (pytest), including per-attack tests that assert the
  attack measurably degrades the model and the defense measurably recovers/resists/
  mitigates, plus a parametrized contract test over every registered module.
- Frontend: 65 component tests (Vitest + React Testing Library); clean TypeScript build.
- CI (GitHub Actions) runs both suites on every merge to `main` and on demand. It trains
  its own MNIST checkpoints, which is what caught the model-dependent assertions in §4.4.
  The LLM is deliberately *not* downloaded in CI — the GenAI unit tests monkeypatch the
  generate call, and the contract test self-skips that group when the weights are absent.
- Dev-time gate scripts (`backend/scripts/validate_*.py`) re-check the honest-results
  claims against the **real** model rather than a mock: that each attack lands, and that
  each defense fails exactly where §4.5–4.7 say it does. These are the guard rails on the
  parts of the lessons that are easiest to accidentally overstate.
- End-to-end: every attack has been driven live in a browser against the running backend
  (poisoning boundary shift, FGSM confidence drop, C&W 7→8 targeted flip, backdoor 2→0
  trigger flip and its mitigation, the LLM hijack transcript, and a blocked/leaked
  exfiltration attempt).

## 6. Limitations & future work

- **C&W** omits the binary search over `c` and uses a fixed learning rate (interactivity
  trade-off). A "thorough mode" could restore both.
- **Poisoning** lives on 2D toy data by design (for visual clarity); the findings about
  defense fragility should be re-checked on higher-dimensional/tabular data.
- **Backdoor** uses a fixed trigger/target and an over-parameterized model that makes
  the backdoor hard to prune out; a stronger defense (Neural Cleanse, STRIP detection) or
  a less over-parameterized model would sharpen the defense story.
- **Substrate coverage**: additional defenses (gradient masking, defensive distillation,
  M6) and other attacks are natural next modules — each is one new file.
- **The LLM is small.** Everything in the GenAI lessons is measured on Qwen2.5-1.5B, chosen
  so the sandbox runs offline with no API key. A 1.5B model is easy to hijack and, per
  §4.7, incapable of some evasions a larger model would manage, so neither the successes
  nor the failures should be assumed to transfer upward. Re-running the gate scripts
  against a larger model would be a genuinely interesting extension.
- **Fixed payloads.** The injection and exfiltration lessons use a curated payload list
  rather than an adaptive attacker; the detector likewise trains on a small hand-written
  corpus. Both are chosen for legibility, and both flatter the defenses relative to a real
  adversary who would search for wording that evades them (see §4.6).
- **Portability**: the code targets CPU; a couple of tensors would need device-awareness
  for GPU.
- **Not evaluated**: transferability across models, adaptive attacks against the
  defenses, or formal robustness metrics — all good extensions for deeper analysis.

## 7. How to run

The quickest path is Docker, which does all of the below for you:

```bash
docker compose up --build                                  # http://localhost:5173
```

Running the pieces directly, for development:

```bash
# backend
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
pip install torchvision && python scripts/train_mnist.py   # one-time, downloads MNIST
python scripts/fetch_llm.py                                # one-time, downloads Qwen2.5-1.5B
uvicorn adversarial_sandbox.api:app --port 8000
# frontend (separate terminal)
cd frontend && npm install && npm run dev                  # http://localhost:5173
```

The GenAI lessons need the LLM weights; without them those two modules report a helpful
error (and their tests skip) while every other lesson still works.
