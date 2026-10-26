# Cognitive routing — document plan and source audit

## Scope and intended outputs

Create a standalone learning/research document and companion newcomer-friendly presentation, using the existing IO v2 design. Practical architecture remains open: selected biological mechanisms can motivate future implementations without pretending a software counterpart is already validated.

- Research: `docs/research/cognitive-routing-research-document.html`
- Presentation: `docs/research/cognitive-routing-presentation-deck.html`
- Keep the source conversation and existing emotions pages intact.
- Reuse current research/deck navigation, accessibility, offline assets, and print behavior. Add a shared component only if the content genuinely needs it.

## Working outline

1. Scope, the coordination problem, and how to read the document.
2. What networks, functional connectivity, anticorrelation, and directed analyses mean.
3. The triple-network framework and the original switching hypothesis.
4. Competition and cooperation, with an accurate historical sequence.
5. Subnetworks and individual mapping; keep different naming schemes separate.
6. Temporal/directional evidence from fMRI and intracranial recordings.
7. DMN contributions to contextual meaning, memory, and social cognition.
8. Evidence limits, clinical interpretation, fatigue, and checks on source-chat claims.
9. Architectural implications, a clearly illustrative scenario, and unresolved design/evaluation questions.
10. Bibliography and source scope.

The presentation follows an explanatory twelve-slide narrative rather than compressing every paragraph. Layout and text density are checked at compact-screen sizes.

## Workflow / status

- [x] Inspect existing research pages, design guide, and repository state.
- [x] Audit selected foundational and follow-up sources; record access limits and reading scope below.
- [x] Refine the outline against the evidence and draft the research document.
- [x] Produce the twelve-slide companion deck from the argument.
- [x] Review content and components; shorten deck navigation labels to keep the expanded desktop outline on one row.
- [x] Check semantic markup, IDs, links/references, and offline asset paths with dependency-free tests.
- [x] Browser-check desktop, compact laptop, and phone; keyboard/fragment navigation and print.
- [x] Check existing emotions layouts and presentation navigation/equation scrolling after the shared keyboard-guard fix.
- [x] Update README, research map, reading guide, and learning checkpoint; initial drafts await user review.

## Evidence standards

- Use primary papers for empirical claims and identify reviews as syntheses, not new experiments.
- Separate results, author interpretations, and our engineering hypotheses.
- Do not turn statistical directionality into perturbational proof or a universal switch.
- Check chronology: cooperation evidence may predate the 2011 framework.
- Do not combine FPCN-A/B, default-network subsystems, and precision-mapped DN-A/B into one canonical atlas.
- Do not portray clinical conditions as consequences of one proven failure rule.
- Treat overload/fatigue and LLM latent routing as open project hypotheses, not established equivalences.
- Preserve practical questions rather than inventing interfaces, thresholds, or an implementation contract.

## Source audit — selected reading pass complete

This is a narrative review, not an exhaustive systematic search. “Read” below means the stated sections, not an assertion that every supplementary analysis or cited experiment was audited. Browser retrieval and local extraction of relevant sections were used; failed section matches were not counted as readings.

| Source / DOI | Reading scope | Consequence for the document |
| --- | --- | --- |
| Menon 2011 · 10.1016/j.tics.2011.08.003 | Indexed abstract and bibliographic record through Europe PMC. Complete review not inspected; full-text access limitation stated in the document. | Cite for proposed framework and clinical scope, not as a new experiment proving a universal switch. |
| Sridharan, Levitin & Menon 2008 · 10.1073/pnas.0800005105 | Open PMC abstract/introduction, experimental design, Granger/network methods, discussion. | Timing and modeled directed influence in auditory, visual, and resting data; authors qualify their usage of “causal.” |
| Spreng et al. 2010 · 10.1016/j.neuroimage.2010.06.016 | Open manuscript abstract, participants/tasks, preprocessing, coupling results, discussion. | Cooperation during autobiographical planning predates the 2011 review; distinguish control from dorsal attention and avoid universalizing this task comparison. |
| Dixon et al. 2018 · 10.1073/pnas.1715766115 | Abstract/introduction, differential coupling results, discussion and limitations. | FPCN-A/B are relative, flexible biases. Some B nodes couple positively with both systems in some contexts; boundaries depend on parcellation and individuals. |
| Andrews-Hanna et al. 2010 · 10.1016/j.neuron.2010.02.005 | Open article's functional-contributions discussion. | Separate the core/MTL/dMPFC account from later within-individual A/B maps; do not construct a canonical combined atlas. |
| DiNicola, Braga & Buckner 2020 · 10.1152/jn.00529.2019 | Abstract and discussion, including limitations and conclusions. | Three samples of six participants scanned four times; episodic/ToM contrasts establish preferences, not exclusive functions. Publication year is 2020 despite the DOI suffix. |
| Das & Menon 2020 · 10.1093/cercor/bhaa111 | Abstract, both cohort descriptions, PTE methods, anticorrelation and directed-hub discussion, conclusion. | Explicit resting wakefulness versus task-free intertrial intervals; not encoding/recall. Distinguish electrical measures from BOLD anticorrelation. |
| Das & Menon 2024 · 10.7554/eLife.99018 | eLife abstract, PTE discussion, limitations/future work. | Four memory experiments, 177 participants overall. Authors request causal manipulation and caution that PTE cannot reliably track rapid shifts. Do not claim a universal continuous millisecond scheduler. |
| Menon 2023 · 10.1016/j.neuron.2023.04.023 | Abstract, direct cognitive functions, suppression/switching with rodent optogenetic summary, internal-narrative proposal, challenges/future directions. | Distinguish evidence across tasks from a proposed integrative narrative account. Acknowledge other causal evidence without conflating species or experiments. |
| Murphy et al. 2009 · 10.1016/j.neuroimage.2008.09.036 | Open abstract. | Preprocessing can introduce/alter negative correlations. Do not infer that every anticorrelation is therefore artificial. |
| Chai et al. 2012 (online 2011) · 10.1016/j.neuroimage.2011.08.048 | Abstract in the open manuscript; indexed abstract/bibliographic record cross-checked through Europe PMC. | Anticorrelations also observed without global signal regression using CompCor; preserve the methodological balance. |

