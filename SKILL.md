---
name: imageavatarppt
description: Generate thesis-led, chapter-based executive PowerPoint decks from Chinese or English outlines using the bundled Parallel Digital template, source-aware editorial layouts, restrained palette-controlled full-slide images, explicit page-to-page transitions, static anti-template audits, and optional multimodal visual QA. Use when Codex must turn loose material into a management, executive, proposal, strategy, steering-committee, or major-project deck; identify the central judgment and decision request; reduce formulaic AI copy and generic AI visual devices; generate 16:9 content images with OpenAI GPT Image or MiniMax; review images and deck rhythm with Kimi Vision; recolor the template; and assemble a final PPTX.
---

# Image Avatar PPT

Build a PPTX from an outline through a controlled plan, image generation, visual QA, and deterministic assembly.

## Provider Roles

- Use OpenAI `gpt-image-2` as the default image generator.
- Use MiniMax `image-01` when the user selects MiniMax.
- Set MiniMax `image_generation.region` to `cn` for credentials issued by the
  China platform and `global` for international credentials.
- Use Kimi Vision for image understanding and QA. Do not present Kimi as an image-generation provider unless its official API adds that capability.
- Never call a paid API before confirming the provider, final slide count, and quality setting with the user.

Read `references/provider-contract.md` before configuring or calling a provider.

On macOS, read provider credentials from Keychain when the corresponding environment variable is absent. Never write API keys into plans, prompts, logs, or skill files.

## Required Inputs

Infer these from the request and source outline. Ask only for material choices that are missing:

- Deck title and audience.
- Source outline or loose text.
- Desired number of content slides or target duration.
- Palette: `primary`, `secondary`, `accent`, `background`, `text`, and optional
  `muted`. Default `background` to `#FFFFFF` and keep it solid.
- Image provider: `openai` or `minimax`.
- Whether Kimi visual QA is required.
- Whether the palette should recolor template pages. Default: yes.
- Real metrics, screenshots, photos, logos, or claims that must remain exact.

If the user provides only a color name, derive a balanced six-color palette,
keep `background` at `#FFFFFF`, and record the exact hex values in the plan.

## Calibrated Management-Deck Defaults

Apply these defaults when the audience is a group executive team or another
mostly non-IT decision-making audience. They capture the quality bar established
through recent water-utility executive-deck work and should be treated as
planning and QA requirements, not optional style suggestions.

- **Visual posture:** Use a restrained, industry-appropriate technology
  language: solid white canvas by default, a clear brand hierarchy, controlled
  accents, crisp lines, quiet object-level shading, and high-contrast
  typography. The result should feel mature, professional, and suitable for a
  group-level report. Avoid cyberpunk, marketing-hero, decorative-card,
  scenic-background, or one-note gradient treatments.
- **Main-point visibility:** The page title and the largest text block must
  carry the page's conclusion or decision point. Do not demote the reason for
  change, the industry-specific judgment, or the intended management outcome to
  tiny annotations. An annotation may explain a point; it may not replace the
  point.
- **Text-to-visual balance:** For substantive content pages, visible text should
  normally occupy about 30%-45% of the usable content area, with 30% as the
  minimum target for an argument page. Use the remaining area for one dominant
  diagram, comparison, process, matrix, or evidence structure. Treat this as a
  readability guardrail rather than a pixel-perfect quota; a cover, chapter
  divider, or architecture page may differ. Compared with a sparse AI-generated
  draft, enrich the visible content by roughly 10%-20%, but do not fill the page
  with paragraphs or tiny labels.
- **Readable evidence:** A substantive page should usually contain one
  conclusion-led title, 2-4 short supporting statements or evidence points, and
  one visual system that explains their relationship. Do not put the whole
  source outline in speaker notes. Put only the spoken expansion, caveats, and
  examples in notes. If the argument still depends heavily on narration after
  this balance, split the page.
