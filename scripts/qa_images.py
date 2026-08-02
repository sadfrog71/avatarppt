#!/usr/bin/env python3
"""Run local geometry checks and optional Kimi Vision QA on slide images."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from credential_store import get_provider_secret
from deck_utils import (
    configured_minimum_size,
    iter_slides,
    load_plan,
    palette_description,
    resolve_path,
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

    media_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    data_url = f"data:{media_type};base64,{encoded}"
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
        f"Expected exact text: {json.dumps(slide['exact_text'], ensure_ascii=False)}. "
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
        "yet earned. The "
        "background must be a "
        f"pure solid {plan['palette']['background']} canvas with no gradient, "
        "photo, texture, pattern, glow, or scenic wallpaper. "
        'Return JSON only: {"pass": boolean, "issues": [string], '
        '"observed_text": [string], "palette_match": boolean, '
        '"solid_background": boolean, "focus_clear": boolean, '
        '"topology_match": boolean, "exact_text_exclusive": boolean, '
        '"content_boundary_respected": boolean, '
        '"thesis_leakage_absent": boolean}.'
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
        return parse_json_content(content)
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unexpected Kimi review response: {response}") from exc


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
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))

    vision_config = plan.get("vision_review", {})
    output_path = resolve_path(
        vision_config.get("output", "outputs/image-qa.json"),
        plan_path.parent,
    )
    assert output_path is not None
    if args.reviewer == "kimi" and not args.confirm_paid_call and not args.dry_run:
        raise SystemExit(
            "Paid Kimi call blocked. Re-run with --confirm-paid-call after user approval."
        )

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
    passed = all(
        item["local_pass"]
        and (
            args.reviewer == "local"
            or args.dry_run
            or bool((item.get("review") or {}).get("pass"))
        )
        for item in ordered_results
    )
    report = {
        "plan": str(plan_path),
        "reviewer": args.reviewer,
        "passed": passed,
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
