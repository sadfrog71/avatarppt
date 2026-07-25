#!/usr/bin/env python3
"""Validate an image-avatar-ppt deck plan before paid API calls."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from deck_utils import HEX_COLOR, iter_slides, load_plan


REQUIRED_PALETTE_KEYS = (
    "primary",
    "secondary",
    "accent",
    "background",
    "text",
)
ALLOWED_PROVIDERS = {"openai", "minimax"}
ALLOWED_MINIMAX_REGIONS = {"cn", "global"}
ALLOWED_LAYOUTS = {
    "opener",
    "overview",
    "metrics",
    "process",
    "system",
    "comparison",
    "roadmap",
    "custom",
}


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not plan.get("output"):
        errors.append("top-level 'output' is required")
    if not plan.get("cover_title"):
        errors.append("top-level 'cover_title' is required")

    palette = plan.get("palette")
    if not isinstance(palette, dict):
        errors.append("top-level 'palette' must be an object")
    else:
        for key in REQUIRED_PALETTE_KEYS:
            value = palette.get(key)
            if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
                errors.append(f"palette.{key} must be a six-digit hex color")
        muted = palette.get("muted")
        if muted is not None and (
            not isinstance(muted, str) or not HEX_COLOR.fullmatch(muted)
        ):
            errors.append("palette.muted must be a six-digit hex color")

    generation = plan.get("image_generation")
    if not isinstance(generation, dict):
        errors.append("top-level 'image_generation' must be an object")
    else:
        provider = generation.get("provider")
        if provider not in ALLOWED_PROVIDERS:
            errors.append("image_generation.provider must be 'openai' or 'minimax'")
        if not generation.get("model"):
            errors.append("image_generation.model is required")
        source_directory = generation.get("source_directory")
        if source_directory is not None and (
            not isinstance(source_directory, str) or not source_directory.strip()
        ):
            errors.append("image_generation.source_directory must be a non-empty path")
        if provider == "openai":
            size = str(generation.get("size", ""))
            if not re.fullmatch(r"\d+x\d+|auto", size):
                errors.append("OpenAI image_generation.size must be WIDTHxHEIGHT or auto")
            if generation.get("quality", "auto") not in {
                "low",
                "medium",
                "high",
                "auto",
            }:
                errors.append(
                    "OpenAI image_generation.quality must be low, medium, high, or auto"
                )
        if provider == "minimax":
            region = generation.get("region", "global")
            if region not in ALLOWED_MINIMAX_REGIONS:
                errors.append(
                    "MiniMax image_generation.region must be 'cn' or 'global'"
                )

    sections = plan.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("top-level 'sections' must be a non-empty array")
        return errors
    if plan.get("include_catalogue", True) and len(sections) > 4:
        errors.append("catalogue-enabled plans support at most four sections")

    vision = plan.get("vision_review", {})
    if vision.get("enabled"):
        if vision.get("provider") != "kimi":
            errors.append("vision_review.provider must be 'kimi' when enabled")
        if not vision.get("model"):
            errors.append("vision_review.model is required when enabled")

    seen_ids: set[str] = set()
    seen_images: set[str] = set()
    for section_index, section in enumerate(sections, start=1):
        prefix = f"sections[{section_index - 1}]"
        if not section.get("main_title"):
            errors.append(f"{prefix}.main_title is required")
        if not section.get("subtitle"):
            errors.append(f"{prefix}.subtitle is required")
        slides = section.get("slides")
        if not isinstance(slides, list) or not slides:
            errors.append(f"{prefix}.slides must be a non-empty array")

    for section_index, slide_index, slide in iter_slides(plan):
        prefix = f"sections[{section_index - 1}].slides[{slide_index - 1}]"
        slide_id = slide.get("id")
        if not isinstance(slide_id, str) or not slide_id.strip():
            errors.append(f"{prefix}.id is required")
        elif slide_id in seen_ids:
            errors.append(f"{prefix}.id duplicates '{slide_id}'")
        else:
            seen_ids.add(slide_id)

        for field in ("title", "message", "visual_subject"):
            if not isinstance(slide.get(field), str) or not slide[field].strip():
                errors.append(f"{prefix}.{field} is required")

        layout = slide.get("layout_type")
        if layout not in ALLOWED_LAYOUTS:
            errors.append(f"{prefix}.layout_type is not supported")

        exact_text = slide.get("exact_text")
        if not isinstance(exact_text, list) or not exact_text:
            errors.append(f"{prefix}.exact_text must be a non-empty array")
        elif any(not isinstance(item, str) or not item.strip() for item in exact_text):
            errors.append(f"{prefix}.exact_text contains an empty/non-string item")

        image = slide.get("image")
        if not isinstance(image, str) or not image.lower().endswith(".png"):
            errors.append(f"{prefix}.image must be a PNG path")
        elif image in seen_images:
            errors.append(f"{prefix}.image duplicates '{image}'")
        else:
            seen_images.add(image)

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    errors = validate_plan(load_plan(plan_path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Valid deck plan: {plan_path}")


if __name__ == "__main__":
    main()
