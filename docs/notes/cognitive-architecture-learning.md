# Cognitive architecture — learning notebook

Working notes, not a research publication or an agreed system specification. See the [research map](research-map.md) for the short overview.

## Purpose and working method

- Learning and source gathering are essential deliverables. Make prerequisites explicit, explain mechanisms through examples, and introduce notation with its meaning rather than assuming a neuroscience background.
- Proceed section by section at the user's pace. Questions, disagreements, and tentative connections are useful inputs, not implicit design decisions.
- Anticipate later coverage using the [source-reading guide](source-reading-guide.md) and the relevant source passages before expanding an early overview. Signpost later explanations, answer immediate prerequisites, and investigate actual gaps; do not force deferral when the user wants depth now.
- Preserve the original conversation. When a topic returns, address new material and unresolved questions rather than repeating earlier explanations; distinguish reading coverage, understanding, and scientific verification.
- Develop independent deep dives and companion presentations first. Create an integrated system document and presentation afterwards.
- Reuse the existing IO design and components; extend the shared vocabulary only when the content needs it.
- Keep user observations, empirical findings, scientific hypotheses, and engineering proposals distinguishable. Discussion summaries remain open to correction.
- Experimental direction: intentionally replicating selected biological mechanisms may be central to the experiment; avoid unnecessary scripting or restriction of expression, not biological structure itself. Simpler prompting is a provisional preference, not a settled rule. See the [experimental-stance checkpoint](#experimental-stance-and-latent-readouts).

## Consciousness and offline modes

**Status:** returning for deeper exploration after the opening-layer discussion. The earlier sleep/homeostasis explanation is understood, and the online-plus-maintenance direction remains provisional. Build on that checkpoint rather than restarting it; no operating-mode implementation or claim about artificial consciousness is established.

### User observations and questions

1. A future sleep-like phase might provide room for rearranging memory and performing work that conflicts with live interaction.
2. Is this grounded in brain function, or primarily a convenient engineering arrangement?
3. Offline work alone may not be sufficient; mechanisms should also be considered during online operation.
4. Synaptic homeostasis needs a deeper explanation and a careful translation into the proposed system.
5. Keep a concise, updatable overview of all topics alongside the fuller learning material.

These are exploratory directions. No sleep schedule, maintenance algorithm, memory representation, or consciousness model has been selected.

### Second-pass focus

The user returns to “1. Consciousness & Offline Modes (Without Biological Clocks)” for deeper exploration. The starting questions are:

- How should we distinguish biological wake/sleep, engagement with the environment, internal processing/maintenance, and consciousness?
- Which memory or regulatory processes can coexist with interaction, and which benefit from a different operating condition?
- What functions do biological clocks and activity rhythms serve, and which might be retained or abstracted? Treat the source's blanket dismissal as a hypothesis to examine, not an agreed premise.
- How would a sleep-like operating condition differ from simply having no incoming user request?

These are learning questions, not a selected mode taxonomy or a requirement to copy biological timing. Continue with biological mechanisms and evidence before choosing architecture or producing the standalone document.

### Terms we need to keep separate

| Term | Working explanation | Important boundary |
| --- | --- | --- |
| Synapse and synaptic strength | A connection between neurons, and how effectively activity at that connection influences the receiving neuron. | A single synapse is not a memory file; memories involve distributed activity and changes. |
| Plasticity | The capacity of neural connections and circuits to change. | Includes strengthening and weakening; not simply accumulating stronger connections. |
| Memory consolidation | Processes that stabilize memories and/or reorganize how they are represented across systems. | Not a literal file transfer, and not restricted to sleep. |
| Replay / reactivation | Recurrence of neural patterns related to previous experience. | Not an exact audiovisual recording; replay during waking is also documented. |
| Homeostatic plasticity | A family of adjustments helping keep neural activity or responsiveness within useful ranges. | Broader than the sleep-specific synaptic homeostasis hypothesis. |
| Synaptic homeostasis hypothesis (SHY) | A proposal that sleep restores a sustainable net level of synaptic strength after waking-related potentiation. | A hypothesis with supporting and qualifying evidence, not a universal rule that every synapse weakens in every sleep period. |
| Catastrophic forgetting | In learning systems, abrupt loss of previously learned performance as shared parameters are updated for new learning. | Different from retrieval competition, limited context, or intentional removal of external memory records. |
| Operational offline mode | Reduced live work to permit maintenance of some component. | Does not imply a particular subjective state, and need not mean shutting down the entire agent. |

### Does the brain perform memory-related work during sleep?

Yes: sleep is associated with active memory reactivation and reorganization, not merely inactivity or a lack of incoming tasks. Active systems-consolidation accounts describe coordinated interactions among hippocampal and cortical networks, particularly during non-REM slow-wave sleep. Their details and applicability vary across memory tasks and sleep stages [S1, S2].

But sleep is not the only relevant state:

- In rats, previous hippocampal place-cell sequences recur during brief pauses in waking behavior [S3].
- In humans, hippocampal–cortical fMRI correlations during post-learning awake rest predict subsequent associative memory [S4]. This is correlational evidence, not a direct demonstration of neuronal replay or its causal effect.
- Learning and synaptic changes occur while awake. The existence of sleep-related processing does not establish that online mechanisms are unnecessary.

The evidence concerns particular physiological conditions. Sleep, dreaming, wakefulness, anesthesia, coma, and subjective consciousness cannot be collapsed into a single online/offline switch. For now, **operating modes and maintenance** is the safer engineering framing; the nature of consciousness remains outside what these sources establish.

### Synaptic homeostasis: the proposed mechanism

Homeostasis means maintaining a viable operating range, not freezing a system at one unchanging value. The relevant resource in SHY is synaptic strength and its consequences for cells and networks.

A simplified account of the hypothesis [S5]:

1. Waking experience produces a net increase in excitatory synaptic strength across many connections. This is a proposed aggregate tendency, not a claim that every waking change is an increase.
2. Unchecked strengthening would impose cellular costs, affect selectivity, and leave less room for further useful change.
3. Sleep provides a different activity and neuromodulatory environment in which net synaptic strength can be reduced or renormalized.
4. Selectivity matters: some connections may be relatively protected while others weaken. Important relative structure can survive even when overall strength falls.

For intuition only, uniformly rescaling strengths `2, 4, 8` into `1, 2, 4` preserves their ratios while lowering the total. This is not an empirical numerical model. Uniform scaling alone does not improve relative signal-to-noise; selective change is needed to alter those relative contributions, and thresholds can also change their functional impact.

Do not equate **weakening**, **elimination of a synapse**, and **forgetting an entire memory**. They are different descriptions and require different measurements. Do not assume that a stronger or more frequently activated connection is necessarily more important or more accurate.

### Selected evidence and limits

- **Structural support [S6]:** de Vivo et al. measured 6,920 synapses from 12 mice, sampling primary motor and somatosensory cortex. Mean axon–spine interface area was about 18% lower after sleep than after waking conditions. Smaller and medium-sized synapses were more affected; the largest were comparatively spared. This measured a structural correlate of strength in sampled tissue, not a direct 18% loss of memory, a loss of 18% of synapses, or the same synapses followed longitudinally.
- **A counterpoint [S7]:** Cary and Turrigiano found stable functional synaptic strengths across natural sleep/wake periods in sampled juvenile-rat cortical circuits. Their results challenge obligatory, widespread downscaling simply because an animal sleeps; they do not establish that sleep never changes synapses.
- **Conditional support [S8]:** repeated imaging in larval zebrafish found sleep-associated synapse loss dependent on neuron subtype and sleep pressure. Sleep induced at low pressure was insufficient by itself. This measures synapse number in a particular animal/developmental model, not human memory or cortical strength directly.

Working conclusion: sleep can enable synaptic remodeling, but “wake strengthens everything; sleep weakens everything” is not an adequate account. Species, age, brain region, prior experience, measurement, and physiological state matter.

### Consolidation, interference, and homeostasis are related but distinct

- **Consolidation:** how experience becomes stable and integrated into existing knowledge.
- **Interference / forgetting:** whether new learning or competing representations undermine access to, or performance on, older knowledge.
- **Homeostasis:** whether activity and connection strengths stay within a useful operating range.

Replay can contribute to consolidation; renormalization can help maintain capacity. Neither label by itself specifies a complete anti-forgetting mechanism. These processes may interact, but the sleep literature does not establish a ready-made continual-learning algorithm for our architecture.

### Possible engineering implications — not decisions

**Candidate principle:** combine bounded, incremental online updates with background maintenance; reserve exclusive offline work for operations that actually conflict with serving live tasks.

| Kind of work | Possible examples | Why separate it? |
| --- | --- | --- |
| Online / incremental | Record an episode with provenance; update retrieval metadata; track contradictions; maintain bounded transient state. | New experience should remain usable without waiting for a large maintenance cycle. |
| Background / concurrent | Propose summaries, find duplicates, compare related episodes, build a candidate index. | Expensive work may run beside live interaction if resource and consistency constraints allow it. |
| Quiescent / exclusive for an affected component | Validate and publish a reorganized memory snapshot; replace a shared representation; train an adapter if learning is introduced. | Some operations may require isolation, but snapshots and staged publication could avoid whole-agent downtime. |

A normalization analogy is useful only after identifying a variable that can actually become unbalanced: associative graph weights, recency or salience scores, bounded state, or trainable parameters. These are not interchangeable with biological synaptic strength.

Additional boundaries:

- A frozen model is not undergoing parameter overwriting merely because a conversation continues. External memory and retrieval can still degrade for other reasons. Actual weight/adapter learning creates a different retention problem.
- Shrinking all weights in a pretrained model is not a safe SHY implementation. Dense-model inference does not automatically become cheaper when weight magnitudes decrease.
- Summarization, index rebuilding, replay training, and regularization solve different problems; calling all of them “sleep” would conceal useful distinctions.
- Do not treat low retrieval frequency as proof that a memory is disposable. Preserve rare but important observations and source provenance; keep proposed summaries separate from original evidence.
- Replaying or synthesizing memories does not create new independent evidence. Synthetic inferences should remain distinguishable from observations.

### Open questions / next learning steps

1. What will “memory” mean in the first system: external episodes and semantic records, trainable weights, or both?
2. Which changes really conflict with live use, and which can be incremental or published from a separate snapshot?
3. What would trigger maintenance: elapsed time, resource pressure, contradiction backlog, or measured degradation?
4. What should be renormalized, and what useful behavior would that restore?
5. How would we check both retention of older knowledge and use of new knowledge after maintenance?
6. Which benefits are due to reduced interference, and which require a specialized processing mode?

The user reports understanding this first explanation. Keep the open research questions for the eventual deep dive; there is no need to settle implementation before continuing the section-by-section reading.

### Deferred thread: continual learning and knowledge retention

**Status:** parked at the user's request; no literature review or training approach selected yet.

The user sees potential value in a limited amount of ongoing model learning, but wants to investigate whether repeated updates could gradually undermine previously learned knowledge.

Questions to revisit:

- How do direct base-weight updates, separately trained adapters, and external-memory updates differ?
- Can repeated small updates accumulate into significant retention or behavior changes?
- How do we distinguish altered base parameters from knowledge that becomes harder to elicit under an adapter?
- How would we measure retention and preserve a recoverable baseline?

Working distinction for later: training a separate adapter can leave the base weights unchanged while altering the combined model's behavior. Direct fine-tuning or merging updates changes the situation. Small updates should not be assumed harmless merely because each is small.

### Source register

This is a selected first pass, not an exhaustive review. Reading scope is recorded so abstracts are not mistaken for full-paper audits. Search was used for discovery; the readings below were retrieved from the listed article pages.

- **[S1] Rasch, B., & Born, J. (2013).** *About Sleep's Role in Memory.* Physiological Reviews, 93, 681–766. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3768102/). DOI: 10.1152/physrev.00032.2012. **Read:** the active-system-consolidation section, including mechanisms, selectivity, and qualifications. Review, not a single experiment.
- **[S2] Klinzing, J. G., Niethard, N., & Born, J. (2019).** *Mechanisms of systems memory consolidation during sleep.* Nature Neuroscience, 22, 1598–1610. [Publisher page](https://www.nature.com/articles/s41593-019-0467-3). DOI: 10.1038/s41593-019-0467-3. **Read:** public abstract only; full text not audited. An integrative account, not proof of one universal mechanism.
- **[S3] Karlsson, M. P., & Frank, L. M. (2009).** *Awake replay of remote experiences in the hippocampus.* Nature Neuroscience, 12, 913–918. [Publisher page](https://www.nature.com/articles/nn.2344). DOI: 10.1038/nn.2344. **Read:** public abstract only; full methods not audited. Rat place-cell replay during brief waking pauses.
- **[S4] Tambini, A., Ketz, N., & Davachi, L. (2010).** *Enhanced Brain Correlations during Rest Are Related to Memory for Recent Experiences.* Neuron, 65, 280–290. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3287976/). DOI: 10.1016/j.neuron.2010.01.001. **Read:** summary and discussion, including alternative explanations and retention-interval limits. Human fMRI association; not direct causal proof of replay or long-term systems consolidation.
- **[S5] Tononi, G., & Cirelli, C. (2014).** *Sleep and the Price of Plasticity: From Synaptic and Cellular Homeostasis to Memory Consolidation and Integration.* Neuron, 81, 12–34. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3921176/). DOI: 10.1016/j.neuron.2013.12.025. **Read:** summary, the rationale for offline renormalization, down-selection mechanisms, and conclusions/caveats. The authors' review and theoretical proposal; its model claims must not be presented as direct observations.
- **[S6] de Vivo, L., et al. (2017).** *Ultrastructural Evidence for Synaptic Scaling Across the Wake/sleep Cycle.* Science, 355, 507–510. [Open manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC5313037/). DOI: 10.1126/science.aah5982. **Read:** main article, including design, results, and limitations; supplementary methods not audited. Mouse cortical ultrastructure, with four animals per experimental group.
- **[S7] Cary, B. A., & Turrigiano, G. G. (2021).** *Stability of neocortical synapses across sleep and wake states during the critical period in rats.* eLife, 10, e66304. [Open article](https://elifesciences.org/articles/66304). DOI: 10.7554/eLife.66304. **Read:** abstract and discussion, including measurement differences and sleep/wake gating of plasticity. Functional measurements in juvenile rats; not evidence about every brain region or developmental stage.
- **[S8] Suppermpool, A., et al. (2024).** *Sleep pressure modulates single-neuron synapse number in zebrafish.* Nature, 629, 639–645. [Article](https://www.nature.com/articles/s41586-024-07367-3). DOI: 10.1038/s41586-024-07367-3. **Read:** abstract and methods, including repeated imaging and behavioral sleep classification; main results/discussion not fully audited. Larval-zebrafish synaptic-marker measurements; not direct measurement of human synaptic efficacy or memory retention.

## Exteroception and computational interoception

**Status:** the user understands and endorses Section 2's central telemetry principle. Specific metrics and state-update rules remain open; this is not a completed research review of perception or self-monitoring.

### User observation

The crucial point is an internal telemetry stream monitoring scratchpad saturation, processing latency, and uncertainty/error information, and using this self-monitoring to inform cognitive-load and fatigue signals.

### Working interpretation and boundaries

- Treat internal monitoring as input to the control loop, not merely diagnostic logging. It could help guide processing allocation and maintenance decisions.
- Separate observable runtime quantities, such as latency and capacity use, from estimates of uncertainty and error. Error rates need a defined task, evaluation signal, and time window; uncertainty estimates require calibration.
- A computational fatigue variable would be a designed control state derived from relevant observations, not a direct measurement of biological exhaustion or subjective feeling. The mapping still needs definition and validation.
- This agreement does not select input modalities, endorse dropping particular sensory channels, or assume every model exposes the same internal telemetry.

### Later coverage

The source introduces cognitive load/fatigue in Section 3 (lines 19–29), then proposes LLM telemetry mappings under “Step C: Direct Telemetry for Epistemic Channels & Fatigue” (lines 746–754). Revisit concrete metrics and feedback rules there rather than expanding them now. In particular, those later entropy-based proposals are not established measurements of confusion, uncertainty, or fatigue merely because the source presents them that way.

## Cognitive routing, load, and fatigue

**Status:** the entire source routing discussion (lines 104–179, Parts 1–3) was read and understood by the user. A selected-source research draft and twelve-slide deck have now been created and checked; these new artifacts await user review. Computational/architectural realization remains explicitly deferred.

### User observation

Fatigue returns as a connection between the earlier operating-mode and telemetry discussions and the routing model. The user is comfortable retaining representational overload as a candidate mechanism while reading on, without deciding whether it is a partial or complete explanation.

### Working connection and questions

Candidate control loop: competing representations or processing pressure → internal observations and load estimates → possible adjustment of processing or maintenance. This is a design hypothesis, not an established biological or LLM mechanism.

- Keep resource occupancy distinct from interference or degraded performance. A busy or large workspace is not by itself proof of harmful overload.
- Revisit whether a fatigue variable would summarize current load or represent a separate state that accumulates and recovers over time.
- Do not assume that overload explains every form of human fatigue, or that the salience network necessarily generates all fatigue and forces a specific mode switch.
- Retain the overload explanation for investigation without committing either to its completeness or to a particular implementation.

### Later coverage

The fuller network discussion at source lines 104–179 develops and qualifies the opening account of executive/default-network opposition, including their cooperation. Do not treat the opening seesaw description as a fixed binary routing rule.

The memory block (lines 180–275) develops interference and complementary learning, while the LLM block (especially lines 710–754) proposes fatigue-related telemetry. These are destinations to revisit, not a comprehensive validated theory of fatigue; the proposed entropy-to-fatigue mappings remain unverified.

### Full routing discussion reading checkpoint

**Scope clarification:** the user's “read and understood everything” referred to the whole routing/attention discussion at source lines 104–179, not just Part 1. This includes the original 2011 account, the subsequent developments, and the proposed architectural implications/routing configurations. Do not ask the user to reread Part 2 as if it were still pending.

**User takeaway:** the topic is interesting and understood; the user has no additional comments to add at this checkpoint.

**Deferred architectural question:** how should these functions take computational form? The user sees the translation as possible but does not yet have an implementation picture. Revisit during research and architectural design/synthesis; no component mapping is selected now.

**Evidence status:** a selected-source pass now supports the standalone draft, with corrections to the chronology, subdivision labels, directed-influence interpretation, and clinical/fatigue generalizations. The [source audit](cognitive-routing-plan.md) records exactly what was read. Menon (2011) was checked through its indexed abstract/record, not the complete review; this limitation is disclosed in the research document.

**Research outputs:** [Cognitive routing and attention](../research/cognitive-routing-research-document.html) has ten sections and eleven selected references; its [companion deck](../research/cognitive-routing-presentation-deck.html) has twelve slides. They use the existing v2 design plus an opt-in comparison-diagram component. Structural, browser, navigation, and print checks are recorded in the audit; no controller or neural-to-software mapping is claimed as validated.

**Continuation:** the user may review these drafts or continue the source reading. The next major source block is memory/complementary learning systems (lines 180–275); no next assignment or approval of the new drafts is assumed.

## Memory retrieval and transformer representations

**Status:** opening Section 4 discussed. The user accepts the refinement distinguishing attention weights from the representations being combined. The broader links to embeddings, vector databases, KV-cache reuse, and latent representations remain for later investigation; no memory implementation has been selected. A selected-source research document and twelve-slide deck now exist as drafts awaiting review, with the source audit and procedure checklist recording the evidence limits.

### User hypothesis

The long-term-memory → working-memory account of reconstructive retrieval suggests a connection between compressed semantic information and an LLM's attention matrices or contextual latent representations at a particular processing moment. Investigate whether these internal representations could help retrieve, reinstate, or integrate memories, rather than assuming that all memory must be supplied as text.

The user clarified that these connections span the other parts of the memory loop as well: vector databases, key/value-cache reuse, attention mechanisms, and embeddings should all be considered. Do not narrow the observation to only the final retrieval step or equate a biological memory tier with one software component.

### Candidate mechanisms across the memory loop

| Mechanism | Possible role to investigate |
| --- | --- |
| Embeddings | Represent experiences, concepts, and retrieval cues numerically for matching. |
| Vector databases | Index persistent episodic or semantic records for similarity-based retrieval, alongside content and metadata. |
| Attention | Select and combine information available to a computation, potentially including retrieved representations. |
| Key/value cache | Reuse representations of previously processed context within compatible inference workflows. |
| Hidden/residual-stream states | Provide contextual representations in which retrieved information may be integrated or from which features may be read. |

These roles can overlap, but representation, indexed storage, access/integration, and runtime reuse are not interchangeable. A vector database can serve different memory timescales; similarity indexing alone does not implement consolidation, exact recall, or biological pattern completion. Study which properties each memory function needs before choosing a component.

### Minimal technical distinctions

- In a standard attention head, input-dependent attention weights describe how positions combine information. Schematically, `attention output = attention weights × value representations`. The attention matrix alone is not a self-sufficient record of the semantic content being combined.
- Hidden/residual-stream states and value representations carry contextual features, but their meaning depends on model, layer, position, and context. A single vector is not automatically a complete snapshot of the model or an independently reusable memory.
- Learned parameters, runtime attention weights, and contextual activations are different objects. Learned query/key/value projection matrices should not be confused with the input-dependent attention matrix.
- A key/value cache preserves some runtime representations for reuse within supported inference workflows; this does not automatically make it durable, compact semantic memory across unrelated contexts.
- The biological description of “compressed semantic nodes” is an abstraction, not an established identification with a particular Transformer tensor. The possible analogy concerns cue-dependent reconstruction and information integration, not identical mechanisms.

These are preliminary technical clarifications. A dedicated investigation of latent memory, attention-based retrieval, and their evidence is deferred.

### Questions to revisit

1. Is an internal representation useful as a retrieval key, the stored memory content, or the place where retrieved content is integrated?
2. What would be stored or reinstated: contextual embeddings, selected hidden states, key/value representations, or another learned memory format?
3. Which information survives that representation, and how could retrieval or reconstruction quality be evaluated while retaining source provenance?
4. How sensitive is reuse to context, token positions, model layers, and model/version changes?
5. Which parts of encoding, episodic storage, consolidation, and retrieval need external records, vector indexing, runtime caches, or learned representations—and which require additional mechanisms?

### Later coverage

The memory expansion at source lines 180–275, especially lines 202–226, develops activated long-term memory, indexing, and reconstructive retrieval. The LLM bridge at lines 704–831 discusses hidden-state readout and steering, mainly in connection with affect and persistent state. It is relevant but does not establish attention matrices as reusable semantic memories or provide a validated latent episodic-memory design.

Keep this bridge linked to both the memory study and the later LLM–state study. The separate weight/adapter-learning and retention question remains parked; this observation does not require choosing parameter updates now.

### Proposed three-tier technical parallel (working hypothesis)

**Status:** the user consolidates the source's memory loop into a concrete engineering hypothesis: STM → Redis vector cache, LTM → vector database, WM → model context. This is a useful design vocabulary, not a demonstrated equivalence. The storage components are plausible; the lifecycle algorithms are the harder and still unresolved part.

**Research outputs:** [Memory systems research](../research/memory-systems-research-document.html) · [12-slide deck](../research/memory-systems-presentation-deck.html) · [source audit](memory-systems-plan.md) · [procedure checklist](memory-procedure-checklist.md). The drafts distinguish source claims, primary evidence, engineering candidates, and staged experiments; no implementation is selected.

| Source tier | Candidate implementation | Useful correspondence | Important limit |
| --- | --- | --- | --- |
| WM | active model context + KV cache + retrieval/control pointers | Holds currently available information and supports selection and binding | A token window is not a 3–7-item biological WM; KV cache is runtime reuse, not a durable memory tier. |
| STM (labile episodic store) | Redis vector index/cache with TTL and episode metadata | Provides a fast, recent, hot episodic index and a possible quarantine area for novel episodes | Cache eviction is not biological pattern separation; it needs orthogonal/sparse episode keys, provenance, salience, promotion, and an explicit lifecycle. |
| LTM (structural connectome) | durable vector DB + relational graph + model weights/adapters | Supports durable declarative records, semantic retrieval, and learned structure | A vector DB is not slow plasticity or a connectome; similarity search alone does not implement generalization, procedural knowledge, or consolidation. |

What the loop needs beyond the three stores:

- **Episode record contract:** id, timestamp, session/context, entities, embedding, source, salience, schema-consistency estimate, status (`labile`, `consolidated`, `archived`), and version.
- **Pattern separation:** explicit episode identity and orthogonal/sparse keys; top-k similarity alone can blur near-duplicate experiences.
- **Retrieval and reconstruction:** query the hot store first, then the durable store; reconstruct a cue-dependent episode and retain provenance.
- **Consolidation:** an offline worker interleaves episodes with existing knowledge, abstracts or resolves conflicts, updates the graph/vector records and possibly an adapter, then promotes and garbage-collects the labile index. This is not merely a file move.
- **Schema bypass:** check consistency against an existing schema; fast-track consistent information and quarantine surprising/conflicting information. The schema representation and the reliability of that check remain open. The source's “bypass” means bypassing slow consolidation, not bypassing validation.
- **Transitive inference:** use graph relations or recombinatorial replay for chains such as AB + BC → AC; label inferred links as inferred and validate them. Vector similarity is not transitive, and not every association is a transitive relation.
- **Reconsolidation:** a prediction error can reopen a retrieved record for a bounded, versioned update; retain provenance and support rollback.
- **Episodic control:** allow bounded direct lookup from the labile store for one-shot decisions, without treating that lookup as a general policy.

A minimal experiment sequence would test encoding and interference first, then schema-consistent versus schema-violating consolidation, then transitive inference and reconsolidation, and finally retrieval into context. Useful measures include exact recent-episode recall, interference between near-duplicates, schema classification accuracy, inferred-link accuracy and false-link rate, retention/drift after consolidation, provenance, latency, and storage cost. Choosing Redis, a particular vector database, or a graph store is premature until those behaviors are specified.

## Social homeostasis, set-points, and motivation

**Status:** exploring the opening Section 5. A selected source pass clarifies the set-point concept and its limitations; no social controller, personality classification, or biological necessity for artificial agents has been established.

### User questions and priorities

- What does an internal social set-point mean? How does it relate to mixed or context-dependent social preferences, rather than a simple introvert/extrovert label? Retain this research question without constructing a personal psychological profile.
- The detector, comparator/control, and effector functions look relevant to the architecture and deserve consideration.
- The Tomova isolation/fasting study and Eisenberger/Lieberman social-exclusion study are interesting background evidence, but the user does not currently regard them as direct implementation drivers. This is a relevance judgment, not a dismissal of the studies.
- Relational/epistemic regulation, curiosity, and cognitive coherence are motivating design directions. Distinguish that interest from a claim that their necessity or implementation has already been validated.

### What the set-point means

Within the proposed social-homeostasis framework, a set-point is a reference for an expected or sufficient quantity/quality of connection. The system compares its estimate of current connection with that reference and may recruit responses to a mismatch [S9].

A scalar teaching approximation is `social mismatch = target connection − estimated connection`. This is not a discovered numerical variable in the human brain, a personality test, or a selected equation for our implementation. The reference may be better represented as an acceptable range or multiple targets rather than a single fixed quota.

Matthews and Tye explicitly propose flexibility with internal needs, environment, and social history. Their Figure 3 discusses different weighting of quality and quantity and integration over time. The identity and organization of the detector/control circuitry remain conjectural; expectations might be processed at different stages. Gemini overstates both the anatomical certainty and the claim that this explains introversion versus extraversion [S9]. The 2019 review is in Annals of the New York Academy of Sciences, not Nature as stated in the source chat.

### Personality, current state, and competing needs

A broad personality trait describes a habitual pattern, not necessarily how a person behaves or feels in every situation. Whole Trait Theory describes distributions of momentary states and situational influences [S11]. Extraversion-related behavior, desire for connection, preference for a particular kind of interaction, and processing cost should not be collapsed into one variable.

As an illustrative possibility, strong interest in connection can coexist with a wish for quieter surroundings or private processing during the same event. This does not establish a cause for anyone's experience or mean that a person simultaneously occupies both extremes of one identically defined measurement scale.

Bales et al. discuss personality and culture as potential influences on social set-points. They also emphasize that estimating those targets requires repeated observations across contexts and timescales. A single stable "introversion number" is not a demonstrated explanation of social need [S10].

### Candidate architectural interpretation — not a specification

| Function | Possible computational role |
| --- | --- |
| Detector | Estimate recent interaction quality, mutual understanding, or unmet coordination needs, retaining uncertainty and provenance. |
| Comparator | Compare those estimates with explicit, context-sensitive goals or acceptable ranges, alongside processing cost and other priorities. |
| Effectors | Select appropriate responses such as clarification, evidence gathering, waiting, reflection, or a bounded request for input. |

Keep need/goal signals distinct from the resources available to satisfy them: a strong reason to communicate need not imply immediate capacity or permission to initiate interaction. Multiple goals may coexist rather than cancelling on one sociality axis.

Boundaries for later design:

- The human studies can motivate or constrain biological claims, but they do not supply software parameters or prove an artificial agent needs loneliness, social pain, or an autonomous demand for company.
- External epistemic calibration can come from observations, tools, experiments, and reliable sources, not only other agents. Social agreement alone is not evidence of truth.
- Mutual understanding is different from agreement. A controller should not turn alignment into sycophancy or pressure to keep a user engaged.
- Cognitive coherence is not sufficient for accuracy: a consistent model can be false. Contradictions should be investigated against evidence, not merely removed.
- Any implemented social/relational drive should respect user boundaries and allow quiet operation when interaction is unavailable or unwanted. Do not assume an aversive human-like state is necessary to obtain useful feedback behavior.

### Later coverage and open questions

The source expands core affect at lines 280–296, social homeostasis at lines 306–336, and curiosity at lines 338–360. Revisit the detailed mechanisms there rather than treating this checkpoint as the whole motivation study. The later strong claims about compulsory social homeostasis and chronic set-point adaptation still require independent checking.

Open questions: which relational and epistemic goals do we actually need; how are quality, targets, uncertainty, and time windows defined; which targets should adapt; and how should conflicting goals and resource limits influence action?

### User synthesis after Parts 1–3

**Status:** the affect / social-homeostasis / curiosity block is read. The user sees useful parallels with the emotion, routing, memory, gating, and telemetry research, but treats the interactions as hypotheses to test and measure. No valuation controller or deficit port is selected.

- **Parts 1–2:** core affect and social homeostasis are useful functional parallels; self-referential bias and limited early interaction require calibration; deficits need a deliberate decision about whether and how to port them.
- **Part 3:** curiosity and learning progress are promising but nontrivial; the Goldilocks/Wundt structure needs operational definitions.
- **Overall:** architecture choices must consider the model (“brain”), stores, and processes, and use their characteristics efficiently rather than reproducing every biological module.

**User clarification:** the system is intended to be an actor with endogenous goals, not a machine whose goals are supplied only from outside. Biological needs and mechanisms—including social hunger—are therefore legitimate candidates to replicate and test. The distinction is between **mechanisms** and **fixed states**: port the detector/comparator/effector loop, adaptive set-points, and resource constraints, not a hardcoded “lonely,” “depressed,” or “socially satisfied” state.

Working interpretation: social hunger can motivate calibration, feedback-seeking, or alignment repair, but it should be context-sensitive, bounded, and non-coercive. A social homeostat cannot guarantee truth; agreement is not evidence. Early low-interaction systems should not treat self-generated outputs as independent evidence, and learning progress is a better exploration signal than raw surprise only when the error metric, time window, and learnability gate are defined.

**Research outputs:** [Valuation, gating, and modulation research](../research/valuation-gating-modulation-research-document.html) · [12-slide deck](../research/valuation-gating-modulation-presentation-deck.html) · [source audit](valuation-gating-modulation-plan.md). The drafts cover core affect, social homeostasis, curiosity, basal-ganglia gating, neuromodulators, and the mechanisms-versus-states distinction.

### Selected source register for this checkpoint

These are theory/review readings, not a complete audit of every experiment they cite. The Tomova and Eisenberger studies were not independently reread at this checkpoint.

- **[S9] Matthews, G. A., & Tye, K. M. (2019).** *Neural mechanisms of social homeostasis.* Annals of the New York Academy of Sciences, 1457(1), 5–25. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7593988/). DOI: 10.1111/nyas.14016. **Read:** abstract; the social-homeostasis framework and Figure 1; flexibility and Figure 3; subjective social experience. Explicitly a proposed functional model with unresolved neural implementation.
- **[S10] Bales, K. L., et al. (2023).** *Individual differences in social homeostasis.* Frontiers in Behavioral Neuroscience, 17, 1068609. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10036751/). DOI: 10.3389/fnbeh.2023.1068609. **Read:** personality/culture and methodological challenges/approaches. Supports investigating individual differences and context; does not establish a simple trait-to-neural-set-point mapping.
- **[S11] Fleeson, W., & Jayawickreme, E. (2015).** *Whole Trait Theory.* Journal of Research in Personality, 56, 82–92. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4472377/). DOI: 10.1016/j.jrp.2014.10.009. **Read:** abstract/introduction and the descriptive-trait section on personality states and their distributions. A framework and review of trait/state evidence, not an assessment of the user's personality; underlying primary studies were not independently audited here.