- **Editorial authorship:** Preserve the solid, quiet canvas, but do not make
  every page a polished infographic. Prefer source screenshots, original
  charts, plain tables, annotated evidence, and native diagrams before generic
  illustration. Use icons, circular badges, rounded cards, central hubs,
  decorative arrows, isometric scenes, and fake dashboards only when the
  content requires them. Do not use those elements to fill whitespace.
- **Copy rhythm:** Vary title forms across facts, observations, decisions,
  questions, and concise topic labels. Treat contrast formulas such as
  “不是……而是……”, “从……到……”, and “先……再……” as occasional devices, not the
  default voice. Preserve a formulaic title only when its contrast is genuinely
  the argument or the user supplied it.
- **Non-IT translation:** Lead with business effect, operating change,
  management value, and replication conditions. Move implementation details
  behind the business judgment. When a technical term is necessary, add a
  short plain-language gloss at first use. Do not let framework names, model
  names, data pipelines, or platform layers become the page's headline unless
  the audience explicitly asks for them.
- **Domain specificity:** Do not use generic “AI can improve efficiency” copy.
  Show what is specific to the subject, audience, and operating context. When
  the source raises a comparison with another sector, make the comparison a
  visible, evidence-backed argument rather than leaving it as an implied
  background assumption.
- **Pagination:** Estimate pages from information density and narrative
  completeness instead of forcing every deck into an arbitrary count. If the
  template catalogue cannot express the required chapter or content structure,
  use a blank/custom deck or an editable directory rather than deleting needed
  content.
- **Architecture and matrix pages:** Make the information hierarchy explicit.
  Use topology, connectors, labels, and short descriptions to explain real
  relationships. Do not let a diagram become a decorative collection of cards;
  every meaningful node should have a clear business role when the page needs
  that explanation.
- **Scenario consistency:** When the user replaces a scenario, update every
  related matrix, architecture, workflow, result, and replication page. Do not
  leave stale labels from an earlier draft. Keep terminology synchronized across
  all pages that describe the same scenario or workflow.
- **Image quality and migration:** Generate content images at `2048x1152` or
  higher when possible, keep 16:9, and inspect both the PNG and a rendered PPTX.
  Reject blur, low-resolution Chinese, malformed characters, clipping,
  overlap, unreadable small text, or a visual that feels like a background with
  text pasted on top. When template integration reduces clarity, provide a
  clean blank-deck version with the same page order and chapter structure so
  the user can migrate pages without accepting degraded assets.

## Output Contract

Deliver:

- `deck-plan.json` containing the resolved outline, palette, provider settings, and per-slide prompts.
- A storyline walkthrough showing the central thesis, decision request, story arc,
  and page-to-page logic before paid generation.
- One generated PNG per content slide.
- `contact-sheet.png` showing all content slides in order for deck-level review.
- A static style-audit JSON covering title formulas, copy density, repeated
  layout families, declared source material, and common AI-default devices.
- `image-qa.json` when Kimi QA is enabled.
- Final `.pptx`.
- Slide inventory JSON generated by the assembler.

## Workflow

1. Lock the executive narrative.
   - Read `references/executive-storyline.md` for management, executive,
     proposal, strategy, steering-committee, or major-project decks.
   - Identify audience, decision goal, evidence, constraints, and missing facts.
   - Write one `core_thesis`: the central judgment the audience should remember.
     Treat it as a deck-level planning compass, not automatic visible copy for
     every page.
   - Write one `decision_request`: the decision, approval, alignment, or next
     action expected from the audience.
   - Define 1-3 `audience_priority` items and a 3-6 move `story_arc` that leads
     causally to the decision request.
   - If two plausible theses would materially change the deck, ask one focused
     question before fixing the slide count or generating images.
   - Do not preserve the source outline order when it weakens the argument.
     Merge repetition, move technical detail behind the business judgment, and
     keep appendices outside the main decision path.

