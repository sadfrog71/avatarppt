# Image Style Guide

This guide defines the full-slide PNG style used for content pages.

## Visual Direction

Create a white-and-blue enterprise technology presentation style that adapts to the user's topic.

The feel should be clean, technical, executive, and suitable for Chinese enterprise or government-facing reporting. It should look topic-specific and intentional, not like a generic SaaS landing page. The visual subject must come from the user's actual scenario.

## Palette

Use these colors consistently:

- Navy title: `#001F3F`
- Deep template blue: `#005AAC`
- Primary blue: `#006EE9`
- Bright blue: `#1090F0`
- Mid blue: `#4F82CA`
- Cyan accent: `#1DB5CD`
- Pale blue: `#E8F2FD`
- Border blue: `#BFE1FF`
- Body gray-blue: `#506080`
- Background white: `#F8FCFF` / `#FFFFFF`

Avoid purple, orange, green, black-gold, dark cyberpunk, and heavy multi-color palettes.

## Typography

- Use bold Chinese sans-serif for titles: Microsoft YaHei, Source Han Sans, Alibaba PuHuiTi, or equivalent.
- Use dark navy for main titles and main metrics.
- Use gray-blue for body text.
- Use huge bold numbers for metrics when the slide has KPIs or quantitative outcomes.
- Render all final Chinese text with deterministic layout tools. Do not ask an image model to draw Chinese text.

## Graphic Elements

Use these recurring elements:

- Topic-specific hero illustrations: products, platforms, facilities, devices, service scenes, maps, operations centers, dashboards, data platforms, workflow scenes, or abstract domain metaphors.
- Blue line-art buildings with white fills and pale-blue shadows.
- Circular icon badges with blue gradients, white icon strokes, outer rings, and soft glow.
- Thin dashed connector lines with circular endpoints.
- Rounded white or pale-blue cards with subtle border and shadow.
- Donut charts, progress rings, horizontal metric lines, and icon-led KPI cards.
- Background texture: bottom wave lines, dot matrices, hexagon outlines, network-node lines, concentric arcs.

## Drawing Rules

- Use 30-degree isometric perspective when the subject benefits from spatial explanation, such as facilities, systems, platforms, operations centers, devices, process scenes, or multi-node networks.
- Line weight should feel vector-like: main strokes 2-4 px, detail strokes 1-2 px at 2560x1440.
- Use white fills, pale-blue surfaces, blue outlines, and small gradients for depth.
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

Use image generation for illustration layers only. First infer the topic from the user's request and build the visual prompt around that topic.

Prompt variables:

- `{domain}`: industry or context, such as manufacturing, healthcare, logistics, education, finance, public services, utilities, energy, real estate, AI platform, training, strategy, or policy.
- `{subject}`: the central visual object, such as product ecosystem, dashboard platform, service workflow, data network, facility, command center, device, map, or process scene.
- `{scenario}`: the specific user goal and slide message.
- `{visual_metaphors}`: 3-5 concrete objects or symbols that match the user's content.

Generic prompt pattern:

```text
blue-white enterprise technology presentation illustration for {domain}, {subject} representing {scenario}, include {visual_metaphors}, clean vector-like line art, optional isometric 2.5D perspective when useful, white and pale-blue surfaces, cobalt blue outlines, cyan accents, subtle technology arcs and data particles, polished Chinese enterprise report style, high clarity, no text, no labels, no people unless explicitly requested, no logos, 16:9
```

Then compose final slide text, cards, charts, and labels in HTML/CSS/SVG/Canvas before exporting the final PNG.

## Negative Prompt

```text
no Chinese text, no English text, no watermark, no logo, no stock photo, no realistic photo, no cartoon, no dark cyberpunk, no neon overload, no purple palette, no orange palette, no heavy 3D render, no clutter
```

## Final Image Checklist

- Size is 16:9 and at least `2560x1440`.
- All text is crisp and readable.
- No AI-rendered malformed text exists.
- Palette stays blue-white with the Parallel Digital cyan accent.
- The image subject clearly matches the user's topic instead of defaulting to factories or water scenes.
- Main content does not collide with subtle background texture.
- The slide still works when inserted full-bleed into the template.
