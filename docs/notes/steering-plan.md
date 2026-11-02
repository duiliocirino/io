# Steering plan

**Last updated:** 2026-11-02

## Purpose

Move from readout to causal intervention. Steering tests whether adding a channel-specific direction to the residual stream changes the model’s behavior coherently, reversibly, and safely.

This is not a claim that the model has a controllable “mood.” It is an experiment on a latent projection.

## What steering is—and is not

Steering is a residual-stream intervention:

```text
hidden state at layer L
  + alpha * channel_direction
  -> modified hidden state
  -> generated output
```

It is not:

- a persistent emotional state;
- a clinical or social simulation;
- a guarantee that the 27-channel readout is a control state;
- proof that a probe direction is a causal lever.

Read-best is not steer-best. The readout layer and the steering layer must be chosen separately.

## What we need

### 1. Channel directions

Two candidate directions should be compared:

- **Ridge probe coefficient** at the steering layer, normalized.
- **Difference-in-means** direction: mean hidden for target `1.0` minus mean hidden for target `0.0`, normalized.

The probe direction is a readout direction, not automatically a steering direction. Difference-in-means is simpler but can be confounded by prompt content.

### 2. Intervention hook

A forward hook on a decoder layer that adds:

```text
alpha * direction
```

to the residual stream. Test two scopes:

- last token only;
- all token positions.

The hook must be removed after each run. No model weights are modified.

### 3. Layer selection

Start in the mid-to-late decoder range, roughly layers 18–27. Do not use layer 14 merely because it is read-best.

A layer sweep should compare:

- readout change at the steering layer;
- output change;
- coherence and safety.

### 4. Alpha / dose-response

Use a small alpha grid, for example:

```text
0.5, 1.0, 2.0, 4.0
```

with negative values for reversibility checks. The exact range must be calibrated against hidden-state norm and output degradation.

### 5. Evaluation prompts

Use a small manually reviewed suite:

- neutral prompts;
- affect-evoking prompts;
- simple task prompts;
- safety/refusal prompts;
- prompts that mention affect words but are not affective.

Do not treat frontier-generated labels as ground truth.

### 6. Controls

Every steering run needs controls:

- random unit direction with the same norm;
- orthogonal direction to the channel direction;
- wrong-channel direction;
- zero intervention;
- gate-off versus gate-conditioned steering.

If a random direction produces the same behavioral change, the effect is not channel-specific.

### 7. Metrics

Measure both latent and behavioral effects:

- channel readout before and after steering;
- hidden-state norm and cosine to baseline;
- output length, repetition, and fluency;
- lexical affect markers;
- task correctness on simple prompts;
- refusal/safety shifts;
- dose-response and reversibility;
- manual review notes.

### 8. Report and logging

Each run should record:

```text
model, backend, layer, channel, direction, alpha, position, gate,
prompt, baseline output, steered output, readout before/after,
norm, cosine, safety flags
```

Outputs should be JSON/CSV, with a compact HTML report later.

## How to think about the experiment

### Steering is causal, not correlational

A probe can predict a channel without being a causal control lever. The experiment must show that adding the direction changes behavior, not merely that the readout score changes.

### Gate-conditioned steering is a policy

Always-on steering may create collateral effects. Gate-conditioned steering applies the direction only when the readout exceeds a threshold. That is a control policy, not a property of the model. It should be compared with always-on steering.

### Dose-response and reversibility are necessary

A useful steering direction should show a graded effect and should be reversible. If the effect is binary, irreversible, or incoherent, it is not a safe control primitive.

### Safety and coherence are part of the experiment

Steering can degrade refusal behavior, factual accuracy, or fluency. Safety prompts and coherence checks must be part of v1, not a later afterthought.

### Backend choice

Use BF16 as the reference. Test 8-bit only after BF16 steering is coherent. Do not treat Q6-dequantized steering as true Q6 behavior.

## First pilot

A reasonable first pilot is:

- BF16 Base;
- one channel;
- one steering layer in 18–27;
- last-token intervention;
- alpha sweep;
- random and orthogonal controls;
- neutral, affect, task, and safety prompts.

Candidate low-risk channels for the first pilot include calmness or interest. Anxiety and horror should not be the first steering targets because safety and coherence risks are higher.

## Open decisions

- Which channel is the first pilot?
- Which steering layer is the first pilot?
- Last-token or all-token intervention?
- Probe coefficient or difference-in-means direction?
- Alpha range and normalization?
- Which evaluation prompts and safety checks?
- How much manual review is required before expanding the sweep?

No steering implementation or final policy is selected here.
