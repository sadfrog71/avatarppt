#!/usr/bin/env python3
"""Run local geometry checks and optional Kimi Vision QA on slide images."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from audit_deck_style import audit_plan
from credential_store import get_provider_secret
from deck_utils import (
    configured_minimum_size,
    image_rendered_text,
    iter_slides,
    load_plan,
    palette_description,
    resolve_path,
    resolved_title_render_mode,
    validate_image_geometry,
)
from generate_images import post_json
from validate_plan import validate_plan


KIMI_ENDPOINT = "https://api.kimi.com/coding/"


def parse_json_content(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("review response must be a JSON object")
    return parsed


def image_data_url(image_path: Path) -> str:
    media_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def enforce_ai_aesthetic_gate(review: dict[str, Any]) -> dict[str, Any]:
    risk = str(review.get("ai_aesthetic_risk", "")).lower()
    if risk == "high":
        review["pass"] = False
        issues = review.setdefault("issues", [])
        if isinstance(issues, list) and not any(
            "AI aesthetic risk" in str(issue) for issue in issues
        ):
            issues.append("AI aesthetic risk is high")
    return review


def review_with_kimi(
    plan: dict[str, Any],
    slide: dict[str, Any],
    image_path: Path,
    model: str,
    timeout: int,
) -> dict[str, Any]:
    api_key = get_provider_secret("kimi")
    if not api_key:
        raise RuntimeError(
            "Kimi key is required in KIMI_API_KEY, MOONSHOT_API_KEY, or macOS Keychain"
        )

    data_url = image_data_url(image_path)
    visual_source = slide.get("visual_source", "not declared")
    source_asset_refs = slide.get("source_asset_refs", [])
    layout_family = slide.get("layout_family", slide["information_topology"])
    graphic_devices = slide.get("graphic_devices", [])
    title_render_mode = resolved_title_render_mode(plan, slide)
    expected_image_text = image_rendered_text(plan, slide)
    prompt = (
        "Review this generated PowerPoint slide. "
        f"Intended message: {slide['message']}. "
        f"Narrative role: {slide['narrative_role']}. "
        f"Thesis expression: {slide['thesis_expression']}. "
        f"Content boundary: {slide['content_boundary']}. "
        f"Thesis connection: {slide['thesis_connection']}. "
        f"Required information topology: {slide['information_topology']}. "
        f"Visual reasoning: {slide['visual_reasoning']}. "
        f"Required dominant visual focus: {slide['visual_focus']}. "
        f"Declared visual source: {visual_source}. "
        f"Source asset references: {json.dumps(source_asset_refs, ensure_ascii=False)}. "
        f"Layout family: {layout_family}. "
        f"Approved graphic devices: {json.dumps(graphic_devices, ensure_ascii=False)}. "
        f"Title render mode: {title_render_mode}. "
        f"Expected image-rendered text: {json.dumps(expected_image_text, ensure_ascii=False)}. "
        "When title render mode is native, reject a title, title placeholder, or "
        "pseudo-title inside the bitmap; require a clean title zone for editable "
        "PowerPoint text. "
        f"Required palette: {palette_description(plan['palette'])}. "
        "Check text corruption, missing or duplicated labels, overlap, clipping, "
        "small unreadable text, palette mismatch, semantic mismatch, competing "
        "visual focal points, decorative clutter, and a topology that flattens "
        "meaningful relationships into disconnected cards or table rows. The "
        "visible copy must contain only the expected exact text; planning "
        "labels, prompt instructions, deck-level thesis, decision request, "
        "transitions, and speaker notes must not leak into the image. Check "
        "every depicted object against the content boundary. When thesis "
        "expression is implicit, reject any literal solution, target "
        "architecture, future-state workflow, or outcome that the page has not "
        "yet earned. Also review authorship quality. Flag standard AI-default "
        "visual devices when they are not required by the content: repeated "
        "rounded-card grids, circular icon badges, symmetric hub-and-spoke "
        "layouts, glowing AI brains or chips, decorative arrows, generic fake "
        "dashboards, excessive line icons, and polished-but-unspecific technology "
        "scenery. Flag formulaic copy, empty slogans, mechanically balanced "
        "three-part phrases, or a page that looks assembled from a generic SaaS "
        "infographic kit. Do not penalize a clean or symmetric page by itself; "
        "penalize repetition, generic symbolism, or decoration without evidence. "
        "If source assets are declared, confirm that the slide visibly uses or "
        "faithfully represents them instead of replacing them with synthetic "
        "evidence. The "
        "background must be a "
        f"pure solid {plan['palette']['background']} canvas with no gradient, "
        "photo, texture, pattern, glow, or scenic wallpaper. "
        'Return JSON only: {"pass": boolean, "issues": [string], '
        '"observed_text": [string], "palette_match": boolean, '
        '"solid_background": boolean, "focus_clear": boolean, '
        '"topology_match": boolean, "exact_text_exclusive": boolean, '
        '"content_boundary_respected": boolean, '
        '"thesis_leakage_absent": boolean, "ai_aesthetic_risk": '
        '"low|medium|high", "standard_ai_elements": [string], '
        '"copy_cliche_absent": boolean, "source_specificity": '
        '"low|medium|high", "editorial_authorship": boolean}.'
    )
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict visual QA reviewer for presentation slides.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": prompt},
                ],
            },
        ],
    }
    endpoint = plan.get("vision_review", {}).get("endpoint", KIMI_ENDPOINT)
    response = post_json(endpoint, api_key, payload, timeout)
    try:
        content = response["choices"][0]["message"]["content"]
        return enforce_ai_aesthetic_gate(parse_json_content(content))
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unexpected Kimi review response: {response}") from exc


def review_deck_style_with_kimi(
    plan: dict[str, Any],
    contact_sheet_path: Path,
    model: str,
    timeout: int,
) -> dict[str, Any]:
    api_key = get_provider_secret("kimi")
    if not api_key:
        raise RuntimeError(
            "Kimi key is required in KIMI_API_KEY, MOONSHOT_API_KEY, or macOS Keychain"
        )

    slides = [slide for _, _, slide in iter_slides(plan)]
    slide_contract = [
        {
            "id": slide.get("id"),
            "title": slide.get("title"),
            "layout_family": slide.get(
                "layout_family", slide.get("information_topology")
            ),
            "visual_source": slide.get("visual_source", "not declared"),
            "title_render_mode": resolved_title_render_mode(plan, slide),
        }
        for slide in slides
    ]
    prompt = (
        "Review this ordered contact sheet as one executive presentation, not as "
        "isolated slides. Determine whether the deck shows deliberate editorial "
        "authorship or a repeated AI-generated infographic system. Inspect repeated "
        "rounded cards, circular badges, central hubs, generic line icons, decorative "
        "arrows, fake dashboards, identical title-plus-diagram-plus-summary-bar "
        "structures, excessive symmetry, and synthetic technology scenery. Inspect "
        "copy rhythm for repeated formulas such as not-X-but-Y, from-X-to-Y, and "
        "first-X-then-Y. Check whether evidence, plain typographic pages, tables, "
        "charts, screenshots, and diagrams create an intentional rhythm. Do not fail "
        "a deck merely for consistent branding; fail it when consistency erases "
        "editorial selection or when generic visual devices substitute for content. "
        f"Slide contract: {json.dumps(slide_contract, ensure_ascii=False)}. "
        'Return JSON only: {"pass": boolean, "issues": [string], '
        '"ai_aesthetic_risk": "low|medium|high", '
        '"repeated_layouts": [string], "formulaic_copy": [string], '
        '"generic_visual_devices": [string], '
        '"material_specificity": "low|medium|high", '
        '"editorial_rhythm": boolean, "recommended_changes": [string]}.'
    )
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict editorial director reviewing an executive presentation.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url(contact_sheet_path)},
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
    }
    endpoint = plan.get("vision_review", {}).get("endpoint", KIMI_ENDPOINT)
    response = post_json(endpoint, api_key, payload, timeout)
    try:
        content = response["choices"][0]["message"]["content"]
        return enforce_ai_aesthetic_gate(parse_json_content(content))
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unexpected Kimi deck review response: {response}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument(
        "--reviewer",
        choices=("local", "kimi"),
        default="local",
        help="Run local checks only or add Kimi Vision review",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--confirm-paid-call",
        action="store_true",
        help="Required acknowledgement before Kimi API calls",
    )
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--limit", type=int, help="Review at most N pending slides")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse passing results already present in the QA report",
    )
    parser.add_argument(
        "--deck-style",
        action="store_true",
        help="Add one paid Kimi review of the ordered contact sheet",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))

    vision_config = plan.get("vision_review", {})
    if args.deck_style and args.reviewer != "kimi":
        raise SystemExit("--deck-style requires --reviewer kimi")
    deck_style_requested = args.reviewer == "kimi" and (
        args.deck_style or bool(vision_config.get("deck_style_review"))
    )
    output_path = resolve_path(
        vision_config.get("output", "outputs/image-qa.json"),
        plan_path.parent,
    )
    assert output_path is not None
    style_audit = audit_plan(plan)
    if (
        args.reviewer == "kimi"
        and not args.dry_run
        and not style_audit.get("passed")
    ):
        raise SystemExit(
            "Static style audit failed; fix the plan before paid Kimi QA. "
            "Run scripts/audit_deck_style.py for the findings."
        )
    if args.reviewer == "kimi" and not args.confirm_paid_call and not args.dry_run:
        raise SystemExit(
            "Paid Kimi call blocked. Re-run with --confirm-paid-call after user approval."
        )

    contact_sheet_path = resolve_path(
        vision_config.get("contact_sheet", "contact-sheet.png"),
        plan_path.parent,
    )
    assert contact_sheet_path is not None

    minimum = configured_minimum_size(plan)
    existing_results: dict[str, dict[str, Any]] = {}
    if args.resume and output_path.exists():
        existing_report = json.loads(output_path.read_text(encoding="utf-8"))
        if existing_report.get("reviewer") == args.reviewer:
            existing_results = {
                item["id"]: item
                for item in existing_report.get("slides", [])
                if item.get("id")
                and item.get("local_pass")
                and (
                    args.reviewer == "local"
                    or bool((item.get("review") or {}).get("pass"))
                )
            }

    slides = [slide for _, _, slide in iter_slides(plan)]
    pending_slides = [
        slide for slide in slides if slide["id"] not in existing_results
    ]
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1")
        pending_slides = pending_slides[: args.limit]

    results: list[dict[str, Any]] = []
    for slide in pending_slides:
        image_path = resolve_path(slide["image"], plan_path.parent)
        assert image_path is not None
        result: dict[str, Any] = {
            "id": slide["id"],
            "image": str(image_path),
            "local_pass": False,
            "review": None,
        }
        try:
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            width, height = validate_image_geometry(image_path, minimum)
            result["dimensions"] = {"width": width, "height": height}
            result["local_pass"] = True
            if args.reviewer == "kimi":
                if args.dry_run:
                    result["review"] = {"pending": True, "model": vision_config.get("model", "kimi-k3")}
                else:
                    result["review"] = review_with_kimi(
                        plan,
                        slide,
                        image_path,
                        vision_config.get("model", "kimi-k3"),
                        args.timeout,
                    )
        except Exception as exc:
            result["error"] = str(exc)
        results.append(result)

    combined = dict(existing_results)
    combined.update({item["id"]: item for item in results})
    ordered_results = [
        combined[slide["id"]] for slide in slides if slide["id"] in combined
    ]
    deck_review: dict[str, Any] | None = None
    if deck_style_requested:
        if args.dry_run:
            deck_review = {
                "pending": True,
                "model": vision_config.get("model", "kimi-k3"),
                "contact_sheet": str(contact_sheet_path),
            }
        elif not contact_sheet_path.exists():
            deck_review = {
                "pass": False,
                "issues": [f"contact sheet not found: {contact_sheet_path}"],
                "ai_aesthetic_risk": "unknown",
            }
        else:
            deck_review = review_deck_style_with_kimi(
                plan,
                contact_sheet_path,
                vision_config.get("model", "kimi-k3"),
                args.timeout,
            )
    passed = all(
        item["local_pass"]
        and (
            args.reviewer == "local"
            or args.dry_run
            or bool((item.get("review") or {}).get("pass"))
        )
        for item in ordered_results
    ) and bool(style_audit.get("passed"))
    if deck_style_requested and not args.dry_run:
        passed = passed and bool((deck_review or {}).get("pass"))
    report = {
        "plan": str(plan_path),
        "reviewer": args.reviewer,
        "passed": passed,
        "style_audit": style_audit,
        "deck_review": deck_review,
        "slides": ordered_results,
    }
    if args.dry_run:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}; passed={passed}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
