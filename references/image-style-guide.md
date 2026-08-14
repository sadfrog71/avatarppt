# Image Style Guide

This guide defines the full-slide PNG style used for content pages.

## Contents

- [Visual Direction](#visual-direction)
- [Editorial Authorship And Source Priority](#editorial-authorship-and-source-priority)
- [Executive Visual Hierarchy](#executive-visual-hierarchy)
- [Narrative Role And Content Boundary](#narrative-role-and-content-boundary)
- [Information Topology First](#information-topology-first)
- [Palette](#palette)
- [Typography](#typography)
- [Graphic Elements](#graphic-elements)
- [Drawing Rules](#drawing-rules)
- [Editorial Layout Families](#editorial-layout-families)
- [AI Image Prompt Pattern](#ai-image-prompt-pattern)
- [Negative Prompt](#negative-prompt)
- [Final Image Checklist](#final-image-checklist)

## Visual Direction

Create a palette-controlled enterprise presentation style that adapts to the user's topic.

The feel should be clean, technical, executive, and suitable for Chinese enterprise or government-facing reporting. It should look topic-specific and intentional, not like a generic SaaS landing page. The visual subject must come from the user's actual scenario. The user palette is authoritative.

Keep the communication restrained. Do not add heroic slogans, market-leader
claims, winner/loser framing, or exaggerated language that the source did not
state. Avoid lines such as "不是追赶者，而是定义者", "重新定义行业", "行业唯一",
or "绝对领先" unless the user explicitly asks for that exact language. Prefer
measurable, neutral wording.

## Editorial Authorship And Source Priority

Create authorship through selection and evidence, not through simulated
imperfection. Keep a quiet canvas while allowing the material form to change.
Choose the page's visual source in this order when the source exists:

1. User-provided screenshot, document excerpt, operational photo, or original
   system view.
2. Native chart or table built from verified data.
3. Native diagram built from source-backed relationships.
4. Generated supporting visual or full-slide image when the argument is
   conceptual and the source has no stronger evidence object.

Do not redraw a real screenshot as a fake dashboard or replace an original
table with decorative KPI cards merely to make the page look designed. Crop,
annotate, enlarge, and highlight source material instead. A human-authored deck
may deliberately include a plain statement page, an annotated screenshot, a
dense but readable table, and a diagram; it does not need an illustration on
every page.

For new plans, record `visual_source`, `source_asset_refs`, `layout_family`, and
`graphic_devices`. Treat `graphic_devices` as a budget: list only the visual
devices needed to explain the claim. Do not let a model invent extra icons,
cards, badges, arrows, dashboards, or technology scenery.

Default new content pages to `title_render_mode=native`. The image must reserve
a clean title zone without drawing the title, a placeholder, or pseudo-text;
the assembler adds the title as editable PowerPoint text. Use an image-rendered
title only when the page explicitly declares `title_render_mode=image`.

For `source_evidence` and `mixed` pages, attach the actual source image to an
asset-aware generation/edit call or compose it locally with native text and
annotation. A filename inside a text prompt is not evidence. If the route cannot
accept the asset, reserve its region and stop before final assembly rather than
letting the model invent a substitute.

## Executive Visual Hierarchy

Design for a decision-maker scanning the page from a distance:

- Use a pure solid-color canvas, white by default. Do not add background
  gradients, photos, textures, patterns, glow, decorative scenery, or
  atmospheric background art.
  Use another solid brand color only when the user explicitly requests it.
- Give every page one primary reading path. This may be a statement, source
  artifact, single number, table, chart, or connected visual system. Do not
  force a diagram onto a page whose best evidence is text or a real screenshot.
- Use enough graphical structure to make the idea legible. A center with five
  connected dimensions is still one visual system; five unrelated decorative
  cards are not.
- Keep accent color controlled, typically around 10-20% of the page, and use it
  to encode active relationships, priorities, key numbers, or risks.
- Prefer generous whitespace, stable alignment, and clear scale contrast over
  decoration. A management slide may feel visually calm while still looking
  deliberate and high quality.
- Allow restrained connectors, nodes, containers, paths, and flat color blocks
  only when they encode business meaning. Circular badges, concentric rings,
  central hubs, rounded-card grids, generic line-icon systems, fake dashboards,
  decorative arrows, isometric worlds, glassmorphism, glow, and floating
  objects are not defaults.

Across a deck, keep title position, margins, palette, icon language, line style,
and typography stable. Vary composition according to the reasoning: diagnose,
compare, explain, prove, sequence, or decide. Adjacent pages that discuss the
same system should retain a visual anchor; a new visual language should signal a
real narrative shift.

## Narrative Role And Content Boundary

Design from the page-level argument, not directly from the deck-level thesis.
The thesis is a north star for selection, rhythm, visual continuity, and reveal
timing; it is not a default headline, center label, hero object, or diagram.

- Use `narrative_role` to decide what the page is allowed to accomplish.
- Use `content_boundary` as a semantic fence for both text and imagery. Visual
  objects are claims: depicting a platform, target architecture, future-state
  workflow, or outcome adds content even when no label is attached.
- When `thesis_expression` is `implicit`, render only the page message and
  source-backed evidence. Let the deck thesis influence subtle visual grammar,
  such as a recurring line language, a controlled gap, an unresolved center,
  or a transition cue. Do not write or literally illustrate the thesis.
- When `thesis_expression` is `explicit`, reveal the thesis only if the page is
  the intended strategic-judgment, solution, or decision moment and the words
  belong in `exact_text`.
- Keep `exact_text` exclusive to image-rendered copy. Do not duplicate a native
  title in it, and do not render prompt labels, deck-planning fields, speaker
  notes, transition copy, or the decision request unless they appear in
  `exact_text`.

Example: if a diagnosis page lists five structural bottlenecks and the later
deck answer is an enterprise agent platform, show the five bottlenecks as one
connected operating constraint. Do not put an agent platform in the center.
The solution may be foreshadowed only through a reusable visual anchor that
does not identify or promise the solution.

## Information Topology First

Choose the visual structure from the relationship among ideas, not from the
format of the source material:

- `hub_spoke`: several dimensions, symptoms, capabilities, or constraints share
  one central subject. Use a clear center node and connected satellites.
- `causal_chain`: one condition produces another. Use directional arrows and
  make the cause-to-effect path explicit.
- `flow`: steps, actors, or handoffs occur in order. Use a process spine or
  swimlane.
- `layers`: capabilities or dependencies build on one another. Use stacked
  layers, nested containers, or foundation-to-application architecture.
- `comparison`: two or more alternatives must be judged against common
  dimensions. Use columns or a comparison matrix.
- `evidence_board`: independent facts jointly support one conclusion. Use a
  central conclusion with a controlled evidence field.
- `network`: many-to-many relationships matter. Use nodes and edges sparingly,
  emphasizing only the connections relevant to the conclusion.
- `spatial_system`: physical location or system placement matters. Use a map,
  facility schematic, or simplified spatial view.

Use a table only when row-and-column lookup or direct comparison is itself the
insight. Do not use a table merely because the source was supplied as a table.
Do not force every page into hub-and-spoke either; select the topology that makes
the message easiest to understand.

## Palette

Use the exact colors from `deck-plan.json` consistently:

- `primary`: main structures, data series, strong borders, and major icons.
- `secondary`: title bands, deep surfaces, and supporting structures.
- `accent`: highlights, active nodes, callouts, and typically 10-20% of the page.
- `background`: the dominant slide canvas and card surfaces.
- `text`: titles and body text.
- `muted`: secondary copy, dividers, inactive data, and subtle borders.

Create lighter and darker tints from these colors only when needed for hierarchy. Do not introduce unrelated hue families. When no palette is supplied, default to the original Parallel Digital blue/cyan system.

## Typography

- Use bold Chinese sans-serif for titles: Microsoft YaHei, Source Han Sans, Alibaba PuHuiTi, or equivalent.
- Keep content titles editable and native by default; image models render them
  only in explicitly declared `image` mode.
- Use the palette `text` color for main titles and main metrics.
- Use the palette `muted` color for body text.
- Use huge bold numbers for metrics when the slide has KPIs or quantitative outcomes.
- Keep Chinese text short and high-level in image-model prompts. Prefer concise labels, 2-6 word card titles, and one-line support text.
- Generated Chinese text must be inspected after image generation. Regenerate the image if key terms are wrong, repeated, malformed, overlapped, cropped, or too small.
- Vary title forms across the deck. Use fact-led, observation-led, decision-led,
  question, or concise topic titles according to the page role. Do not build the
  deck voice from repeated “不是……而是……”, “从……到……”, “先……再……”, parallel
  three-part slogans, or generic verbs such as “全面赋能” and “重新定义”.
- Prefer concrete actors, actions, objects, dates, quantities, and operating
  conditions from the source. Remove copy that could be pasted unchanged into
  an unrelated AI, digital-transformation, or SaaS presentation.

## Graphic Elements

Choose the lightest device that explains the conclusion:

- Use typography, rules, direct annotation, a real source artifact, or a native
  chart before adding symbolic illustration.
- Use a card only when it establishes a real grouping or comparison. Do not use
  cards as the universal container for every sentence.
- Use an icon only when it improves scanning or identifies a real object. Do
  not put a circular badge beside every label or fill empty space with generic
  shield, gear, cloud, chip, robot, document, or dashboard icons.
- Use connectors only for real dependency, causality, sequence, handoff, or
  flow. A decorative dashed line is not a relationship.
- Use a hub only when the source contains a genuine shared center. Do not place
  “AI”, “平台”, a glowing brain, chip, water drop, or organization logo in the
  center by habit.
- Keep user-provided screenshots and photos documentary. Crop and annotate
  them; do not restyle them into synthetic UI or generated stock imagery.

## Drawing Rules

- Use flat two-dimensional editorial drawing by default. Use isometric or 2.5D
  perspective only when physical placement or depth is part of the argument.
- Keep line weight, corner treatment, and icon style consistent within one
  visual system, but do not apply the same visual system to every page.
- Use shadows sparingly and only to clarify stacking. Prefer rules, spacing,
  alignment, and scale for hierarchy.
- Let data visuals look like credible analytical charts. Preserve axes, units,
  source notes, uncertainty, and comparison baselines when they matter; do not
  convert them into ornamental progress rings or oversized KPI tiles.
- Do not force rounded corners. Tables, evidence frames, annotations, and
  architecture layers may use square or minimally rounded geometry.

## Editorial Layout Families

### Topic Opener

Use one clear statement, source object, or thesis line. Add supporting elements
only when they prove or qualify it. Do not surround the opener with capability
nodes by default.

Examples: product ecosystem, service platform, operations center, city map, facility, hospital, logistics network, data platform, policy system, training framework.

### Overview

Use an editorial summary, annotated source artifact, compact agenda, or one
diagram that establishes the frame. Avoid the recurring left-illustration /
right-rounded-panel formula.

### Metrics

Use a real chart, comparison table, or a small number of direct metrics with
units, baselines, time periods, and source notes. KPI cards are optional, not the
default.

### Donut Result

Use a donut only for a defensible part-to-whole relationship with labeled
denominators. Do not use a donut as a decorative result symbol.

### Process

Use the actual process structure: numbered steps, swimlanes, handoff table,
annotated screenshot sequence, or a path with exception branches. Circular
nodes and bottom cards are optional.

### System / Platform / Solution

Use native layers, interfaces, boundaries, actors, or deployment zones. Keep
architecture labels editable where possible. Use a central schematic only when
the system genuinely has a center; use 2.5D only for spatial relationships.

### Capability Map

Use grouped capabilities, a dependency tree, a maturity scale, or a map of
ownership. Do not automatically place a topic node in the center.

### Shared Center / Structural Constraints

Use a shared center only when the source establishes one. Otherwise prefer an
evidence board, causal chain, comparison, or grouped list. If a hub is used,
keep satellites unequal when the evidence supports different priority or
weight; avoid decorative radial symmetry.

### Table / Matrix

Use only when the audience needs direct row-and-column comparison or lookup.
If the rows are five symptoms of one shared problem, prefer a shared-center or
evidence-board composition.

### Comparison

Use two columns, a matrix, paired source artifacts, or before/after evidence.
Keep common comparison dimensions aligned. Icons and accent tags are optional.

### Roadmap

Timeline, milestones, phase cards, or maturity ladder. Use dots, progress lines, and compact cards.

## AI Image Prompt Pattern

Use GPT Image or another image model to generate the final full-slide content PNG. First infer the topic from the user's request, reduce the message into a clean slide structure, then build the visual prompt around that topic.

Default to one final generated version per slide. First choose the page's
material form and visual source; then choose a layout:

- Verified facts: prefer source evidence, native charts, plain tables, or direct
  annotation over generated dashboards.
- Process or architecture: prefer native editable diagrams; use ImageGen only
  when the spatial or conceptual visual cannot be expressed clearly with native
  shapes.
- Conceptual judgment: allow a generated full-slide composition, but budget the
  visual devices and avoid generic AI symbols.
- Dense copy: split the page or use an editorial text-and-evidence layout; do
  not solve density by creating many rounded cards.

Do not generate several template/style alternatives unless the user asks for options. Regenerate only to fix Chinese accuracy, duplicate text, text overlap, cropped content, business meaning, or visual quality.

Choose the layout from the slide's `audience_question`, `message`,
`claim_type`, `narrative_role`, `thesis_expression`, `content_boundary`,
`information_topology`, `visual_focus`, `visual_reasoning`, `visual_source`,
`source_asset_refs`, `layout_family`, and `graphic_devices`,
not from the source format or a desire to make every page look different. The
title states the conclusion; the dominant visual system proves or explains it;
supporting elements provide evidence.

Prompt variables:

- `{domain}`: industry or context, such as manufacturing, healthcare, logistics, education, finance, public services, utilities, energy, real estate, AI platform, training, strategy, or policy.
- `{subject}`: the central visual object, such as product ecosystem, dashboard platform, service workflow, data network, facility, command center, device, map, or process scene.
- `{scenario}`: the specific user goal and slide message.
- `{visual_metaphors}`: 3-5 concrete objects or symbols that match the user's content.
- `{exact_chinese_text}`: concise image-rendered subtitles, labels, metrics, and
  proof points. Omit the title in native mode; include it only in image mode.
- `{title_render_mode}`: `native` by default, or explicit `image` / `none`.
- `{visual_source}`: source evidence, native chart, native diagram, generated
  visual, or mixed.
- `{source_asset_refs}`: the exact screenshots, documents, charts, tables,
  photos, or identifiers that must remain traceable.
- `{layout_family}`: the editorial family used to control deck-level repetition.
- `{graphic_devices}`: a short allow-list of visual devices justified by the
  page; an empty list means typography and source material should carry it.

Generic prompt pattern:

```text
16:9 full-slide Chinese executive PowerPoint page for {domain}. Narrative role: {narrative_role}. Audience question: {audience_question}. Page conclusion: {message}. Thesis expression: {thesis_expression}. Content boundary: {content_boundary}. Thesis connection: {thesis_connection}. Visual source: {visual_source}. Source asset references: {source_asset_refs}. Layout family: {layout_family}. Approved graphic devices: {graphic_devices}. Title render mode: {title_render_mode}; in native mode reserve a clean title zone and render no title, placeholder, or pseudo-text. Use a pure white solid background with no texture, pattern, background photo, or scenic wallpaper. Information topology: {information_topology}. Visual reasoning: {visual_reasoning}. Create one primary reading path: {visual_focus}. Prefer typography, source evidence, native charts, plain tables, and direct annotation before symbolic illustration. Do not add generic line icons, circular badges, rounded-card grids, a glowing AI brain or chip, fake dashboards, decorative arrows, or automatic hub-and-spoke composition. Exact palette {palette}, enterprise report style, generous whitespace, stable grid. Render only this exact concise Chinese text: {exact_chinese_text}. Do not render planning labels, prompt instructions, or deferred solution content. No text overlap, no duplicated text, no cropped text, no malformed Chinese characters, no logos.
```

If the generated result contains Chinese errors or collisions, tighten the copy and regenerate the image. Do not patch around major text defects by inserting the faulty image into the PPT.

### Direct Codex ImageGen Slide

Use this route when the user wants the image model to design the whole PPT page,
or when previous outputs looked like text placed on top of a background. In this
route, prompt Codex's built-in `image_gen` tool to generate the complete
full-slide page as one integrated bitmap.

This route is the preferred route for image-based PPT deliverables where the
user asks ImageGen / GPT Image / Codex image generation to produce the slide
pages themselves. Do not treat the image model as a background generator in this
case. Text, diagrams, KPI figures, icons, visual metaphor, and hierarchy must be
planned as one page. If the source has too much material, split the argument
across more slides or move supporting detail into speaker notes rather than
falling back to local overlay.

Prompt pattern:

```text
Use case: productivity-visual / infographic-diagram.
Asset type: complete 16:9 executive PowerPoint slide image.
Primary request: design the entire slide as one integrated executive report
page that is understandable without speaker narration. The visual composition,
Chinese text, icons, KPI figures, scene, and hierarchy must be conceived as one
whole. Do not create a background first and then place cards or text on top.
Palette: {palette}.
Topic: {slide_topic}.
Page message: {message}.
Audience question: {audience_question}.
Claim type: {claim_type}.
Narrative role: {narrative_role}.
Thesis expression: {thesis_expression}.
Content boundary: {content_boundary}.
Thesis connection: {thesis_connection}.
Title render mode: {title_render_mode}. In native mode, keep the title out of the
bitmap and reserve a clean editable-title zone with no placeholder or pseudo-text.
Exact image-rendered Chinese text: {concise_text}.
Visual source: {visual_source}.
Source asset references: {source_asset_refs}.
Layout family: {layout_family}.
Approved graphic devices: {graphic_devices}.
Canvas: pure white solid background. No background gradient, photo, texture,
pattern, glow, or decorative scene. Subtle shading inside semantic nodes is
allowed when it supports hierarchy.
Information topology: {information_topology}.
Visual reasoning: {visual_reasoning}.
Dominant visual system: {visual_focus}.
Composition direction: {specific comparison / relationship / flow / architecture / evidence board}.
Context continuity: inherit {visual_anchor_from_previous} where useful, while
preparing the audience for {transition_to_next}.
If thesis expression is implicit: do not include the deck thesis or decision
request in the image prompt; do not render or literally depict the deferred
answer. Use the thesis connection only as non-literal visual subtext.
Avoid: watermark, logo, pseudo text, invented claims, inflated slogans,
oversized opaque cards, dense bullet pages, scenic wallpaper, decorative 3D
objects, glassmorphism, excessive ornament, disconnected cards that hide real
relationships, separate background + overlay feel, generic line-icon filler,
automatic circular badges, repeated rounded-card grids, glowing AI brains or
chips, fake dashboards, decorative arrows, automatic symmetric hub-and-spoke.
```

Keep the exact visible Chinese text short. For longer source material, convert
it into speaker notes or subsequent slides rather than asking the image model to
render paragraphs. Inspect the output at full size; regenerate if any key
Chinese term is malformed, oddly spaced, or visually detached from the page.

For a deck, vary the page structure by message. Avoid repeating the same
left-title/right-card composition. Let the slide's argument choose the visual
form: two-column comparison, deployment-gap bridge, structural bottleneck map,
knowledge-foundation platform, agent expert matrix, command center dashboard,
closed-loop workflow, KPI evidence board, service-model contrast, or rollout
roadmap. The composition should carry meaning while the background remains
plain and quiet.

Also vary the material form. Use source evidence where it exists, native data
views where precision matters, plain typography where the judgment is enough,
and generated visuals only where they add explanatory value. Do not repeat the
same title grammar, icon family, center object, summary bar, or number of blocks
across adjacent pages merely to preserve consistency.

The visible text should be concise but sufficient to express the source
argument. A slide with only a title and generic labels is under-specified unless
the slide is intentionally a chapter divider or closing page.

## Negative Prompt

```text
no watermark, no logo, no generated stock-photo substitute, no cartoon, no dark cyberpunk, no neon overload, no unrelated colors, no gradient background, no background photo, no texture, no pattern, no excessive glow, no cinematic wallpaper, no floating decorative objects, no glassmorphism overload, no disconnected card collection, no generic line-icon filler, no automatic circular badges, no repeated rounded-card grid, no glowing AI brain or chip, no fake dashboard, no decorative arrows, no automatic symmetric hub-and-spoke, no excessive ornament, no clutter, no duplicated text, no overlapping text, no tiny unreadable text, no malformed Chinese characters, no random extra labels
```

## Final Image Checklist

- Size is 16:9 and meets the configured provider output size.
- One strongest version was generated for each slide by default, not multiple template alternatives.
- All text is crisp and readable.
- No AI-rendered malformed Chinese text exists.
- No repeated or duplicated Chinese phrases appear unless repetition is intentional.
- No label, title, icon, card, chart annotation, or footer text overlaps another element.
- No text is cropped at the slide edge or hidden behind decorative elements.
- Key business terms match the user's source material.
- Formulaic title structures and generic transformation slogans do not dominate
  the deck voice.
- Declared source assets remain recognizable and are not replaced by synthetic
  screenshots, dashboards, metrics, or documentary imagery.
- Bitmap copy contains only `exact_text`; a native title appears only after
  assembly, while planning labels and deck-level thesis text do not leak onto
  implicit pages.
- Every semantic object stays inside `content_boundary`; diagnosis and evidence
  pages do not prematurely depict the later solution or future state.
- Palette matches the exact hex values in `deck-plan.json`.
- The image subject clearly matches the user's topic instead of defaulting to factories or water scenes.
- No background texture competes with the main content.
- The slide still works when inserted full-bleed into the template.
- In contact-sheet thumbnail view, the main thesis and visual argument are
  still recognizable.
- Every content page uses a pure white or explicitly approved solid-color
  background with no busy decorative treatment.
- Each page has one unmistakable dominant visual system.
- A page may instead use one primary reading path carried by typography, a
  source artifact, a native chart, or a plain table; it is not forced into a
  diagram.
- The chosen topology matches the actual relationship among the ideas.
- Connectors, nodes, layers, or paths communicate meaning rather than decoration.
- The sequence has a deliberate visual rhythm and adjacent pages retain useful
  visual anchors rather than jumping between unrelated styles.
- The page does not feel like local text pasted onto a generated background.
- For direct ImageGen decks, layouts vary according to slide role rather than
  repeating one template composition.
- The contact sheet does not repeat rounded-card grids, circular icon badges,
  central hubs, decorative arrows, generic dashboards, or bottom summary bars
  as a default visual grammar.
- The deck contains visible editorial selection: different material forms are
  used because the evidence and argument differ, not to satisfy a template.
