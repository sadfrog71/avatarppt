# Image Style Guide

This guide defines the full-slide PNG style used for content pages.

## Visual Direction

Create a white-and-blue smart water / industrial AI / digital factory style.

The feel should be clean, technical, executive, and suitable for Chinese enterprise or government-facing reporting. It should look like a polished smart-water solution presentation, not a generic SaaS landing page.

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
- Use huge bold numbers for KPIs.
- Render all final Chinese text with deterministic layout tools. Do not ask an image model to draw Chinese text.

## Graphic Elements

Use these recurring elements:

- Isometric 2.5D water treatment plants, factories, dashboards, data platforms.
- Blue line-art buildings with white fills and pale-blue shadows.
- Circular icon badges with blue gradients, white icon strokes, outer rings, and soft glow.
- Thin dashed connector lines with circular endpoints.
- Rounded white or pale-blue cards with subtle border and shadow.
- Donut charts, progress rings, horizontal metric lines, and icon-led KPI cards.
- Background texture: bottom wave lines, dot matrices, hexagon outlines, network-node lines, concentric arcs.

## Drawing Rules

- Industrial scenes should use 30-degree isometric perspective.
- Line weight should feel vector-like: main strokes 2-4 px, detail strokes 1-2 px at 2560x1440.
- Use white fills, pale-blue surfaces, blue outlines, and small gradients for depth.
- Icons should be simple, geometric, and consistent: water drop, shield, gear, cloud, AI chip, dashboard, factory, trophy, sensor, link, chart.
- Cards should have light blue borders, 18-28 px visual radius at 2560x1440, and soft shadows.
- Data visuals should be readable and not Excel-like.

## Page Recipes

### Overview

Left 40%: isometric plant illustration.

Right 60%: large rounded panel with 5-6 icon rows.

### Metrics

Grid of KPI cards with large numbers. Use circular icons and thin blue accent lines. Optional right-side case image placeholder.

### Donut Result

Large donut chart on the left, icon explanation list in the middle, case image placeholder on the right.

### Process

Five horizontal circular nodes connected by arrows. Add short labels below each node and explanation cards along the bottom.

### Platform

Central 2.5D dashboard/platform. Feature cards on left and right. Dashed lines connect cards to the center.

### Capability Map

Central factory or platform. Surrounding circular icon nodes connected with thin lines.

## AI Image Prompt Pattern

Use image generation for illustration layers only:

```text
blue-white smart water industrial AI illustration, isometric 2.5D water treatment plant, clean vector-like line art, white building surfaces, cobalt blue outlines, pale blue shadows, subtle technology arcs and data particles, enterprise presentation style, high clarity, no text, no labels, no people, no logos, 16:9
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
- Main content does not collide with subtle background texture.
- The slide still works when inserted full-bleed into the template.