2. Build the storyboard.
   - Split the material into at most four chapters when the template catalogue is included.
   - Give each content slide one `audience_question`, one conclusion-led
     `message`, one explicit transition into the next page, and one dominant
     `visual_focus` describing the visual system. Except for cover, chapter, and closing pages, avoid
     topic-only titles.
   - Define the slide's `narrative_role`, `thesis_expression`,
     `content_boundary`, and `thesis_connection`. Separate the deck-level
     north star from the page-level claim: a diagnosis page must diagnose, an
     evidence page must prove, and a solution page may reveal the answer.
   - Default `thesis_expression` to `implicit`. The deck thesis may guide visual
     grammar, emphasis, sequencing, and a subtle visual anchor, but it must not
     appear as page copy or as a literal solution object unless the source and
     the page's narrative role explicitly reveal it.
   - Treat visuals as claims. An AI platform, target architecture, product,
     outcome, or future-state scene shown on a problem page is premature
     solution leakage even if it is not labeled in text.
   - Infer the information topology before choosing a layout. Distinguish
     shared-center relationships, causal chains, sequences, hierarchies,
     comparisons, matrices, networks, spatial systems, and evidence boards.
   - Do not copy the source format mechanically. A source table may become a
     hub-and-spoke diagram when its rows are dimensions of one central issue; a
     bullet list may become a flow, layer model, or causal chain when the items
     are related.
   - Classify each claim as `fact`, `inference`, `proposal`, or `decision`; do
     not present an inference or proposal as established fact.
   - Use the `because / but / therefore` test. Each page needs evidence, a
     remaining tension, or a reason the next page must follow.
   - Alternate title forms intentionally. Read all titles as a sequence and
     rewrite repeated “不是……而是……”, “从……到……”, “先……再……” structures unless
     the contrast is source-backed and necessary.
   - Choose the visual source before choosing decorative elements. Record real
     screenshots, photos, charts, tables, or documents that can carry the page;
     do not replace source evidence with a synthetic dashboard or illustration.
   - Add concise `speaker_notes` when the spoken explanation matters; do not
     force the full narrative into generated image text.
   - Never invent metrics, customer names, dates, or evidence.
   - Keep the tone restrained and evidence-based. Avoid inflated slogans,
     winner/loser framing, or self-congratulatory claims such as "不是追赶者，
     而是定义者" unless the user explicitly provides that wording and asks to
     retain it. Prefer concrete phrasing such as "具备先发探索价值",
     "可形成集团级复制路径", or "有机会沉淀为方法论".