### Main corrections to the conversation's framing

- Competition and cooperation are not a strict historical before/after-2011 replacement story.
- CEN/FPN/FPCN, DAN, and salience labels require study-specific definitions.
- FPCN-A/B, a default-network core/subsystem account, and precision-mapped default A/B are not interchangeable pieces of one atlas.
- Directed statistical influence is distinct from intervention; higher-resolution recordings do not by themselves demonstrate rapid continuous arbitration.
- The 2020 and 2024 iEEG studies address different conditions. Clinical electrode coverage and task sampling limit generalization.
- Narrative integration is a synthesis/proposal; clinical conditions and fatigue are not one proven switching failure.
- Architectural questions remain open. Biological mechanisms may intentionally be replicated, with appropriate controls rather than scripts dictating outcomes.

## Validation results for the initial draft

- `python3 -m unittest discover -s tests -v`: four test methods pass across all four research/deck HTML files. Checks include balanced authored markup, unique IDs, local links/assets, ARIA label targets, outline/slide counts, and valid native MathML.
- `node --check docs/assets/io-presentation.js` and `git diff --check`: pass.
- Browser layout matrix: 13 page/viewport cases, including existing emotions pages. New research checked at 1440×1000, 1024×768, 375×812, and 320×740; new deck at 1440×1000, 1280×720, 1024×600, 375×812, and 320×740. No page-wide horizontal overflow, slide/footer overlap, or unfocusable overflowing reference regions detected.
- Visual inspection: desktop/phone research and comparison diagram; deck cover, laptop/phone comparison slide, and phone claim table. Shortened outline labels keep all twelve links on one row at the expanded desktop size.
- Research controls: contents disclosure, anchor navigation/current-section marker, and keyboard horizontal table scrolling verified.
- Presentation controls: previous/next, Home/End, ArrowRight/PageDown, history back/forward, fragment reload, and outline-to-slide focus verified at laptop/phone sizes. Existing emotions controls and local equation scrolling also pass.
- A real keyboard bug was reproduced and fixed: `.table-scroll` now joins `.equation-scroll` in the shared deck shortcut guard, so arrows scroll a focused wide table instead of advancing slides.
- Native browser diagnostic presets pass for both new pages: no console or page errors, and no failed reading-asset requests in the inspected session.
- Print: research export contains 16 pages, all eleven DOI references, and the final footer; reading rail is hidden. Deck export contains twelve landscape pages with matching slide footers. Research page 1 and deck page 6 were raster-inspected. The native exporter used Letter paper; the CSS requests widescreen slide pages, so the intended 16:9 export still depends on honoring CSS page size in printer settings.

Detailed browser result data, screenshots, and QA-only PDF exports were saved under `/tmp/io-routing-qa/`, outside the repository. They are not publication assets or an assertion of exhaustive accessibility/device testing. The existing emotions HTML files were not edited.

## Delivery status and remaining work

The research document and twelve-slide deck are initial drafts ready for user review. The scope is a selected-source narrative synthesis, with the 2011 full-text access limitation visible in both the audit and research bibliography. Practical architecture, latent-readout mappings, and implementation experiments remain unresolved by design. No commits were made.
