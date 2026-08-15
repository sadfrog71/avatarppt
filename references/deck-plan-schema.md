# Deck Plan Schema

Use one JSON file as the source of truth for planning, generation, QA, and assembly.

## Top-Level Fields

```json
{
  "output": "outputs/example.pptx",
  "cover_title": "專案成果匯報",
  "footer": "平行數字  交叉現實",
  "audience": "管理層",
  "objective": "形成專案決策共識",
  "language": {
    "primary": "zh-Hant",
    "preserve_terms": ["AI", "KPI", "FDE", "SCADA"]
  },
  "storyline": {
    "core_thesis": "統一知識與流程底座是智能體規模化複製的前提",
    "decision_request": "確認一期建設範圍、責任人和評估口徑",
    "audience_priority": [
      "業務價值",
      "落地可行性",
      "投入與風險"
    ],
    "story_arc": [
      {
        "move": "判斷",
        "question": "為什麼現在需要推進？",
        "answer": "現有點狀能力難以形成可複製的業務閉環"
      },
      {
        "move": "方案",
        "question": "應該建設什麼？",
        "answer": "先統一知識與流程底座，再分場景擴展智能體"
      },
      {
        "move": "決策",
        "question": "管理層今天要確認什麼？",
        "answer": "一期範圍、責任人和評估口徑"
      }
    ]
  },
  "storyline_review": {
    "status": "pass",
    "thesis_alignment": "每頁都在證明、解釋或落實中心判斷",
    "executive_relevance": "價值、可行性、風險與責任邊界足以支撐本次決策",
    "flow": "相鄰頁面可用因為、但是或所以自然連接",
    "visual_consistency": "白色底板、關係驅動構圖、統一視覺語法、主次清晰",
    "open_issues": []
  },
  "include_cover": true,
  "include_catalogue": true,
  "include_closing": true,
  "apply_palette_to_template": true,
  "authorship": {
    "mode": "editorial",
    "static_audit": "strict",
    "max_formulaic_title_ratio": 0.25,
    "max_same_layout_ratio": 0.45,
    "max_same_layout_run": 2,
    "max_exact_text_items": 14,
    "max_exact_text_characters": 220,
    "max_standard_ai_device_ratio": 0.35,
    "max_typography_first_ratio": 0.35,
    "max_same_material_form_ratio": 0.55,
    "require_conclusion_titles": true,
    "require_semantic_visual_anchor": true,
    "require_result_evidence_on_metrics": true,
    "allowed_formulaic_titles": [],
    "allowed_cliche_terms": []
  },
  "palette": {
    "name": "青綠科技",
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
    "max_accent_graphic_area_ratio": 0.30,
    "style": "clean executive technology presentation",
    "negative_prompt": "no watermark, no logo, no duplicated text, no cropped text, no gradient background, no photo background, no texture, no pattern, no excessive glow, no scenic wallpaper, no disconnected card collection, no excessive ornament"
  },
  "vision_review": {
    "enabled": true,
    "provider": "kimi",
    "model": "kimi-k3",
    "output": "outputs/image-qa.json",
    "require_pass": true,
    "deck_style_review": false,
    "contact_sheet": "outputs/contact-sheet.png"
  },
  "sections": []
}
```

## Section And Slide Fields