3. Create `deck-plan.json`.
   - Follow `references/deck-plan-schema.md`.
   - For new plans, declare `authorship`, plus each slide's `visual_source`,
     `source_asset_refs`, `layout_family`, and `graphic_devices`. These fields
     improve static and visual QA; older plans remain valid without them.
   - For new plans, default content slides to `title_render_mode=native`.
     Generated images must reserve a clean title zone without rendering a
     title, title placeholder, or pseudo-text. The assembler adds the real
     title as editable PowerPoint text. Use `image` only when the user explicitly
     needs the title integrated into the bitmap; use `none` for an intentional
     untitled page. Older plans without `authorship` keep image-rendered titles
     for compatibility.
   - For `source_evidence` or `mixed` pages, inspect the actual source assets and
     use an asset-aware ImageGen edit/reference call or a native/local composer.
     Do not pass only the asset filename to a text-only generation call and let
     the model reconstruct a synthetic screenshot, chart, photo, or document.
   - Choose a page role for every content slide: `opener`, `overview`, `metrics`, `process`, `system`, `comparison`, `roadmap`, or `custom`.
   - For image-based PPT requests where the user asks ImageGen / GPT Image /
     Codex image generation to output the PPT pages themselves, prefer
     `direct_imagegen_slide` as the default route. Do not downgrade to
     text-free backgrounds plus local text overlay merely because the deck has
     substantial content. Instead, restructure the story, split pages when
     needed, and keep each slide's visible text to a designed set of readable
     thesis lines, KPI figures, labels, and evidence points. Put surplus detail
     into `speaker_notes`.
   - When the user explicitly wants GPT Image / Codex image generation to make
     the PPT page itself, or complains that text and background are not designed
     as one whole, set `image_generation.composition_mode` to
     `direct_imagegen_slide`. In this mode, use Codex's built-in `image_gen`
     tool to generate each full 16:9 slide as one integrated bitmap: visual
     metaphor, scene, diagrams, KPI figures, labels, and Chinese hierarchy are
     conceived together in the prompt. Do not generate a text-free background
     and do not run local overlay compositors for these content pages.
   - In `direct_imagegen_slide`, plan each page as a complete visual argument:
     a main thesis, a visual structure that embodies that thesis, and a small
     number of supporting proof points. Use a pure solid-color canvas, white by
     default. Build meaning with layout, typography, relationships, diagrams,
     and evidence instead of scenic backgrounds or decorative texture.
   - Keep one dominant visual system or focus region per page. It may contain a
     center node, connected satellites, arrows, layers, or a controlled set of
     shapes when those elements encode real relationships. Background, scenery,
     and ornament must remain subordinate to the conclusion.
   - Make `exact_text` the exclusive image-rendered-copy contract. Do not
     duplicate a `native` title in `exact_text`, and do not promote
     `storyline.core_thesis`, `decision_request`, `transition`, speaker notes,
     or prompt instructions into visible text unless those words are also
     intentionally included in `exact_text`.
   - Allow graphical richness that explains the idea: connectors, nodes,
     containers, icons, paths, and restrained color blocks. Reject graphics
     that exist only to decorate the page.
   - Keep adjacent pages visually related when they explain the same system,
     but change composition when the reasoning changes.
   - Use `image_generation.local_text_overlay = true` only when the user has
     not asked ImageGen to design the PPT pages themselves and the deck must
     preserve a large amount of exact editable text. In that route, set
     `source_directory` to a separate folder. The provider then creates
     text-free visual backgrounds while the local compositor preserves all
     required copy exactly.
   - When the user asks ImageGen to participate in the PPT design itself rather
     than provide illustrations, set `image_generation.composition_mode` to
     `designed_canvas`. Prompt the image model to create pure-white,
     text-free information-graphic canvases with title zones, blank content
     regions, diagrams, flows, and visual hierarchy; the local compositor then
     overlays exact Chinese text.
   - When the user wants a high-design deck rather than content-dense pages,
     and has not asked for direct Codex image generation, set
     `image_generation.composition_mode` to `ui_designer`. Use GPT Image to
     generate restrained text-free information structures on a white solid
     canvas: comparisons, flows, KPI bands, architecture layers, and process
     paths. Then use
     `scripts/compose_ui_designer_slides.py` at `1920x1080` or higher to
     overlay only concise Chinese labels, decisions, and key metrics. In this
     mode, keep the information structure visually dominant: do not add
     full-width opaque headers, large text panels, dense card stacks, or
     immersive background art. Do not preserve every outline sentence as
     visible bullet text in this mode.
   - Without local text overlay, reduce image-rendered copy to concise labels
     and proof points. Keep the title native by default. Put long explanations
     in speaker notes or a separate editable-text workflow.
   - Write `exact_text` as an array so QA can compare expected strings.
   - Use one output image path per slide.

4. Review the full storyline before spending.
   - Present the resolved `core_thesis`, `decision_request`, chapter arc, and a
     compact slide sequence showing each page's message and
     `transition.to_next`.
   - Review the deck as a senior solution expert: check thesis alignment,
     executive relevance, evidence gaps, redundancy, abstraction jumps,
     chapter closure, final convergence on the decision request, and whether
     the spoken bridges read naturally in sequence.
   - Run `scripts/audit_deck_style.py` and resolve high-risk findings: repeated
     title formulas, one dominant layout family, long runs of the same topology,
     dense generated copy, weak evidence provenance, or excessive standard AI
     devices. Use `--strict` when the plan's authorship policy is a release gate.
   - Check reveal timing. Reject a page that states or depicts a later answer
     before the story has earned it, or that substitutes the deck thesis for
     the source-backed page content.
   - Delete or merge any slide whose removal does not weaken the argument.
   - Record the result in `storyline_review`. Keep `status` blocked until thesis
     alignment, executive relevance, page flow, and visual consistency pass and
     `open_issues` is empty.
   - Do not proceed to paid generation until the storyboard passes this review.

