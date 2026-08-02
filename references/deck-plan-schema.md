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
  "storyline": {
    "core_thesis": "统一知识与流程底座是智能体规模化复制的前提",
    "decision_request": "确认一期建设范围、责任人和评估口径",
    "audience_priority": [
      "业务价值",
      "落地可行性",
      "投入与风险"
    ],
    "story_arc": [
      {
        "move": "判断",
        "question": "为什么现在需要推进？",
        "answer": "现有点状能力难以形成可复制的业务闭环"
      },
      {
        "move": "方案",
        "question": "应该建设什么？",
        "answer": "先统一知识与流程底座，再分场景扩展智能体"
      },
      {
        "move": "决策",
        "question": "管理层今天要确认什么？",
        "answer": "一期范围、责任人和评估口径"
      }
    ]
  },
  "storyline_review": {
    "status": "pass",
    "thesis_alignment": "每页都在证明、解释或落实中心判断",
    "executive_relevance": "价值、可行性、风险与责任边界足以支撑本次决策",
    "flow": "相邻页面可用因为、但是或所以自然连接",
    "visual_consistency": "白色底板、关系驱动构图、统一视觉语法、主次清晰",
    "open_issues": []
  },
  "include_cover": true,
  "include_catalogue": true,
  "include_closing": true,
  "apply_palette_to_template": true,
  "palette": {
    "name": "青绿科技",
    "primary": "#0B6E69",
    "secondary": "#174A5B",
    "accent": "#F2B134",
    "background": "#FFFFFF",
    "text": "#102A2E",
    "muted": "#6B7F80"
  },
  "image_generation": {
    "provider": "openai",
    "model": "gpt-image-2",
    "size": "2048x1152",
    "quality": "high",
    "composition_mode": "direct_imagegen_slide",
    "background_mode": "solid",
    "allow_nonwhite_background": false,
    "style": "clean executive technology presentation",
    "negative_prompt": "no watermark, no logo, no duplicated text, no cropped text, no gradient background, no photo background, no texture, no pattern, no excessive glow, no scenic wallpaper, no disconnected card collection, no excessive ornament"
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
      "title": "核心流程效率已具备量化验证基础",
      "audience_question": "一期建设是否已经产生可验证的业务价值？",
      "message": "核心流程效率得到可量化提升",
      "claim_type": "fact",
      "narrative_role": "成效证据页：证明一期建设已产生可验证价值",
      "thesis_expression": "implicit",
      "content_boundary": "仅呈现用户提供的前后效率证据；不展示后续平台方案、目标架构或决策请求",
      "thesis_connection": "通过可量化证据增强建设主张的可信度，但不直接复述整套主旨",
      "layout_type": "metrics",
      "information_topology": "comparison",
      "exact_text": [
        "核心流程效率已具备量化验证基础",
        "处理时长",
        "自动化率"
      ],
      "facts": [
        "只放用户提供且可核实的数据"
      ],
      "visual_subject": "运营指挥中心与数据流程",
      "visual_focus": "一组占据页面中心的前后效率对比指标",
      "visual_reasoning": "前后指标需要在同一坐标中直接比较，比较结构比中心辐射更适合",
      "transition": {
        "from_previous": "承接上一页对一期建设目标的说明",
        "to_next": "价值已得到验证，下一页回答如何把单点成果复制到更多场景"
      },
      "speaker_notes": "先讲结论，再解释口径和数据来源，最后引出规模化复制问题。",
      "prompt": "",
      "image": "images/s1-01.png"
    }
  ]
}
```

## Planning Rules

- Write `storyline` before creating slide prompts. `core_thesis` must be one
  specific judgment, not a generic topic. `decision_request` must name the
  alignment, approval, or next action expected from the audience.
- Keep `story_arc` to 3-6 causal moves. Each move must contain `move`,
  `question`, and `answer`.
- Complete `storyline_review` after reviewing the full storyboard as a senior
  solution expert. Set `status` to `pass` only when thesis alignment, executive
  relevance, page flow, and visual consistency have been checked and
  `open_issues` is empty. Validation blocks image generation otherwise.
- Keep `id` and `image` unique.
- Use valid six-digit hex colors.
- Keep `exact_text` concise and designed for the page. Short labels should
  normally be under 18 Chinese characters, but thesis lines, KPI captions, and
  evidence points may be longer when they are necessary for the slide to carry
  the source argument. Avoid long paragraphs; split pages or use speaker notes
  when the visible text would become dense.
- Put real quantitative claims in `facts`; do not synthesize unsupported values.
- Use `claim_type` to distinguish `fact`, `inference`, `proposal`, and
  `decision`. Do not write an inference or proposal as a fact.
- Write `narrative_role` in natural language to state what the page does in the
  argument. Do not use it as another rigid layout enum.
- Set `thesis_expression` to `implicit` by default. Use `explicit` only when the
  page intentionally reveals the deck thesis and that claim belongs to the
  page's source-backed argument.
- Write `content_boundary` as a semantic fence covering both copy and imagery:
  what the page may show and what later solution, future-state, outcome, or
  decision content must remain deferred.
- Write `thesis_connection` to explain how the page advances the deck thesis
  through evidence, tension, continuity, or transition. Thesis alignment does
  not require repeating or literally illustrating the thesis.
- Make `audience_question` the question the page answers and `message` the
  conclusion. Except for cover, chapter, and closing pages, prefer a
  conclusion-led `title` over a topic label.
- Define one `visual_focus` per page. It should describe the first object,
  relationship, or visual system the audience sees. It may contain multiple
  connected elements when the relationship itself is the message.
- Write `information_topology` as a concise structural description such as
  `hub_spoke`, `causal_chain`, `flow`, `layers`, `comparison`, `evidence_board`,
  `network`, `spatial_system`, or another topology justified by the content.
  Treat these as guidance, not a closed template list.
- Write `visual_reasoning` to explain why the selected topology expresses the
  slide's conclusion better than a table, bullet list, or unrelated cards. Do
  not mechanically preserve the source format.
- Write `transition.from_previous` and `transition.to_next` for every content
  slide. Read them in sequence before generation; adjacent pages must connect
  causally rather than only share a topic.
- Put explanations needed for delivery in `speaker_notes`; keep generated image
  text concise.
- Treat `exact_text` as the exclusive visible-copy contract. Do not render
  `core_thesis`, `decision_request`, planning field names, transitions, or
  speaker notes unless the intended words are also present in `exact_text`.
- For `thesis_expression = implicit`, omit the deck thesis and decision request
  from the image prompt. Reject literal depictions of deferred solutions even
  when they contain no text; visual objects also make claims.
- Default `palette.background` to `#FFFFFF`. Use a pure solid-color canvas with
  no background photo, texture, pattern, glow, or scenic wallpaper unless the
  user explicitly requests a different background treatment. Allow restrained
  shapes, connectors, flat tints, and subtle object-level shading when they
  encode relationships. Set
  `image_generation.allow_nonwhite_background` to `true` only for that explicit
  exception.
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
