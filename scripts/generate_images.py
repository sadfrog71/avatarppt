#!/usr/bin/env python3
"""Generate palette-controlled slide images from a validated deck plan."""

from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Any

from audit_deck_style import audit_plan
from credential_store import get_provider_secret
from deck_utils import (
    image_rendered_text,
    iter_slides,
    language_policy_description,
    load_plan,
    max_accent_graphic_area_ratio,
    palette_description,
    resolve_path,
    resolved_graphic_area_ratio,
    resolved_graphic_role,
    resolved_title_render_mode,
    result_evidence_items,
)
from validate_plan import validate_plan


OPENAI_ENDPOINT = "https://api.openai.com/v1/images/generations"
MINIMAX_ENDPOINTS = {
    "cn": "https://api.minimaxi.com/v1/image_generation",
    "global": "https://api.minimax.io/v1/image_generation",
}


def build_prompt(plan: dict[str, Any], slide: dict[str, Any]) -> str:
    generation = plan["image_generation"]
    storyline = plan["storyline"]
    facts = "; ".join(slide.get("facts", [])) or "no unsupported numeric claims"
    visual_source = slide.get("visual_source", "not declared")
    source_asset_refs = "; ".join(slide.get("source_asset_refs", [])) or "none"
    layout_family = slide.get("layout_family", slide["information_topology"])
    graphic_devices = "; ".join(slide.get("graphic_devices", [])) or "only devices justified by the content"
    graphic_role = resolved_graphic_role(plan, slide)
    graphic_area_ratio = resolved_graphic_area_ratio(plan, slide)
    max_accent_ratio = max_accent_graphic_area_ratio(plan)
    max_accent_percent = round(max_accent_ratio * 100)
    language_instruction = language_policy_description(plan)
    material_form = str(slide.get("material_form") or "not declared")
    semantic_visual_anchor = str(
        slide.get("semantic_visual_anchor") or "not declared"
    )
    result_evidence = result_evidence_items(slide)
    if result_evidence:
        evidence_instruction = (
            "Prioritize this result evidence in the main visual: "
            + "; ".join(
                f"{key}={value}" for key, value in result_evidence.items()
            )
            + ". Show baseline, target, actual result, and time period together "
            "when supplied; preserve every value and unit exactly. "
        )
    else:
        evidence_instruction = (
            "Do not invent a baseline, target, actual result, time period, or KPI. "
        )
    if graphic_role == "accent":
        target_percent = round((graphic_area_ratio or max_accent_ratio) * 100)
        graphic_instruction = (
            "Use one or two semantic graphic accents or a compact illustrative "
            f"vignette occupying about {target_percent}% of the usable content area "
            f"and never more than {max_accent_percent}%. Do not make the page "
            "text-only or line-only when a visual cue would improve comprehension. "
        )
    elif graphic_role in {"explanatory", "evidence"}:
        graphic_instruction = (
            "The chart, framework, process, concept diagram, screenshot, or evidence "
            "object is information-bearing and may occupy more than the accent cap. "
            f"Keep any secondary decorative graphics within {max_accent_percent}%. "
        )
    elif graphic_role == "none":
        graphic_instruction = (
            "This is an intentionally typography-led page. Do not add an illustration, "
            "but maintain a complete composition through scale, spacing, and alignment. "
        )
    else:
        graphic_instruction = (
            "Use meaningful graphic accents when they improve scanning or explanation. "
            "Do not interpret anti-template constraints as a ban on graphics. "
        )
    title_render_mode = resolved_title_render_mode(plan, slide)
    if title_render_mode == "native":
        title_instruction = (
            "Reserve a clean title zone for editable native PowerPoint text. "
            "Do not render the title, a title placeholder, or pseudo-text. "
        )
    elif title_render_mode == "none":
        title_instruction = "Do not render a title or reserve a title placeholder. "
    else:
        title_instruction = "Render the title only when it appears in exact_text. "
    if visual_source in {"source_evidence", "mixed"}:
        provenance_instruction = (
            "Do not redraw, imitate, or fabricate the declared source assets. "
            "This text-only provider call does not attach them; preserve a designed "
            "evidence region for an asset-aware or local composition step. "
        )
    else:
        provenance_instruction = "Do not fabricate screenshots, documentary photos, or data evidence. "
    negative = generation.get(
        "negative_prompt",
        "no watermark, no logo, no duplicated text, no cropped text",
    )
    if generation.get("local_text_overlay"):
        text_constraint = (
            "Do not render any words, letters, numbers, logos, captions, labels, "
            "watermarks, UI text, or pseudo-text. Leave calm negative space for a "
            "professional Chinese typography overlay added later."
        )
    else:
        image_exact_text = image_rendered_text(plan, slide)
        exact_text = " | ".join(image_exact_text) or "no image-rendered text"
        text_constraint = (
            f"Render only this concise text, exactly as written: {exact_text}. "
            "Do not render planning labels, prompt instructions, the deck "
            "objective, transitions, speaker notes, or any other copy."
        )
    if slide["thesis_expression"] == "explicit":
        thesis_context = (
            f"This page intentionally reveals the deck thesis: "
            f"{storyline['core_thesis']}. It may appear visually only within "
            "the page content boundary, and may appear as text only when the "
            "same wording is present in exact_text. "
        )
    else:
        thesis_context = (
            "The deck thesis and decision request are intentionally withheld "
            "on this page. Do not render them as text and do not literally "
            "depict the deferred solution, future-state architecture, promised "
            "outcome, or decision. Use only the page-specific evidence and "
            "permitted non-literal visual subtext. "
        )
    structured_prompt = (
        "Create one complete 16:9 presentation slide image. "
        f"Audience: {plan.get('audience', 'executive audience')}. "
        f"Objective: {plan.get('objective', '')}. "
        f"Slide role: {slide['layout_type']}. "
        f"Narrative role: {slide['narrative_role']}. "
        f"Thesis expression: {slide['thesis_expression']}. "
        f"Content boundary: {slide['content_boundary']}. "
        f"Thesis connection: {slide['thesis_connection']}. "
        f"{thesis_context}"
        f"Audience question: {slide['audience_question']}. "
        f"Message: {slide['message']}. "
        f"Conclusion-led native title copy: {slide['title']}. "
        f"Claim type: {slide['claim_type']}. "
        f"Information topology: {slide['information_topology']}. "
        f"Visual subject: {slide['visual_subject']}. "
        f"Dominant visual focus: {slide['visual_focus']}. "
        f"Visual reasoning: {slide['visual_reasoning']}. "
        f"Visual source: {visual_source}. Source asset references: {source_asset_refs}. "
        f"Layout family: {layout_family}. Approved graphic devices: {graphic_devices}. "
        f"Material form: {material_form}. "
        f"Non-text semantic visual anchor: {semantic_visual_anchor}. The anchor must "
        "be visibly recognizable and carry at least one layer of meaning before "
        "the labels are read; text boxes, thin rules, arrows, or empty containers "
        "alone do not satisfy it. "
        f"Graphic role: {graphic_role}. {graphic_instruction}"
        f"Title render mode: {title_render_mode}. {title_instruction}"
        f"{provenance_instruction}"
        f"Non-visible transition cue for composition only: "
        f"{slide['transition']['to_next']}. "
        f"Verified facts only: {facts}. "
        f"{evidence_instruction}"
        f"Language policy: {language_instruction} "
        f"Exact palette: {palette_description(plan['palette'])}. "
        f"Visual style: {generation.get('style', 'clean executive presentation')}. "
        f"{text_constraint} "
        f"Use a pure solid {plan['palette']['background']} background with no "
        "background photo, texture, pattern, glow, or scenic wallpaper. Allow "
        "restrained nodes, connectors, paths, containers, icons, domain silhouettes, "
        "compact 2D illustrations, and pale color blocks when they improve scanning "
        "or encode relationships. Judge the page as a complete visual composition: "
        "beautiful, simple, immediately understandable, and easy for an executive "
        "speaker to narrate. The title and visual must communicate the main logic "
        "without depending on an unusually skilled speaker; narration should add "
        "context, not supply the missing argument. Use one dominant reading path "
        "and a clear hierarchy. "
        "Do not repeat generic line-icon rows, circular badges, rounded-card grids, "
        "a glowing AI brain or chip, a symmetric hub-and-spoke, fake dashboard chrome, "
        "or arrows without a real relationship. These devices are not absolutely "
        "forbidden; use an individual one only when the content genuinely needs it "
        "and the overall page does not look templated. Use asymmetry only when it "
        "clarifies priority; do not manufacture visual complexity. "
        f"Avoid: {negative}."
    )
    custom_prompt = str(slide.get("prompt", "")).strip()
    if custom_prompt:
        return f"{custom_prompt}\n\nMandatory constraints:\n{structured_prompt}"
    return structured_prompt