5. Lock the palette and prompts.
   - Read `references/image-style-guide.md`.
   - Inject the exact hex palette into every prompt.
   - State the background, title color, card color, line color, and accent usage explicitly.
   - Default `background` to `#FFFFFF`. Use a pure solid-color background with
     no background photo, texture, pattern, glow, or decorative scene. Allow
     restrained flat fills, subtle object-level shading, and connector lines
     inside the information graphic when they clarify relationships. Use a
     different solid brand color only when the user explicitly requests it.
     Set `allow_nonwhite_background` to `true` only for that explicit exception.
   - Keep a consistent visual language across the deck while adapting the subject to each slide.
   - Keep company typography and margins stable, but vary the material form.
     Permit a plain statement, source screenshot, native chart, annotated table,
     reasoning diagram, or generated scene. Do not force all pages into an
     icon-card or hub-and-spoke system.

6. Validate before spending.

```bash
python3 scripts/validate_plan.py deck-plan.json
python3 scripts/audit_deck_style.py deck-plan.json --output style-audit.json
python3 scripts/generate_images.py deck-plan.json --dry-run
```

7. Confirm paid generation.
   - Report provider, model, number of images, size, and quality.
   - If Kimi deck-style QA is enabled, report one additional paid contact-sheet
     review call.
   - Wait for user confirmation.

8. Generate images.

For `composition_mode=direct_imagegen_slide`, use the built-in `image_gen`
skill/tool instead of `scripts/generate_images.py`. Generate one slide at a time
with a complete prompt containing:

- use case: `productivity-visual` or `infographic-diagram`;
- asset type: complete 16:9 executive PowerPoint slide image;
- primary request: design the entire slide as one integrated executive report
  page that is understandable without speaker narration;
- slide narrative role, audience question, and page conclusion;
- `thesis_expression`, `content_boundary`, and `thesis_connection`;
- when `thesis_expression` is `implicit`, omit the deck thesis and decision
  request from the image prompt and explicitly forbid their text or literal
  depiction; use only the slide-specific content and permitted visual subtext;
- when `thesis_expression` is `explicit`, include the deck thesis only when it
  belongs to this page's source-backed argument and `exact_text` contract;
- exact palette;
- exact visible Chinese text, kept concise;
- one dominant visual system on a pure white solid canvas;
- information topology and the reason that topology matches the message;
- integrated composition direction that binds text, scene, diagrams, KPI
  figures, and visual hierarchy into one page;
- declared visual source, source-asset references, layout family, and only the
  graphical devices that the page actually needs;
- the actual referenced source images when the page uses `source_evidence` or
  `mixed`; if the generation route cannot attach them, preserve the evidence
  region for native/local composition instead of fabricating a substitute;
- page-specific composition: do not reuse one left-title/right-card layout
  across the deck. Let each slide's message choose the form, such as two-column
  comparison, deployment-gap bridge, structural bottleneck map, knowledge
  foundation platform, agent matrix, command center dashboard, closed-loop
  workflow, KPI evidence board, service model comparison, or rollout roadmap;
- avoid list: no watermark, no logo, no pseudo text, no extra claims, no
  marketing exaggeration, no gradient background, no background photo, no
  texture, no pattern, no excessive glow, no scenic wallpaper, no disconnected
  card collection when the content has relationships, no separate background +
  overlay feel, no generic line-icon filler, no automatic circular badges, no
  repeated rounded-card grid, no glowing AI brain or chip, no fake dashboard,
  no automatic symmetric hub-and-spoke.

