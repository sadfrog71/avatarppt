# Deck Plan Schema

Use one JSON file as the source of truth for planning, generation, QA, and assembly.

## Top-Level Fields

```json
{
  "output": "outputs/example.pptx",
  "cover_title": "项目成果汇报",
  "footer": "平行数字  交叉现实",
  "audience": "管理层",
  "objective": "形成项目决策共识",
  "include_cover": true,
  "include_catalogue": true,
  "include_closing": true,
  "apply_palette_to_template": true,
  "palette": {
    "name": "青绿科技",
    "primary": "#0B6E69",
    "secondary": "#174A5B",
    "accent": "#F2B134",
    "background": "#F7FBFA",
    "text": "#102A2E",
    "muted": "#6B7F80"
  },
  "image_generation": {
    "provider": "openai",
    "model": "gpt-image-2",
    "size": "2048x1152",
    "quality": "high",
    "composition_mode": "direct_imagegen_slide",
    "style": "clean executive technology presentation",
    "negative_prompt": "no watermark, no logo, no duplicated text, no cropped text"
  },
  "vision_review": {
    "enabled": true,
    "provider": "kimi",
    "model": "kimi-k3",
    "output": "outputs/image-qa.json",
    "require_pass": true
  },
  "sections": []
}
```

## Section And Slide Fields

```json
{
  "main_title": "应用成效（一）",
  "subtitle": "运营效率全面提升",
  "slides": [
    {
      "id": "s1-01",
      "title": "运营效率指标",
      "message": "核心流程效率得到可量化提升",
      "layout_type": "metrics",
      "exact_text": [
        "运营效率指标",
        "处理时长",
        "自动化率"
      ],
      "facts": [
        "只放用户提供且可核实的数据"
      ],
      "visual_subject": "运营指挥中心与数据流程",
      "prompt": "",
      "image": "images/s1-01.png"
    }
  ]
}
```

## Planning Rules

- Keep `id` and `image` unique.
- Use valid six-digit hex colors.
- Keep `exact_text` concise and designed for the page. Short labels should
  normally be under 18 Chinese characters, but thesis lines, KPI captions, and
  evidence points may be longer when they are necessary for the slide to carry
  the source argument. Avoid long paragraphs; split pages or use speaker notes
  when the visible text would become dense.
- Put real quantitative claims in `facts`; do not synthesize unsupported values.
- Leave `prompt` empty only when `generate_images.py` should compose it from the structured fields.
- Keep at most four sections when `include_catalogue` is true.
- Use PNG output paths.
- Use `image_generation.composition_mode = "direct_imagegen_slide"` when Codex
  should call built-in `image_gen` to design each whole slide as one integrated
  page. In that mode, do not set `local_text_overlay` and do not ask the
  provider to create a text-free background. The prompt must bind Chinese text,
  diagrams, KPI figures, scene, and information hierarchy into one visual
  argument, and should avoid repeated template-like compositions across the
  deck.
- Avoid exaggerated, promotional conclusions in `exact_text` and prompts. Do
  not invent lines such as "不是追赶者，而是定义者"; use restrained claims tied to
  the source outline.