## Experimental stance and latent readouts

**Status:** working ideas raised during Section 5, not a selected model, readout, training method, or control policy. The user explicitly accepts “motivating” rather than “validating,” but clarifies that deliberately replicating selected biological mechanisms is part of the experiment. The assistant's earlier preference for avoiding imposed psychology was too broad; the concern is unnecessary restriction of expression. The user has confirmed this clarification; individual mechanisms and prompting choices remain open.

### User direction and clarification

- Investigating information extractable from an LLM's latent representations appears central to the proposed system. Interaction quality is one candidate; the user recognizes possible bias toward this intuition.
- Certain biologically motivated mechanisms should be deliberately replicated. Their being imposed does not make them invalid experimental components.
- Avoid unnecessary actions or instructions that overly prescribe how the model and architecture express themselves. Allow behavior to develop through the implemented mechanisms and interaction, while recognizing that those mechanisms inevitably influence behavior.
- Shorter, simpler prompts seem preferable to the user as an initial intuition. Keep alternatives open: this is not a universal rule or an agreed prompt policy.
- The scope of “finding its own rights and wrongs” needs clarification: developing preferences/valuation is not automatically the same question as permissions for real-world actions. Do not record unrestricted autonomy, a specific moral framework, or particular experimental boundaries as agreed.

