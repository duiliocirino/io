# Memory procedures — transferability checklist

## Scope

Checked the memory deep dive (source lines 180–275) and adjacent memory-related passages (especially lines 596–612 and 704–831). This checklist separates procedures the source explicitly describes from biology-adjacent candidates. “Transferable” here means a candidate design analogy, not a validated equivalence.

## Explicitly described in the memory deep dive

| Procedure | Source description | Engineering candidate | Caveat |
| --- | --- | --- | --- |
| Complementary fast/slow systems | Separate fast episodic learning from slow overlapping semantic/procedural learning to avoid catastrophic interference. | Separate a hot episodic store from durable records and slow parametric updates. | CLS is a framework, not a universal architecture. |
| Working memory as activated LTM | WM holds pointers to existing LTM nodes rather than copying full records. | Retrieval references/pointers into durable records; assemble an active context. | A context window is not literal pointer slots. |
| Activity-silent WM and reactivation | Only one item is actively firing; others stay “warm” and are reactivated by a ping. | Cached/warm representations reactivated on demand. | KV cache is only a rough analogy; biological calcium maintenance is not replicated. |
| Focus of attention | One item is actively selected while the other held items remain warm. | An active slot or attention focus; reinsert other items when needed. | Capacity and selection policy are task-dependent; not a fixed 3–7 software limit. |
| Salience tagging and one-shot episodic write | Novel, emotional, or high-value content is written quickly into the labile store. | Novelty/importance score; write an episode to a hot index. | Salience detection and its thresholds are unvalidated. |
| Hippocampal indexing | A lightweight coordinate index records which LTM nodes and sensory features were co-active at time t. | Episode index pointing to content, entities, context, and provenance. | Not a literal hippocampal coordinate system. |
| Pattern separation | High-dimensional, sparse, orthogonal codes prevent similar episodes from interfering. | Explicit episode IDs plus orthogonal/sparse keys or projections. | LLM embeddings are dense; separation must be deliberate. |
| Pattern completion | A partial cue reactivates the full episode index through an auto-associative loop. | Cue-based associative reconstruction, graph completion, or associative memory. | Similarity search alone is not pattern completion. |
| Reconstructive retrieval | The index reactivates distributed LTM nodes, which WM reconstructs. | Reconstruct the episode from index, durable records, and current context. | Not verbatim playback; reconstruction can distort. |
| Interleaved replay and consolidation | Offline replay mixes new episodes with older patterns and slowly updates LTM. | Background consolidation worker; interleave new and old records; slow updates. | Sleep/sharp-wave ripples are biological evidence, not a required implementation schedule. |
| Garbage collection | After consolidation, the labile index can be cleared. | Promote/archive labile records and apply a retention policy. | Biological forgetting is not simple deletion. |
| Schema bypass | Schema-consistent information is fast-tracked; schema-violating information is quarantined and slowly replayed. | Explicit consistency check; fast-track or quarantine. | The animal evidence does not establish a reliable LLM schema classifier. “Bypass” means bypassing slow consolidation, not validation. |
| Generative replay and transitive inference | Recombine AB and BC episodes into ABC/AC, producing synthetic insights. | Graph inference or recombinatorial replay; label and validate inferred links. | Vector similarity is not transitive; generated links can be false. |
| Episodic control | WM can query the labile store directly for one-shot decisions. | Bounded direct lookup from the hot store for novel situations. | Not a general policy; avoid treating one episode as a rule. |
| Reconsolidation | Prediction error makes a retrieved LTM trace labile; WM edits it and re-locks it. | Versioned, prediction-error-triggered update with provenance and rollback. | Not every retrieval triggers reconsolidation; conditions and windows are uncertain. |

## Adjacent source procedures worth carrying over

- **Input/output gating (PBWM):** decide what enters working memory and what is allowed to leave as output. Engineering: a controller around the active context; do not confuse a token window with gating.
- **State- and affect-biased retrieval:** current network mode, emotional state, and salience bias which memories are retrieved. Engineering: context/affect tags and query weighting.
- **Acetylcholine-like sensory-versus-memory weighting:** shift attention toward live input or internal priors. Engineering: attention/logit bias; the biological mapping is speculative.
- **Prediction error and surprise:** trigger encoding, quarantine, schema accommodation, or reconsolidation. Engineering: explicit mismatch checks and event records.
- **Offline consolidation and synaptic homeostasis:** scheduled maintenance, replay, and possible pruning/renormalization. Adjacent to memory, not identical to consolidation; the sleep evidence is mixed across conditions.

## Additional biology-adjacent candidates not explicit in the memory block

- **Encoding specificity / contextual cues:** retrieval is strongest when the cue matches the encoding context. Engineering: store context and use it in retrieval.
- **Source monitoring / provenance:** track whether a memory came from observation, inference, or another source. Engineering: provenance fields and verification.
- **Procedural memory / habit learning:** skills and policies are not just declarative records. Engineering: parametric weights, adapters, or policy modules—not only a vector database.
- **Spacing and interleaving:** distribute learning across episodes rather than concentrating it. Engineering: consolidation schedules and mixed replay.
- **Retrieval-induced forgetting:** retrieving one memory can weaken competing memories. A caution, not necessarily a desired procedure.
- **Constructive episodic simulation:** use episodic memory to generate future or counterfactual scenarios. Engineering: generative recombination; not the same as consolidation.
- **Temporal order and sequence encoding:** episodic memory includes order and duration. Engineering: timestamps, sequence metadata, and event logs.
- **Selective replay/consolidation:** not every episode is replayed or consolidated. Engineering: prioritization by salience, relevance, and schema status.
- **Adaptive forgetting/pruning:** resource management and interference control. Engineering: retention policy, archival, and deletion—not equivalent to biological forgetting.
- **Metacognitive confidence:** estimate reliability of a retrieved memory. Engineering: confidence and validation fields; not a settled biological procedure.

## What not to claim

- Redis is not STM; a vector database is not LTM; a context window is not WM.
- Schema bypass is not a validated LLM algorithm.
- Transitive inference does not follow from vector similarity.
- Reconsolidation is not a simple database edit.
- Not every biological memory procedure has a direct software equivalent.

## Next use

This checklist can become the procedure appendix of a memory research document. The document should separate source claims, primary evidence, engineering hypotheses, and experiments; the companion deck should present the same distinctions without implying that the mapping is already implemented.
