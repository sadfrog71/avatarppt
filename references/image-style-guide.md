# Image Style Guide

This guide defines the full-slide PNG style used for content pages.

## Contents

- [Visual Direction](#visual-direction)
- [Executive Visual Hierarchy](#executive-visual-hierarchy)
- [Information Topology First](#information-topology-first)
- [Palette](#palette)
- [Typography](#typography)
- [Graphic Elements](#graphic-elements)
- [Drawing Rules](#drawing-rules)
- [Page Recipes](#page-recipes)
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

## Executive Visual Hierarchy

Design for a decision-maker scanning the page from a distance:

- Use a pure solid-color canvas, white by default. Do not add background
  gradients, photos, textures, patterns, glow, decorative scenery, or
  atmospheric background art.
  Use another solid brand color only when the user explicitly requests it.
- Give every page one dominant visual system or focus region. This may be a
  single number or object, or a connected group of nodes, layers, arrows, or
  evidence items when the relationship itself is the message.
- Use enough graphical structure to make the idea legible. A center with five
  connected dimensions is still one visual system; five unrelated decorative
  cards are not.
- Keep accent color controlled, typically around 10-20% of the page, and use it
  to encode active relationships, priorities, key numbers, or risks.
- Prefer generous whitespace, stable alignment, and clear scale contrast over
  decoration. A management slide may feel visually calm while still looking
  deliberate and high quality.
- Allow restrained connectors, nodes, containers, rings, paths, and flat color
  blocks when they encode business meaning. Use cinematic scenes, complex
  isometric worlds, glassmorphism, glow, and floating objects only when the user
  explicitly requests them.

Across a deck, keep title position, margins, palette, icon language, line style,
and typography stable. Vary composition according to the reasoning: diagnose,
compare, explain, prove, sequence, or decide. Adjacent pages that discuss the
same system should retain a visual anchor; a new visual language should signal a
real narrative shift.

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
- Use the palette `text` color for main titles and main metrics.
- Use the palette `muted` color for body text.
- Use huge bold numbers for metrics when the slide has KPIs or quantitative outcomes.
- Keep Chinese text short and high-level in image-model prompts. Prefer concise labels, 2-6 word card titles, and one-line support text.
- Generated Chinese text must be inspected after image generation. Regenerate the image if key terms are wrong, repeated, malformed, overlapped, cropped, or too small.

## Graphic Elements

Choose only the elements needed to explain the conclusion; do not use this as a
decoration checklist:

- Topic-specific hero illustrations: products, platforms, facilities, devices, service scenes, maps, operations centers, dashboards, data platforms, workflow scenes, or abstract domain metaphors.
- Palette-colored line-art subjects with background-colored fills and restrained shadows.
- Circular icon badges using `primary`, `secondary`, and `accent`, with white or background-colored icon strokes.
- Thin dashed connector lines with circular endpoints.
- Rounded background-colored cards with subtle palette borders and shadows.
- Donut charts, progress rings, horizontal metric lines, and icon-led KPI cards.
- Solid white or user-approved solid-color background with no decorative
  texture.

## Drawing Rules

- Use 30-degree isometric perspective when the subject benefits from spatial explanation, such as facilities, systems, platforms, operations centers, devices, process scenes, or multi-node networks.
- Line weight should feel vector-like: main strokes 2-4 px, detail strokes 1-2 px at 2560x1440.
- Use solid fills, palette tints, primary outlines, restrained shadows, and
  subtle object-level shading for depth. Keep the slide background flat and
  quiet.
- Icons should be simple, geometric, and consistent. Select icons from the user's domain, such as shield, gear, cloud, AI chip, dashboard, facility, device, user, service, map, sensor, document, link, chart, trophy, wallet, hospital, logistics, energy, education, or policy symbols.
- Cards should have light blue borders, 18-28 px visual radius at 2560x1440, and soft shadows.
- Data visuals should be readable and not Excel-like.

## Page Recipes

### Topic Opener

Use one central subject or thesis statement with 3-5 capability/value nodes. Add
a KPI/status badge only if the content includes a real metric.

Examples: product ecosystem, service platform, operations center, city map, facility, hospital, logistics network, data platform, policy system, training framework.

### Overview

Left 35-45%: thematic illustration matched to the user's scenario.

Right 55-65%: large rounded panel with 4-6 icon-led information rows.

### Metrics

Grid of KPI cards with large numbers. Use circular icons and thin blue accent lines. Optional right-side case image placeholder.

### Donut Result

Large donut chart on the left, icon explanation list in the middle, case image placeholder on the right.

### Process

Horizontal circular nodes connected by arrows. The number of nodes should match the actual process, usually 4-6. Add short labels below each node and explanation cards along the bottom.

### System / Platform / Solution

Use a central simplified schematic chosen from the content: system, product,
platform, service, facility, workflow, or solution architecture. Use 2.5D only
when spatial relationships are essential. Put only necessary evidence on the
sides and connect it to the center.

### Capability Map

Central topic subject with surrounding circular capability nodes connected by thin lines.

### Shared Center / Structural Constraints

Use a central subject, root issue, or enterprise capability with 4-7 connected
dimensions around it. Give each satellite a short label and one concise impact
line. Vary size or accent only when the source supports priority. Use connectors
to show shared dependence, not to imply unsupported causality.

### Table / Matrix

Use only when the audience needs direct row-and-column comparison or lookup.
If the rows are five symptoms of one shared problem, prefer a shared-center or
evidence-board composition.

### Comparison

Two-column, matrix, or before/after structure. Use restrained accent tags, icon-led rows, and clear contrast without using harsh red/green unless the user requests it.

### Roadmap

Timeline, milestones, phase cards, or maturity ladder. Use dots, progress lines, and compact cards.

## AI Image Prompt Pattern

Use GPT Image or another image model to generate the final full-slide content PNG. First infer the topic from the user's request, reduce the message into a clean slide structure, then build the visual prompt around that topic.

Default to one final generated version per slide. Pick the page recipe automatically by judging how much detail and text the slide needs:

- More text or many facts: use panels, matrices, status cards, or information architecture diagrams.
- Fewer words or conceptual messages: use central illustrations, capability maps, curves, or process visuals.
- Mixed facts and judgment: use a main visual plus 3-5 concise evidence cards.

Do not generate several template/style alternatives unless the user asks for options. Regenerate only to fix Chinese accuracy, duplicate text, text overlap, cropped content, business meaning, or visual quality.

Choose the recipe from the slide's `audience_question`, `message`,
`claim_type`, `information_topology`, `visual_focus`, and `visual_reasoning`,
not from the source format or a desire to make every page look different. The
title states the conclusion; the dominant visual system proves or explains it;
supporting elements provide evidence.

Prompt variables:

- `{domain}`: industry or context, such as manufacturing, healthcare, logistics, education, finance, public services, utilities, energy, real estate, AI platform, training, strategy, or policy.
- `{subject}`: the central visual object, such as product ecosystem, dashboard platform, service workflow, data network, facility, command center, device, map, or process scene.
- `{scenario}`: the specific user goal and slide message.
- `{visual_metaphors}`: 3-5 concrete objects or symbols that match the user's content.
- `{exact_chinese_text}`: concise Chinese title, subtitles, labels, and card text to render. Keep it sparse and avoid long paragraphs.

Generic prompt pattern:

```text
16:9 full-slide Chinese executive PowerPoint page for {domain}. Audience question: {audience_question}. Conclusion: {message}. Use a pure white solid background with no texture, pattern, photo, or scenic wallpaper. Information topology: {information_topology}. Visual reasoning: {visual_reasoning}. Create one dominant visual system: {visual_focus}. Allow restrained nodes, connectors, arrows, containers, rings, icons, and pale color blocks when they encode real relationships. Exact palette {palette}, enterprise report style, generous whitespace, stable grid, render this exact concise Chinese text: {exact_chinese_text}, no text overlap, no duplicated text, no cropped text, no malformed Chinese characters, no logos
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
Core message: {message}.
Audience question: {audience_question}.
Claim type: {claim_type}.
Exact visible Chinese text: {concise_text}.
Canvas: pure white solid background. No background gradient, photo, texture,
pattern, glow, or decorative scene. Subtle shading inside semantic nodes is
allowed when it supports hierarchy.
Information topology: {information_topology}.
Visual reasoning: {visual_reasoning}.
Dominant visual system: {visual_focus}.
Composition direction: {specific comparison / relationship / flow / architecture / evidence board}.
Context continuity: inherit {visual_anchor_from_previous} where useful, while
preparing the audience for {transition_to_next}.
Avoid: watermark, logo, pseudo text, invented claims, inflated slogans,
oversized opaque cards, dense bullet pages, scenic wallpaper, decorative 3D
objects, glassmorphism, excessive ornament, disconnected cards that hide real
relationships, separate background + overlay feel.
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

The visible text should be concise but sufficient to express the source
argument. A slide with only a title and generic labels is under-specified unless
the slide is intentionally a chapter divider or closing page.

## Negative Prompt

```text
no watermark, no logo, no stock photo, no realistic photo, no cartoon, no dark cyberpunk, no neon overload, no unrelated colors, no gradient background, no background photo, no texture, no pattern, no excessive glow, no cinematic wallpaper, no floating decorative objects, no glassmorphism overload, no disconnected card collection, no excessive ornament, no clutter, no duplicated text, no overlapping text, no tiny unreadable text, no malformed Chinese characters, no random extra labels
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
- Palette matches the exact hex values in `deck-plan.json`.
- The image subject clearly matches the user's topic instead of defaulting to factories or water scenes.
- No background texture competes with the main content.
- The slide still works when inserted full-bleed into the template.
- In contact-sheet thumbnail view, the main thesis and visual argument are
  still recognizable.
- Every content page uses a pure white or explicitly approved solid-color
  background with no busy decorative treatment.
- Each page has one unmistakable dominant visual system.
- The chosen topology matches the actual relationship among the ideas.
- Connectors, nodes, layers, or paths communicate meaning rather than decoration.
- The sequence has a deliberate visual rhythm and adjacent pages retain useful
  visual anchors rather than jumping between unrelated styles.
- The page does not feel like local text pasted onto a generated background.
- For direct ImageGen decks, layouts vary according to slide role rather than
  repeating one template composition.