### What latent readout would and would not establish

The working hypothesis is that representations may contain useful information about relevance, coherence, agreement/conflict, or other interaction-related properties. Replace “any model surely has a reliable interaction-quality representation” with model- and task-specific questions.

Keep these steps distinct:

1. **Encoding:** information is present in activations.
2. **Decoding:** a readout predicts an operationally defined target on held-out examples.
3. **Construct validity:** that target actually captures what we mean by interaction quality, rather than politeness, agreement, length, or another shortcut.
4. **Causal relevance:** the representation participates in the model's behavior; predictive access alone does not demonstrate this [S13].
5. **Control usefulness:** using the readout in a feedback loop improves relevant outcomes without destabilizing behavior.

Interaction quality may need several estimates rather than one scalar. Textual fluency, task progress, factual correctness, mutual understanding, and user preference need not agree. A readout cannot directly know private user experience or outcomes absent from its evidence. Runtime telemetry and external feedback remain complementary sources, not quantities that must all be inferred from language-model activations.

### Selected evidence and limits

- **[S12] INSPECTOR / Representation-as-a-Judge:** a 2026 preprint predicts teacher-model rubric scores from small-model representation features. Its main tasks are reasoning benchmarks, and its labels come from an LLM judge. Fine-grained cross-dataset score transfer is limited. This supports investigating task-specific evaluative readouts, not a universal measure of real-world conversation quality.
- **[S13] Probe interpretation:** successful probing does not establish that the model uses the decoded property for its task. Careful controls are necessary.
- **[S14] Contrastive Activation Addition:** selected behaviors can be changed by activation interventions in the studied Llama 2 Chat settings. Reading a property and steering behavior are different experiments; this does not validate arbitrary social or emotional variables.

