# Source gap register and audit

## Purpose

This note consolidates what the Gemini discussion covers, what the existing research packs already capture, and what remains under-integrated. It is a control document for the later synthesis and technical architecture—not a new research pack and not a claim that the source is wrong.

The source is a generative synthesis. Some claims are empirical, some are interpretations, and some are engineering proposals. The register separates those levels and records repeated blocks so they are not mistaken for new evidence.

## Coverage summary

The source covers:

- offline modes, consolidation, and synaptic homeostasis;
- exteroception and computational interoception;
- triple-network routing, cognitive load, and fatigue;
- CLS 2.0 memory: working memory, short-term labile traces, long-term structure, schema bypass, replay, episodic control, and reconsolidation;
- core affect, social homeostasis, epistemic curiosity, and the proposed cognitive-coherence drive;
- basal-ganglia/PBWM gating: default brake, selective release, competitor veto, conflict hold, and input/output gating;
- neuromodulators as global meta-parameters;
- latent readout and steering of an LLM;
- a complete loop that treats the LLM as a computational cortex inside a persistent external state machine.

The dedicated Layer 6 and Layer 7 expansions at lines 370–459 are repeated at lines 484–573. The repetition is not additional evidence.

## Gap register

| Gap | Source location | Current status | Why it matters | Next question |
| --- | --- | --- | --- | --- |
| **Virtual body / computational interoception** | Lines 13–18 | Partially covered in routing and valuation notes; not integrated as a first-class state layer | A disembodied system still needs internal telemetry: context load, latency, uncertainty, error rate, storage, compute budget | Define measurable internal variables and their set-points |
| **Offline mode / synaptic homeostasis / weight normalization** | Lines 3–11 | Memory document covers sleep and synaptic homeostasis, but the architecture does not schedule an offline mode | Prevents catastrophic forgetting and uncontrolled representational saturation | Define offline schedule, replay policy, pruning/renormalization, and retention tests |
| **Cognitive coherence as a homeostatic drive** | Lines 61–75 | Social and epistemic drives are developed; cognitive coherence is not | Internal contradictions and schema conflicts need a repair signal, not only curiosity or social calibration | Define contradiction detection, schema consistency, and bounded repair |
| **Softmax placement** | Lines 624–638 | Implicit in the documents; not stated precisely | The 27 affective channels can co-activate; the softmax simplex belongs to action/thought selection, not emotion channels | Separate affective state from gate selection |
| **27-channel functional clustering** | Lines 638–648 | Not developed in the packs | The source groups channels into epistemic, social, goal-valuation, temporal/aesthetic, and visceral clusters | Treat the clustering as a design hypothesis and test it |
| **Equation upgrades** | Lines 650–692 | Partially covered through interaction and arbitration; formal upgrades are missing | Lateral coupling \(W_{ij}\), dynamic decay, and bidirectional projection are central to a persistent state | Formalize and test the state-update equations |
| **Affect-biased retrieval and schema gate** | Lines 602–622 | Memory document covers state/affect-biased retrieval and schema assimilation as hypotheses | The integrated loop needs a retrieval policy and a quarantine/fast-track decision | Define retrieval weighting, provenance, and schema checks |
| **Latent readout and steering** | Lines 710–830 | Recorded in the learning notebook; no full specification yet | The 27D state needs calibrated probes, direct telemetry, and bounded steering | Build model-specific readout and steering experiments |
| **RLHF self-report unreliability** | Lines 722–728 | Not explicit in the packs | Asking the LLM to output emotional JSON is wasteful and unreliable; probes and telemetry are better | Use latent probes and direct telemetry rather than verbal self-report |
| **Prototype stack** | Lines 826–830 | Absent | The bridge needs an open-weights model and residual-stream hooks | Choose Qwen 3.5 9B or Dory 1.0 4B and test with TransformerLens/nnsight/vLLM |
| **Safety and steering externalities** | Not developed in the source | Added in the notes and research caveats | Steering can degrade coherence, push states off-manifold, and create jailbreak risk | Require bounded, reversible, audited interventions |
| **Runtime dashboard** | User addition, not in the source | Not yet designed | Observability is needed to see latent state, memory, gating, action, and modality at runtime | Design a time-series telemetry dashboard |
| **Complete architecture naming** | Lines 464–480 and 578–594 | Partially captured | The source calls it “6-layer” but lists Layers 1–7 with Layers 6 and 7 combined | Clarify the layer count and interfaces |
| **Repeated blocks** | Lines 484–573 | Already noted | The repetition can inflate apparent coverage | Do not double-count it as new material |

## Claim corrections

- **“PBWM proves”** — PBWM is a computational model, and Chatham et al. support specific gating evidence, not a universal controller.
- **“Social homeostasis strictly requires”** — social hunger is a candidate mechanism, not a software requirement or a clinical state.
- **“The 27 feelings are constructed by DMN/LTM hubs”** — this is a biological analogy, not an LLM mechanism. The practical route is latent readout and calibration.
- **“Linear emotion subspaces are causal”** — activation steering shows causal effects in specific models and settings; it does not establish a universal emotion axis.
- **“Monosemantic features for confusion, sycophancy, conflict, and goal frustration”** — SAE features can be polysemantic; “dedicated feature” language should be qualified.
- **“Attention entropy is the exact equivalent of fatigue”** — this is a hypothesis, not an established equivalence.
- **“RLHF models are notoriously bad at verbal self-report”** — plausible design rationale, but it needs citation and task-specific validation.

## What is already covered

The routing, memory, and valuation packs already cover the main mechanisms:

- triple-network routing and its evidence limits;
- CLS 2.0 memory procedures and engineering caveats;
- core affect, social homeostasis, curiosity, gating, and neuromodulators;
- latent readout and steering as a correction to the biological framing.

The gap register is therefore about **integration**, not missing source sections.

## Recommended next step

Use this register as the checklist for the integrated synthesis and the technical architecture. Then move to the model-specific latent experiment:

1. choose the model;
2. extract residual-stream activations;
3. calibrate affect/value probes;
4. test causal steering and coherence;
5. connect the readout to a persistent state and dashboard.

No implementation, thresholds, set-points, or final architecture are selected here.
