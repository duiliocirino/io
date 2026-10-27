# Valuation, gating, and modulation — plan and source audit

## Scope and outputs

Create a research document and companion presentation covering Layers 5–7 as candidate mechanisms for an endogenous actor. The system is intended to generate goals from its own needs and comprehension, so biological mechanisms—including social hunger—are legitimate candidates to replicate and test. The document distinguishes mechanisms from fixed states and leaves implementation open.

- Research: `docs/research/valuation-gating-modulation-research-document.html`
- Presentation: `docs/research/valuation-gating-modulation-presentation-deck.html`
- Keep the existing routing, memory, and emotion pages intact.
- Reuse the v2 research/deck layouts, offline assets, and print behavior.

## Working outline

1. The actor problem: endogenous valuation, not only external task goals.
2. Core affect: valence as error change, arousal as unresolved uncertainty.
3. Wanting versus liking.
4. Social homeostasis: detector, comparator, effector; quality over presence.
5. Acute versus chronic deficit and adaptive set-points.
6. Epistemic curiosity: learning progress, noisy TV, Goldilocks.
7. Basal-ganglia/PBWM gating: default brake, selective release, veto, emergency hold.
8. Input versus output gating and silent rollouts.
9. Neuromodulators: dopamine, norepinephrine, serotonin, acetylcholine.
10. Integration, arbitration, resource limits, and experiments.
11. Bibliography and source scope.

## Evidence standards

- Treat biological mechanisms as candidates, not fixed states or one-to-one software equivalents.
- Separate source claims, primary evidence, model interpretations, and engineering hypotheses.
- Do not claim that valence/arousal, social hunger, or neuromodulator variables are directly measurable in an LLM without validation.
- Do not turn human isolation, rodent circuitry, or computational models into universal architecture requirements.
- Keep “mechanism versus state” explicit: port the detector/comparator/effector loop, adaptive set-points, learning-progress gate, and gating control—not hardcoded loneliness, depression, curiosity, or satisfaction labels.
- Preserve unresolved choices: error metrics, time windows, set-point values, gate thresholds, modulator mappings, arbitration policy, and evaluation.

## Source audit — selected reading pass

This is a selected-source narrative review, not an exhaustive systematic search. “Checked” means bibliographic records and abstracts; full texts were not independently inspected for every entry.

| Source / DOI | Reading scope | Consequence for the document |
| --- | --- | --- |
| Russell 1980 · 10.1037/h0077714 | Crossref bibliographic record. | Valence–arousal circumplex; descriptive model, not software state. |
| Barrett 2017 · 10.1093/scan/nsw154 | Crossref/OpenAlex record. | Constructed-emotion account; not a universal taxonomy. |
| Joffily & Coricelli 2013 · 10.1371/journal.pcbi.1003094 | Crossref record. | Valence as error/free-energy change proposal. |
| Hesp et al. 2021 · 10.1162/neco_a_01341 | Crossref record. | Computational affect model; not a validated human measurement. |
| Berridge & Robinson 1998 · 10.1016/S0165-0173(98)00019-8 | Crossref record. | Wanting versus liking; not a direct LLM reward signal. |
| Matthews & Tye 2019 · 10.1111/nyas.14016 | Crossref record; review sections noted in the learning notebook. | Detector/comparator/effector framework; flexible set-points; unresolved neural implementation. |
| Tomova et al. 2020 · 10.1038/s41593-020-00742-z | Crossref record. | Human isolation/fMRI evidence; not a software social-hunger parameter. |
| Lee, Chen & Tye 2021 · 10.1016/j.cell.2021.02.028 | Crossref record. | Acute seeking versus chronic adaptation/withdrawal; proposed circuit account. |
| Kidd & Hayden 2015 · 10.1016/j.neuron.2015.09.010 | Crossref record. | Curiosity/information-seeking review. |
| Kidd, Piantadosi & Aslin 2012 · 10.1371/journal.pone.0036399 | Crossref record. | Infant attention evidence; Goldilocks heuristic, not universal law. |
| Oudeyer, Kaplan & Hafner 2007 · 10.1109/TEVC.2006.890271 | Crossref record. | Computational intrinsic-motivation account. |
| Schmidhuber 2010 · 10.1109/TAMD.2010.2056368 | Crossref record. | Formal curiosity/intrinsic-motivation proposal. |
| O’Reilly & Frank 2006 · 10.1162/089976606775093909 | Crossref abstract. | PBWM computational model with dynamic gating. |
| Chatham, Frank & Badre 2014 · 10.1016/j.neuron.2014.01.002 | Crossref record. | Output gating evidence in a specific paradigm. |
| Doya 2002 · 10.1016/S0893-6080(02)00044-8 | Crossref record. | Neuromodulators as meta-parameters; computational framework. |
| Schultz, Dayan & Montague 1997 · 10.1126/science.275.5306.1593 | Crossref record. | Dopamine reward-prediction-error account. |
| Yu & Dayan 2005 · 10.1016/j.neuron.2005.04.026 | Crossref record. | Norepinephrine/uncertainty proposal. |
| Dayan & Yu 2006 · 10.1080/09548980601004024 | Crossref record. | Phasic norepinephrine interrupt/reset account. |
| Hasselmo 1999 · 10.1016/S1364-6613(99)01365-0 | Crossref record. | Acetylcholine and encoding/retrieval balance; LLM mapping speculative. |

## Main corrections to the source framing

- **“Proves” is too strong.** PBWM is a computational model; Chatham et al. support specific gating evidence, not a universal controller.
- **The basal-ganglia pathways are simplified.** The source’s Go/No-Go/hyperdirect account is a useful abstraction, not a literal software circuit.
- **Social homeostasis is a proposed functional loop.** Human isolation findings and rodent circuitry do not supply fixed software set-points or a requirement that an artificial agent feel loneliness.
- **Social hunger is a mechanism, not a state.** The system can estimate mismatch and request calibration; it should not hardcode loneliness or depression.
- **Curiosity is not raw surprise.** Learning progress needs a defined error metric, time window, learnability estimate, and schema competence.
- **Neuromodulator mappings are hypotheses.** Dopamine has the clearest candidate role; norepinephrine, serotonin, and acetylcholine are less direct and require validation.
- **Mechanisms versus states matters.** Port the loop and control policy; avoid fixed affective or clinical labels.

## Validation results for the initial draft

- Structural tests: all research/deck HTML files pass balanced markup, unique IDs, local links/assets, ARIA targets, outline/slide counts, and native MathML checks.
- Browser layout matrix: research document at 1440×1000, 1024×768, 375×812, and 320×740; deck at 1440×1000, 1280×720, 1024×600, 375×812, and 320×740. No page-wide overflow; tables scroll locally on phones; deck slides have no content/footer overlap. The twelve-link desktop outline stays on one row at 1440 px.
- Navigation: research contents disclosure, anchor navigation, local table scrolling, and deck previous/next, Home/End, ArrowRight/PageDown, history, fragment reload, and outline focus verified.
- Native browser diagnostics pass for both new pages: no console messages or page errors; local reading assets load.
- Print: research export contains 13 pages and all 19 bibliography entries; deck export contains twelve Letter-landscape pages, one slide per page. The CSS requests 16:9 slide pages; the native exporter used Letter paper.
- Existing emotion, routing, and memory pages remain unchanged except for the research-index links.

## Delivery status and remaining work

The Layers 5–7 research document and twelve-slide deck are initial drafts ready for user review. The plan, source audit, and learning checkpoint are recorded. Practical architecture, thresholds, set-point values, neuromodulator mappings, and experiments remain open. No commit was made.