### Candidate experimental comparisons — deferred, not implementation

1. Identify the biological function or mechanism being deliberately implemented and the question its implementation tests. Mechanistic replication and observing resulting expression are compatible aims.
2. Use appropriate controls to distinguish the effect of that mechanism from prompt prescriptions, inherited model behavior, and other architectural changes. Observation-only conditions are useful comparisons, not a rule prohibiting biological interventions.
3. Evaluate readouts across new dialogues, topics, styles, and contexts; check shortcuts and compare against simpler text/context/telemetry baselines. Keep pre-response prediction distinct from judging an already completed response.
4. Retain failures and alternative interpretations. An imposed mechanism should be reported as imposed; behaviors arising from its interaction with the rest of the system can still be studied as emergent dynamics. A probe detecting an injected direction alone does not establish an independently arising state.

The role of human-readable categories, including the existing 27-channel vocabulary, remains open: they might be controls, readouts, or both. Do not infer that the user wants them to be observational only. A separate readout can be trained without changing the base model; coupling it to a reward or controller is another experimental choice, not inherently a mistake.

### Biological structure and expressive freedom

The intended distinction is between implementing biologically motivated mechanisms and unnecessarily scripting their exact behavioral expression. Mechanisms will themselves influence expression; the goal is not an architecture without constraints or influence.

