# Memory systems — research plan and source audit

## Scope and outputs

Create a standalone learning/research document and companion newcomer-friendly presentation about memory systems and transferable biological procedures. Keep practical architecture open: candidate substrates such as Redis, vector databases, graph stores, and model context are hypotheses, not validated equivalents.

- Research: `docs/research/memory-systems-research-document.html`
- Presentation: `docs/research/memory-systems-presentation-deck.html`
- Procedure checklist: `docs/notes/memory-procedure-checklist.md`
- Keep the existing emotions and routing pages intact.
- Reuse the v2 research/deck layouts, navigation, offline assets, and print behavior. Add no new design component unless the content requires one.

## Working outline

1. Memory as a lifecycle, not a storage lookup.
2. Stability–plasticity and catastrophic interference.
3. Three functional tiers: WM, labile STM, LTM.
4. Working memory as activation, maintenance, and gating.
5. Episodic encoding: hippocampal indexing, pattern separation, salience.
6. Retrieval: pattern completion, reconstruction, encoding specificity, source monitoring.
7. Consolidation: interleaved replay, sleep/rest evidence, synaptic homeostasis, garbage collection.
8. CLS 2.0: schema bypass, generative replay/transitivity, episodic control, reconsolidation.
9. Broader transferable-procedure checklist.
10. Engineering candidates: hot index, durable records, graph, parametric knowledge, consolidation worker.
11. Claim checks and staged experiments.
12. Bibliography and source scope.

## Evidence standards

- Use primary papers for empirical claims and identify reviews/models as syntheses or proposals.
- Separate source claims, primary evidence, author interpretations, and engineering hypotheses.
- Do not turn animal memory paradigms into universal human or LLM algorithms.
- Keep “STM,” “LTM,” and “WM” as source-specific functional labels, not interchangeable software containers.
- Treat Redis, vector databases, and context windows as candidate substrates, not demonstrated equivalents.
- Do not claim that vector similarity implements pattern separation, pattern completion, or transitivity.
- Do not treat schema bypass, reconsolidation, or sleep consolidation as settled implementation rules.
- Preserve unresolved choices: schema representation, TTL/promotion, parametric versus external consolidation, validation, privacy, and evaluation.

## Source audit — selected reading pass

This is a selected-source narrative review, not an exhaustive systematic search. “Checked” below means bibliographic records and abstracts; full texts were not independently inspected for every entry.

| Source / DOI | Reading scope | Consequence for the document |
| --- | --- | --- |
| McClelland, McNaughton & O’Reilly 1995 · 10.1037/0033-295x.102.3.419 | Crossref bibliographic record; framework known from the source. Full text not independently audited. | Cite for the CLS framework and catastrophic-interference rationale, not as a software specification. |
| Kumaran, Hassabis & McClelland 2016 · 10.1016/j.tics.2016.05.004 | Europe PMC abstract; bibliographic record. | Cite for CLS update, replay weighting, rapid schema-consistent learning, and relevance to artificial agents. |
| Kumaran & McClelland 2012 · 10.1037/a0028681 | OpenAlex abstract and bibliographic record. | Cite REMERGE as a computational model of generalization through recurrent episodic interaction, not as proof of a transitive-inference algorithm. |
| Tse et al. 2007 · 10.1126/science.1135935 | Crossref abstract. | Rat paired-associate evidence for rapid schema-consistent assimilation; avoid “almost immediate” as a universal human/LLM claim. |
| Nader, Schafe & LeDoux 2000 · 10.1038/35021052 | Europe PMC abstract. | Retrieval-triggered lability in a specific fear-memory paradigm; not universal memory editing. |
| Teyler & DiScenna 1986 · 10.1037/0735-7044.100.2.147 | Europe PMC/OpenAlex abstract. | Hippocampal indexing theory; index of neocortical activity, not a literal file pointer. |
| Cowan 2008 · 10.1016/S0079-6123(07)00020-9 | Crossref bibliographic record. | Embedded-processes account; capacity estimates vary; “3–7” is not a fixed software limit. |
| Stokes 2015 · 10.1016/j.tics.2015.05.004 | OpenAlex abstract. | Activity-silent working memory as a proposed dynamic-coding framework; mechanism remains debated. |
| Miller & Cohen 2001 · 10.1146/annurev.neuro.24.1.167 | Crossref bibliographic record. | Control as integration of task-relevant information; not a homunculus. |
| O’Reilly & Frank 2006 · 10.1162/089976606775093909 | Crossref abstract. | PBWM computational model of dynamic gating; not direct proof of human gating. |
| Chatham, Frank & Badre 2014 · 10.1016/j.neuron.2014.01.002 | Crossref bibliographic record. | Output gating during selection from working memory. |
| Yassa & Stark 2011 · 10.1016/j.tins.2011.06.006 | Crossref bibliographic record. | Review of hippocampal pattern separation. |
| Neunuebel & Knierim 2014 · 10.1016/j.neuron.2013.11.017 | Crossref bibliographic record. | Direct spatial-task evidence for CA3 pattern completion and dentate-gyrus pattern separation. |
| Squire 2004 · 10.1016/j.nlm.2004.06.005 | Crossref bibliographic record. | Declarative versus nondeclarative/procedural memory systems. |
| Tulving & Thomson 1973 · 10.1037/h0020071 | Crossref bibliographic record. | Encoding specificity: cue–context matching. |
| Johnson, Hashtroudi & Lindsay 1993 · 10.1037/0033-2909.114.1.3 | Crossref bibliographic record. | Source monitoring and provenance. |
| Anderson, Bjork & Bjork 1994 · 10.1037/0278-7393.20.5.1063 | Crossref bibliographic record. | Retrieval can weaken competing memories; caution, not a required procedure. |
| Addis et al. 2009 · 10.1016/j.neuropsychologia.2008.10.026 | Crossref bibliographic record. | Constructive episodic simulation; not consolidation. |
| Hasselmo 1999 · 10.1016/S1364-6613(99)01365-0 | Crossref bibliographic record. | Acetylcholine proposal for encoding/retrieval balance; LLM mapping speculative. |
| Rasch & Born 2013 · 10.1152/physrev.00032.2012 | Review sections noted in the learning notebook. | Active systems consolidation during sleep; not one universal mechanism. |
| Klinzing, Niethard & Born 2019 · 10.1038/s41593-019-0467-3 | Public abstract only. | Integrative account; details vary by task and sleep stage. |
| Tononi & Cirelli 2014 · 10.1016/j.neuron.2013.12.025 | Review summary and caveats in the learning notebook. | Homeostasis/consolidation proposal; not direct observation of universal pruning. |
| de Vivo et al. 2017 · 10.1126/science.aah5982 | Crossref bibliographic record. | Structural synaptic correlate in sampled mouse cortex; not memory-loss measurement. |
| Cary & Turrigiano 2021 · 10.7554/eLife.66304 | Crossref bibliographic record. | Counterpoint to obligatory widespread downscaling; not proof sleep never changes synapses. |
| Tambini, Ketz & Davachi 2010 · 10.1016/j.neuron.2010.01.001 | Summary and discussion in the learning notebook. | Correlational fMRI evidence for rest and retention; not causal replay proof. |