```json
{
  "main_title": "應用成效（一）",
  "subtitle": "營運風險識別由被動轉向提前預警",
  "slides": [
    {
      "id": "s1-01",
      "title": "提前36小時識別風險，減少被動處置",
      "audience_question": "一期建設是否已產生可驗證的業務價值？",
      "message": "風險識別提前量已超過既定目標",
      "claim_type": "fact",
      "narrative_role": "成效證據頁：證明一期建設已產生可驗證價值",
      "thesis_expression": "implicit",
      "content_boundary": "僅呈現使用者提供的風險識別證據；不展示後續平台方案、目標架構或決策請求",
      "thesis_connection": "透過可量化證據增強建設主張的可信度，但不直接複述整套主旨",
      "layout_type": "metrics",
      "title_render_mode": "native",
      "information_topology": "comparison",
      "visual_source": "native_chart",
      "source_asset_refs": [
        "source/risk-warning-metrics.xlsx"
      ],
      "layout_family": "evidence_comparison",
      "material_form": "data_visual",
      "graphic_role": "evidence",
      "graphic_area_ratio": 0.55,
      "semantic_visual_anchor": "基線、目標與實際提前量的三段對比圖",
      "graphic_devices": [
        "native baseline-target-actual chart",
        "source note"
      ],
      "exact_text": [
        "基線：平均提前6小時",
        "目標：提前24小時",
        "實際：提前36小時",
        "週期：2026年1—6月"
      ],
      "result_evidence": {
        "baseline": "平均提前6小時",
        "target": "提前24小時",
        "actual": "提前36小時",
        "time_period": "2026年1—6月",
        "source_ref": "source/risk-warning-metrics.xlsx"
      },
      "facts": [
        "只使用使用者提供且可核實的數據"
      ],
      "visual_subject": "SCADA風險預警與營運處置流程",
      "visual_focus": "頁面中心的基線、目標與實際提前量對比",
      "visual_reasoning": "三組同口徑數值需要在同一尺度直接比較，數據對比比中心輻射更適合",
      "transition": {
        "from_previous": "承接上一頁對一期建設目標的說明",
        "to_next": "價值已得到驗證，下一頁回答如何把單點成果複製到更多場景"
      },
      "speaker_notes": "先講結論，再解釋口徑和數據來源，最後引出規模化複製問題。",
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
- Use `authorship` to configure the zero-cost style audit. `static_audit=warn`
  reports risks without blocking older plans; `static_audit=strict` turns any
  style warning into a generation gate. Use `strict` for new plans and release
  candidates; plans without `authorship` remain warning-only for compatibility.
  Ratio thresholds must be between 0 and 1. Keep
  `allowed_formulaic_titles` and `allowed_cliche_terms` narrow and source-
  justified.
- For new executive plans, set `language.primary=zh-Hant`. Write prose in
  Traditional Chinese while preserving exact English abbreviations in
  `language.preserve_terms`, including `AI`, `KPI`, `FDE`, and `SCADA` unless
  the source requires another policy.
- Set `image_generation.max_accent_graphic_area_ratio` to a value greater than
  0 and no greater than 0.30. The default is 0.30.
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
  conclusion. Except for cover, chapter, and closing pages, write the `title`
  as the conclusion itself. Prefer “提前36小時識別風險，減少被動處置” over a
  topic label such as “專案成效” or “平台架構”.
- Read all titles as one sequence. Keep contrast formulas such as
  “不是……而是……”, “从……到……”, and “先……再……” below the configured ratio unless
  the source argument genuinely depends on that contrast. Mix fact-led,
  observation-led, decision-led, question, and concise topic titles.
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
- For new plans, set `visual_source` to `source_evidence`, `native_chart`,
  `native_diagram`, `generated_visual`, or `mixed`. Record traceable screenshots,
  documents, tables, charts, photos, or identifiers in `source_asset_refs`.
  Give each page a concise `layout_family` so the static audit can detect deck-
  level repetition. Set `graphic_role` to `accent`, `explanatory`, `evidence`,
  or intentional `none`, and estimate `graphic_area_ratio` from 0 to 1. Default
  conceptual pages to `accent` at roughly 0.15-0.30. Frameworks, processes,
  narrative concepts, charts, screenshots, and source objects may use
  `explanatory` or `evidence` and exceed 0.30 because they carry information.
  Declare `material_form` as `typography`, `source_evidence`, `data_visual`,
  `diagram`, `illustration`, `table`, or `mixed`. For every non-typographic
  graphic role, write one `semantic_visual_anchor`: the non-text object, data
  pattern, framework, process, spatial system, or concept visual that carries
  at least one layer of meaning. “Three columns”, “large text”, “arrows”, and
  empty boxes are layout instructions, not semantic anchors.
  Use `graphic_devices` as an allow-list; individual icons, cards, hubs, arrows,
  or illustrations are acceptable when relevant, but do not repeat them as a
  generic deck-wide visual system.
- Write `transition.from_previous` and `transition.to_next` for every content
  slide. Read them in sequence before generation; adjacent pages must connect
  causally rather than only share a topic.
- Put explanations needed for delivery in `speaker_notes`; keep generated image
  text concise. The title plus the visual should communicate the main conclusion
  and relationship without depending on an unusually skilled speaker.
- On metrics and outcome pages, add `result_evidence` with `baseline`, `target`,
  `actual`, and `time_period`; use `null` only to record a genuine source gap.
  Put supplied values in the title or `exact_text`, keep units and dates exact,
  and record `source_ref`. Never invent a missing baseline or result.
- Treat `exact_text` as the exclusive visible-copy contract. Do not render
  `core_thesis`, `decision_request`, planning field names, transitions, or
  speaker notes unless the intended words are also present in `exact_text`.
- New plans default to `title_render_mode=native`: do not include the title in
  `exact_text`, reserve a clean title zone in the bitmap, and let the assembler
  add the title as editable PowerPoint text. Set `title_render_mode=image` only
  when the title must be part of the integrated bitmap, and then include the
  complete title in `exact_text`. Use `none` only for an intentional untitled
  page. Plans created before the `authorship` contract retain image-title
  behavior for compatibility.
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
- Before paid generation, run `scripts/audit_deck_style.py`. Resolve high-risk
  formulaic copy, dense generated text, dominant layout families, long repeated
  runs, topic-only titles, overused typography-first or single material forms,
  undeclared evidence sources, missing semantic anchors, incomplete result
  evidence, excessive planned graphics, and common AI-default visual devices.
- Set `vision_review.deck_style_review=true` only after confirming one
  additional paid Kimi call. The review uses the ordered contact sheet to judge
  repeated layouts, generic visual grammar, material specificity, copy rhythm,
  and editorial authorship across the deck.
- Avoid exaggerated, promotional conclusions in `exact_text` and prompts. Do
  not invent lines such as "不是追赶者，而是定义者"; use restrained claims tied to
  the source outline.
