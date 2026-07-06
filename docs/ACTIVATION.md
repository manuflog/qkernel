# Contextuality activation by dimension embedding

A base Weyl family that is **non-contextual** under the state-independent odd-Q
criterion can become **contextual** after passive embedding into twice the local
dimension (`d -> 2d`). The embedded family is the **fiber pool**: the union, over
base contexts, of every valid `d -> 2d` lift of that context. Lifting is a
label-level passive embedding in the mathematical model (a relabeling of Weyl
indices; no entangling gates appear in the label algebra). qkernel makes no
claim that this embedding is free as a physical or compiler resource (see the
README scope box). Under the odd-Q criterion this exhibits contextuality as a
resource *activated* by embedding.

## Usage
```python
from qkernel.io import load_program
from qkernel.embedding import activation_report

report = activation_report(load_program("examples/activation_base_d4.json"))
# report.base_contextual   -> False  (odd-Q obstruction absent at d=4)
# report.fiber_contextual  -> True   (present in the fiber pool at d=8)
# report.activated         -> True
```
CLI: `qkernel activation examples/activation_base_d4.json`.

## Verdict is criterion-consistent
Activation compares `analyze` (the odd-Q obstruction) on the base at `d` against
`analyze` on the fiber pool at `2d` — the *same* criterion at both levels. (This is
distinct from the AvN `check_zd_valuation`, which can already report a d=4 family as
contextual; the two criteria are not interchangeable.)

## Yield (verified)
Activation is not universal: for random non-contextual bases the activation yield
rises **monotonically** with base size, and the rise is **non-linear** (concave,
saturating toward 1). Wilson 95% CI, 150-400 seeds/point (`experiments/activation_yield.py`):

| base size | 3 | 4 | 5 | 6 | 7 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|---|---|
| yield | 4.5% | 13.5% | 19.0% | 30.0% | 42.0% | 46.0% | 66.2% | 73.8% |

The 3->4 step has disjoint CIs ([2.4,8.3] vs [9.4,18.9]), so it is statistically real.
An apparent 10%->8% dip in an earlier coarse 60-seed run was sampling noise. The
non-activation probability (1 - yield) decays roughly geometrically (~0.87 per added
context), giving the steep-then-saturating shape.

## Dependence on base dimension (verified)
Activation readiness falls off sharply with base dimension. Yield at nctx=6 (100-150 seeds):
d=4->8 **30%** [23,38]; d=6->12 **9%** [4.8,16]; d=8->16 **2%** [0.6,7]. The d=4->8 curve fits
1 - yield ~ 1.63 * 0.861^nctx (R^2=0.98); at d>=6 the yield sits near the noise floor for small bases.

A tempting hypothesis — "2-primary d activates readily" — is **refuted**: d=8 (=2^3, purely
2-primary) activates as rarely as d=6, not like d=4. So 2-adic structure alone does not govern
activation; base dimension does, with d=4 a special readily-activating regime.

## Why is d=4 special? (structural finding)
Activation is a **codimension-1** event, not a coarse size effect. Fiber pools that activate are
structurally **indistinguishable** from those that do not: at fixed (d, nctx) the activating and
non-activating pools have the same pool size, the same cycle-space dimension, and the same number of
odd-carry contexts (measured over random non-contextual bases). Activation is determined solely by
whether the fiber carry vector b escapes the row space of the incidence matrix (the full odd-Q test) --
there is no coarse proxy. So the sharp fall in yield with base dimension d is real but is **not**
explained by pool size or cycle dimension; it reflects how often the carry vector escapes the row
space, a delicate arithmetic property of the d -> 2d carry. (This corrects an earlier hand-wave that
the d=8 pool is "just large enough" to close odd cycles -- the cycle spaces are in fact the same size.)

## Activation as resource generation
`qkernel.embedding.activated_resource` (CLI: `activation-resource`) turns activation into a usable
resource: given a non-contextual base, if the d->2d embedding activates, it extracts the cheapest
activated contextuality test (a low-weight odd-Q kernel of the fiber pool) as concrete fiber
measurement settings, with the resource value (fiber d)/2.

**Verification criterion (important).** The activated test is verified on the **odd-Q** criterion that
activation is defined on (every observable used an even number of times, odd total carry) -- *not* via
`verify_kernel`, which additionally demands Z_d/AvN valuation-contextuality. Those criteria differ:
the minimal activated fiber sub-family is a genuine odd-Q (state-independent parity) obstruction but
need not be AvN-contextual on its own. Using the odd-Q verifier keeps the resource claim consistent
with the definition and the validated yield curves.