## Main corrections to the source framing

- **STM is not a generic cache.** The source’s Short-Term Labile Episodic Store is a fast, sparse episodic index with a quarantine role. Redis can be a hot-index candidate, but cache eviction is not pattern separation.
- **LTM is not one vector database.** It includes semantic and procedural structure. A vector DB stores declarative records; procedural knowledge needs weights, adapters, or policy modules.
- **WM is not just context.** A context window is an active workspace, but it lacks pointer-based activation, activity-silent maintenance, and input/output gating.
- **Consolidation is not a file move.** It involves replay, interleaving, abstraction, schema integration, and retention decisions.
- **Schema bypass is narrower than the source suggests.** Tse et al. used a rat paired-associate paradigm; it does not establish an LLM schema classifier or universal fast assimilation.
- **Reconsolidation is not unrestricted editing.** Nader et al. studied a specific fear-memory paradigm; updates should be time-bounded, versioned, and auditable.
- **Transitivity does not follow from similarity.** REMERGE is a model of recurrent generalization; inferred links need graph relations and validation.
- **Sleep is not the same as offline consolidation.** Sleep can contribute, but consolidation also occurs in waking rest; synaptic homeostasis is adjacent, not identical.
- **Activity-silent WM is debated.** Stokes’s framework is a proposal/review, not a settled universal mechanism.

## Validation results for the initial draft

- Structural tests: all four research/deck HTML files pass balanced markup, unique IDs, local links/assets, ARIA targets, outline/slide counts, and native MathML checks. Local documentation links and anchors also pass (60 checks).
- Browser layout matrix: research document at 1440×1000, 1024×768, 375×812, and 320×740; deck at 1440×1000, 1280×720, 1024×600, 375×812, and 320×740. No page-wide horizontal overflow. Research tables fit on desktop/laptop and scroll locally on phones; a focused table scrolls with ArrowRight. Deck slides have no content/footer overlap. The twelve-link desktop outline stays on one row at 1440 px.
- Navigation: research contents disclosure, anchor navigation/current-section marker, and local table scrolling verified. Deck previous/next, Home/End, ArrowRight/PageDown, history back/forward, fragment reload, and outline-to-slide focus verified in a fresh session with waits between transitions. Rapid batch key sequences can race the requestAnimationFrame current-slide update, so checks use explicit waits rather than assuming immediate state.
- Native browser diagnostics pass for both new pages: no console messages or page errors, and local reading assets load. The deck QA check used a visible substring plus the slide selector; the heading text is present.
- Print: research export contains 17 pages, all 25 bibliography entries, and the final footer. Deck export contains twelve Letter-landscape pages with matching slide footers, one slide per page. The CSS requests 16:9 slide pages, but the native exporter used Letter paper; the intended 16:9 export depends on honoring CSS page size in printer settings. The research print has a short section-opening page before a wide table; content is retained.
- Existing emotions and routing HTML files remain unchanged except for the shared deck keyboard guard already documented.

## Delivery status and remaining work

The memory research document and twelve-slide deck are initial drafts ready for user review. The procedure checklist is recorded. Practical architecture, latent readout mappings, thresholds, schema, and implementation experiments remain open by design. No commits were made.