def post_json(
    url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int,
    attempts: int = 2,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if attempt == attempts or exc.code < 500:
                raise RuntimeError(f"API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if attempt == attempts:
                raise RuntimeError(f"API connection failed: {exc}") from exc
        time.sleep(attempt)
    raise RuntimeError("API request failed")


def generate_openai(
    config: dict[str, Any],
    prompt: str,
    timeout: int,
) -> bytes:
    api_key = get_provider_secret("openai")
    if not api_key:
        raise RuntimeError(
            "OpenAI key is required in OPENAI_API_KEY or macOS Keychain"
        )
    payload = {
        "model": config.get("model", "gpt-image-2"),
        "prompt": prompt,
        "size": config.get("size", "2048x1152"),
        "quality": config.get("quality", "high"),
        "n": 1,
    }
    response = post_json(OPENAI_ENDPOINT, api_key, payload, timeout)
    try:
        encoded = response["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI image response: {response}") from exc
    return base64.b64decode(encoded)


def generate_minimax(
    config: dict[str, Any],
    prompt: str,
    timeout: int,
) -> bytes:
    api_key = get_provider_secret("minimax")
    if not api_key:
        raise RuntimeError(
            "MiniMax key is required in MINIMAX_API_KEY or macOS Keychain"
        )
    payload = {
        "model": config.get("model", "image-01"),
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "base64",
    }
    region = config.get("region", "global")
    response = post_json(MINIMAX_ENDPOINTS[region], api_key, payload, timeout)
    try:
        encoded = response["data"]["image_base64"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected MiniMax image response: {response}") from exc
    return base64.b64decode(encoded)


def save_as_png(image_bytes: bytes, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required to normalize generated images to PNG"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(image_bytes)) as image:
        image.convert("RGB").save(output_path, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved prompts without calling a provider",
    )
    parser.add_argument(
        "--confirm-paid-call",
        action="store_true",
        help="Required acknowledgement before non-dry-run API calls",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate images that already exist",
    )
    parser.add_argument("--limit", type=int, help="Generate at most N pending images")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    style_audit = audit_plan(plan)

    config = plan["image_generation"]
    provider = config["provider"]
    source_directory = config.get("source_directory")
    pending: list[tuple[dict[str, Any], Path, str]] = []
    for _, _, slide in iter_slides(plan):
        output_value = slide["image"]
        if source_directory:
            output_value = str(Path(source_directory) / f"{slide['id']}.png")
        output_path = resolve_path(output_value, plan_path.parent)
        assert output_path is not None
        if output_path.exists() and not args.overwrite:
            continue
        pending.append((slide, output_path, build_prompt(plan, slide)))

    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1")
        pending = pending[: args.limit]

    print(
        f"Provider={provider} model={config['model']} "
        f"quality={config.get('quality', 'provider-default')} pending={len(pending)}"
    )
    if args.dry_run:
        for slide, output_path, prompt in pending:
            print(f"\n[{slide['id']}] -> {output_path}\n{prompt}")
        return
    if not pending:
        print("No pending images.")
        return
    if not style_audit.get("passed"):
        raise SystemExit(
            "Static style audit failed; fix the plan before a paid image call. "
            "Run scripts/audit_deck_style.py for the findings."
        )
    if not args.confirm_paid_call:
        raise SystemExit(
            "Paid API call blocked. Re-run with --confirm-paid-call after user approval."
        )

    generators = {
        "openai": generate_openai,
        "minimax": generate_minimax,
    }
    generator = generators[provider]
    for index, (slide, output_path, prompt) in enumerate(pending, start=1):
        print(f"Generating {index}/{len(pending)}: {slide['id']}")
        image_bytes = generator(config, prompt, args.timeout)
        save_as_png(image_bytes, output_path)
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