After each `image_gen` call, inspect the slide image directly. Reject malformed
Chinese, invented slogans, awkward spacing, visual clutter, or a composition
that feels like a background with text pasted over it. Also reject pages where
the visible copy is too sparse to carry the source argument, or where the
background dominates and the core message cannot be read at contact-sheet
thumbnail size. Also reject any page whose background is not a clean approved
solid color or whose visual language jumps abruptly from adjacent pages. Reject
premature solution leakage: visible thesis copy, solution objects, future-state
architecture, or outcomes that exceed the slide's `content_boundary`. Save
accepted PNGs into the workspace output directory, then assemble them
full-bleed into PPTX using the Presentation skill's
`@oai/artifact-tool` workflow or the local assembler.

For provider-script generation, run:

```bash
python3 scripts/generate_images.py deck-plan.json --confirm-paid-call
```

Use `--overwrite` only when intentionally regenerating existing slide images. Use `--limit 1` for a first-slide style calibration when the user requests it.

9. Compose exact local text when enabled.

```bash
python3 scripts/compose_slide_images.py deck-plan.json
```

10. Inspect and review.
   - Reject malformed Chinese, missing exact terms, duplicated labels, collisions, cropped content, unreadable small text, wrong palette, or wrong business meaning.
   - Generate the ordered contact sheet:

```bash
python3 scripts/create_contact_sheet.py deck-plan.json
```

   - Review a contact sheet in order. Confirm each page has one dominant visual
     system, its topology matches the content relationships, the background is
     pure and quiet, and the deck has consistent visual grammar and pacing.
   - Review whether the deck contains editorial rhythm and material specificity:
     source evidence, plain typographic pauses, native data views, diagrams, and
     generated visuals should appear because the argument needs them, not as a
     fixed quota or repeated template.
   - Run the zero-cost static audit again after titles and prompts are final:

```bash
python3 scripts/audit_deck_style.py deck-plan.json --output style-audit.json
```

   - Run local dimension checks for every image.
   - If Kimi QA is enabled, run:

```bash
python3 scripts/qa_images.py deck-plan.json --reviewer kimi --confirm-paid-call
```

This call is also paid and requires confirmation. Use `--limit 1` for a
canary review and `--resume` for the remaining slides without reviewing a
passing slide twice. Add `--deck-style` to review the ordered contact sheet for
repeated AI-default visual grammar and copy rhythm; that option makes one
additional paid Kimi call. Regenerate only failed slides.

11. Assemble.

```bash
python3 scripts/assemble_deck.py deck-plan.json
```

The assembler preserves editable template structure, duplicates chapter
dividers, inserts full-bleed content PNGs, adds editable native content titles
by default for new plans, optionally recolors known template colors, and writes
a slide inventory.

12. Verify.
   - Confirm slide count and order against `deck-plan.json`.
   - Confirm every content slide contains exactly one full-bleed image.
   - Render thumbnails when a renderer is available and inspect all slides.
   - Read the titles and `transition.to_next` fields aloud in order; confirm the
     explanation moves smoothly toward `decision_request`.
   - Confirm the output PPTX embeds the latest generated images.

## Template Rules

- Use `assets/parallel-digital-standard-template.pptx`.
- Use template slide 1 as cover, slide 2 as catalogue, slide 3 as the reusable chapter divider, and slide 5 as closing.
- Keep chapter-page text editable.
- Use content visuals as replaceable full-slide images; keep content titles as
  editable native text by default.
- Set `apply_palette_to_template` to `false` only when original corporate branding must remain unchanged.
- Do not alter the original template asset.

Read `references/template-inventory.md` when changing template handling.

## Failure Rules

- Stop if a required API key is missing; name the required environment variable.
- Stop if a slide image is missing, non-PNG, not close to 16:9, or below the configured minimum dimensions.
- Stop if the catalogue is enabled with more than four chapters.
- Do not silently switch providers.
- Do not assemble images that failed QA.
- Do not claim Kimi generated an image when it only reviewed one.