Pretraining, post-training, memory choices, environments, feedback, and readout labels also introduce prior structure. Make those assumptions explicit and test their contribution rather than claiming a blank-slate system.

Prompt simplicity is a provisional hypothesis. Distinguish prompt length from prescriptiveness: a long prompt can supply useful context, while a short one can still dictate behavior. Later comparisons should account for necessary information and interface instructions, not assume that the shortest prompt must win. No concrete prompt configuration is selected now.

Distinguish enabling mechanisms, hypothesis-laden architectural choices, deliberate behavioral scripting, and experimental permissions/limits. Privacy, consent, resources, and external-action boundaries concern conducting the experiment; their concrete scope remains to be discussed rather than treated as agreed psychological requirements.

### Later coverage

Return to this checkpoint with the LLM bridge at source lines 704–831, especially representation reading at lines 722–754 and steering at lines 756–792. For proposed injection and fixed mappings, ask which implement intended biological mechanisms and which unnecessarily prescribe expression; assess them with suitable controls rather than rejecting interventions by default. The dedicated latent-readout and feedback investigation remains for later.

### Source register and reading scope

- **[S12] Li, Z., et al. (2026).** *Rethinking LLM-as-a-Judge: Representation-as-a-Judge with Small Language Models via Semantic Capacity Asymmetry.* [arXiv:2601.22588v1](https://arxiv.org/html/2601.22588v1). **Read:** abstract, annotation procedure, feature extraction/probing (including Appendix B), limitations, and out-of-distribution Appendix G; metadata also checked with `hf papers info`. First-version preprint reading, not an independently replicated result or a claim about every model. Rubrics and teacher-model labels shape the learned readout.
- **[S13] Ravichander, A., Belinkov, Y., & Hovy, E. (2021).** *Probing the Probing Paradigm: Does Probing Accuracy Entail Task Relevance?* EACL, 3363–3377. [ACL record](https://aclanthology.org/2021.eacl-main.295/). DOI: 10.18653/v1/2021.eacl-main.295. **Read:** abstract and bibliographic record only; full experiments not audited. Relevant methodological warning, not direct evidence about social-quality readouts.
- **[S14] Rimsky, N., et al. (2024).** *Steering Llama 2 via Contrastive Activation Addition.* ACL, 15504–15522. [ACL record](https://aclanthology.org/2024.acl-long.828/). DOI: 10.18653/v1/2024.acl-long.828. **Read:** abstract and bibliographic record only; detailed intervention/generalization results remain to be reviewed. A candidate for the later steering study, not evidence of a complete emotion interface.

## Cognitive action selection and gating

**Status:** the user has read the dedicated Layer 6 expansion and considers the basal-ganglia/PBWM gating process crucial and interesting. The source destinations are identified; biological claims and implementation details have not been independently reviewed at this checkpoint.

### User checkpoint

The transferable idea is a **default brake plus selective release**: keep working-memory content and candidate outputs suppressed by default, open a gate for a relevant item, veto lower-value competitors, and apply a global hold when conflict or interruption is high. Input gating and output gating are separate: what enters the workspace is not the same decision as what is allowed to drive speech or action. This is a strong candidate control layer for the architecture, but it should not be treated as a literal three-pathway software controller or as proof that the biological circuit maps directly to an LLM.

### User takeaway

Candidate action preparation and inhibitory gating address important functions missing from the original framing. Retain both for the architecture study rather than treating the absence of physical movement as making action selection irrelevant.

### Later coverage

- **Opening overview:** “Layer 6 Abstracted: Cognitive Action Selection & Output Gating,” lines 81–87, introduces candidate action buffers and inhibitory threshold gating.
- **Dedicated expansion:** “Part 1: Layer 6 Abstracted — The Basal Ganglia as a Cognitive & Output Gate,” lines 370–401. This discusses maintaining versus updating working memory and holding candidate outputs before release.
- **Proposed model:** “The PBWM Model,” line 380 onward, presents competition and the source's Go / No-Go / global-hold pathway account. Treat these as claims to examine against the cited literature, not already verified anatomical or software equivalences.
- **Additional distinction:** “Input Gating vs. Output Gating,” lines 392–400, separates admitting/updating workspace content from allowing selected content to drive execution or communication.
- **Runtime return:** “Basal Ganglia Output Gating,” lines 816–818, places internal-versus-external output in the proposed LLM loop.
- **Duplicate:** the dedicated Layer 6 text recurs at lines 484–515 as part of the already identified repeated block; it is not additional evidence or a new deep dive.

Candidate preparation is expanded through competition and selection, but the source does not provide a complete implementation of a candidate buffer. Questions about parallel versus sequential preparation, selection criteria, workspace maintenance, and release policy remain for later.

This is compatible with deliberately implementing a biologically motivated mechanism while avoiding scripts that predetermine the exact expressed response. No particular gate algorithm or threshold is selected now.

## Global modulation and latent-derived control signals

**Status:** the user has read the Layer 7 expansion and sees it as important for porting modulatory variables into the disembodied architecture. The user sees direct usage for dopamine, less direct usage for norepinephrine, even less for serotonin, and least for acetylcholine; all suggest candidate variables, processes, or directions rather than literal chemical equivalents. No reliable probe or control implementation has been established.

### User hypothesis and checkpoint

Explore whether dopamine-, norepinephrine-, and serotonin-inspired factors can be extracted from an LLM's latent representations. Acetylcholine seems to the user like a somewhat different kind of “check,” but still potentially applicable; the meaning and mechanism of that check remain to be explored.

The user's current ranking is pragmatic rather than established: dopamine has the clearest candidate role in value, prediction error, and gating; norepinephrine is less direct; serotonin and acetylcholine are still more speculative. All four can suggest variables, processes, or control directions, but none should be treated as a one-to-one LLM parameter.

### Distinctions needed now

- Biological names are shorthand for candidate computational functions here, not evidence that an LLM contains measurable neurotransmitter levels or a corresponding single latent coordinate.
- A useful representation, a calibrated readout, and a state used to modulate computation are different things. Some control signals may combine latent estimates with persistent state, direct telemetry, or observed outcomes rather than being extracted from one activation snapshot.
- For example, a reward-prediction-error analogue requires a comparison of an outcome with an expectation; reading an apparent value-related feature alone does not establish that comparison.
- An acetylcholine-inspired balance between incoming evidence and retrieved priors could be one interpretation of “check.” Weighting information is not an independent guarantee that it is true. Do not record this interpretation as already accepted by the user.

Candidate connection: `latent estimates + observations + persistent state → modulatory state → effects on processing`. This is a possible design to investigate, not a requirement that every factor use the same extraction pipeline.

| Biological shorthand | Computational topic to investigate, not an established identity |
| --- | --- |
| Dopamine | Outcome-versus-expectation signals, value, and their relationship to motivation or gating. |
| Norepinephrine | Unexpected change, reorientation, and adaptive gain or selection behavior. |
| Acetylcholine | Weighting incoming evidence against retrieved information; possible encoding/retrieval-mode control. |
| Serotonin | Horizon, restraint, or continuation decisions; do not equate temporal discounting with token budget by default. |

Treat the source's one-to-one mappings as hypotheses to check. Distinguish an implemented biological analogue from a claim that its exact state already exists in the unmodified LLM.

### Later coverage

- **Dedicated expansion:** “Part 2: Layer 7 Abstracted — Neuromodulators as Meta-Parameters (Doya's Framework),” lines 402–459. The individual sections begin at dopamine 408, norepinephrine 422, acetylcholine 438, and serotonin 448.
- **Duplicate:** lines 516–573 repeat this expansion; they are not additional evidence.
- **Affect-to-control proposals:** lines 686–692 suggest hand-authored mappings from emotion channels to modulatory factors. Assess whether those rules fit the intended biological mechanism and experimental question rather than assuming they are necessary or empirically validated.
- **LLM return:** “Deep Look at Mechanism 2: Neuromodulators Mapped to Transformer Math,” lines 784–792, proposes inference-time controls. These are engineering proposals, not proof of directly readable chemical equivalents.

Keep this topic linked to latent-readout reliability, persistent state, gating, and the user's distinction between intentional biological replication and unnecessarily scripted expression. The detailed biological and implementation study remains for later; no new literature audit was performed at this checkpoint.
