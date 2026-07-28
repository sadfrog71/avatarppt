# Image Style Guide

This guide defines the full-slide PNG style used for content pages.

## Visual Direction

Create a palette-controlled enterprise presentation style that adapts to the user's topic.

The feel should be clean, technical, executive, and suitable for Chinese enterprise or government-facing reporting. It should look topic-specific and intentional, not like a generic SaaS landing page. The visual subject must come from the user's actual scenario. The user palette is authoritative.

Keep the communication restrained. Do not add heroic slogans, market-leader
claims, winner/loser framing, or exaggerated language that the source did not
state. Avoid lines such as "不是追赶者，而是定义者", "重新定义行业", "行业唯一",
or "绝对领先" unless the user explicitly asks for that exact language. Prefer
measurable, neutral wording.

## Palette

Use the exact colors from `deck-plan.json` consistently:

- `primary`: main structures, data series, strong borders, and major icons.
- `secondary`: title bands, deep surfaces, and supporting structures.
- `accent`: highlights, active nodes, callouts, and no more than 15% of the page.
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

Use these recurring elements:

- Topic-specific hero illustrations: products, platforms, facilities, devices, service scenes, maps, operations centers, dashboards, data platforms, workflow scenes, or abstract domain metaphors.
- Palette-colored line-art subjects with background-colored fills and restrained shadows.
- Circular icon badges using `primary`, `secondary`, and `accent`, with white or background-colored icon strokes.
- Thin dashed connector lines with circular endpoints.
- Rounded background-colored cards with subtle palette borders and shadows.
- Donut charts, progress rings, horizontal metric lines, and icon-led KPI cards.
- Background texture: bottom wave lines, dot matrices, hexagon outlines, network-node lines, concentric arcs.

## Drawing Rules

- Use 30-degree isometric perspective when the subject benefits from spatial explanation, such as facilities, systems, platforms, operations centers, devices, process scenes, or multi-node networks.
- Line weight should feel vector-like: main strokes 2-4 px, detail strokes 1-2 px at 2560x1440.
- Use background fills, palette tints, primary outlines, and small gradients for depth.
- Icons should be simple, geometric, and consistent. Select icons from the user's domain, such as shield, gear, cloud, AI chip, dashboard, facility, device, user, service, map, sensor, document, link, chart, trophy, wallet, hospital, logistics, energy, education, or policy symbols.
- Cards should have light blue borders, 18-28 px visual radius at 2560x1440, and soft shadows.
- Data visuals should be readable and not Excel-like.

## Page Recipes

### Topic Opener

Central subject illustration chosen from the user's deck topic. Surround it with 4-6 circular capability/value nodes. Add an optional KPI/status badge only if the content includes a real metric.

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

Central 2.5D subject illustration chosen from the content: system, product, platform, service, facility, workflow, or solution architecture. Feature cards sit on the left and right. Dashed lines connect cards to the center.

### Capability Map

Central topic subject with surrounding circular capability nodes connected by thin lines.

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

Prompt variables:

- `{domain}`: industry or context, such as manufacturing, healthcare, logistics, education, finance, public services, utilities, energy, real estate, AI platform, training, strategy, or policy.
- `{subject}`: the central visual object, such as product ecosystem, dashboard platform, service workflow, data network, facility, command center, device, map, or process scene.
- `{scenario}`: the specific user goal and slide message.
- `{visual_metaphors}`: 3-5 concrete objects or symbols that match the user's content.
- `{exact_chinese_text}`: concise Chinese title, subtitles, labels, and card text to render. Keep it sparse and avoid long paragraphs.

Generic prompt pattern:

```text
16:9 full-slide Chinese enterprise PowerPoint page for {domain}, {subject} representing {scenario}, include {visual_metaphors}, exact palette {palette}, clean vector-like line art, optional isometric 2.5D perspective when useful, polished executive report style, render this exact concise Chinese text: {exact_chinese_text}, clear hierarchy, generous whitespace, no text overlap, no duplicated text, no cropped text, no malformed Chinese characters, no logos
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
Exact visible Chinese text: {concise_text}.
Composition direction: {specific scene / metaphor / flow / architecture}.
Avoid: watermark, logo, pseudo text, invented claims, inflated slogans,
oversized opaque cards, dense bullet pages, separate background + overlay feel.
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
roadmap. The background should carry meaning, not serve as decorative wallpaper.

The visible text should be concise but sufficient to express the source
argument. A slide with only a title and generic labels is under-specified unless
the slide is intentionally a chapter divider or closing page.

## Negative Prompt

```text
no watermark, no logo, no stock photo, no realistic photo, no cartoon, no dark cyberpunk, no neon overload, no unrelated colors, no heavy 3D render, no clutter, no duplicated text, no overlapping text, no tiny unreadable text, no malformed Chinese characters, no random extra labels
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
- Main content does not collide with subtle background texture.
- The slide still works when inserted full-bleed into the template.
- In contact-sheet thumbnail view, the main thesis and visual argument are
  still recognizable.
- The page does not feel like local text pasted onto a generated background.
- For direct ImageGen decks, layouts vary according to slide role rather than
  repeating one template composition.
