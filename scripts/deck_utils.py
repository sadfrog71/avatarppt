#!/usr/bin/env python3
"""Shared helpers for the image-avatar-ppt scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator


HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def load_plan(plan_path: Path) -> dict[str, Any]:
    return json.loads(plan_path.read_text(encoding="utf-8"))


def resolve_path(value: str | None, base_dir: Path) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path


def iter_slides(plan: dict[str, Any]) -> Iterator[tuple[int, int, dict[str, Any]]]:
    for section_index, section in enumerate(plan.get("sections", []), start=1):
        for slide_index, slide in enumerate(section.get("slides", []), start=1):
            yield section_index, slide_index, slide


def resolved_title_render_mode(plan: dict[str, Any], slide: dict[str, Any]) -> str:
    explicit = slide.get("title_render_mode")
    if explicit in {"image", "native", "none"}:
        return str(explicit)
    return "native" if isinstance(plan.get("authorship"), dict) else "image"


def image_rendered_text(plan: dict[str, Any], slide: dict[str, Any]) -> list[str]:
    items = [str(item) for item in slide.get("exact_text", [])]
    if resolved_title_render_mode(plan, slide) in {"native", "none"}:
        title = str(slide.get("title", ""))
        items = [item for item in items if item != title]
    return items


def palette_description(palette: dict[str, str]) -> str:
    order = ("primary", "secondary", "accent", "background", "text", "muted")
    return ", ".join(f"{key} {palette[key]}" for key in order if palette.get(key))


def configured_minimum_size(plan: dict[str, Any]) -> tuple[int, int]:
    generation = plan.get("image_generation", {})
    width = generation.get("minimum_width")
    height = generation.get("minimum_height")
    if isinstance(width, int) and isinstance(height, int):
        return width, height

    size = generation.get("size", "")
    match = re.fullmatch(r"(\d+)x(\d+)", str(size))
    if match and generation.get("provider") == "openai":
        return int(match.group(1)), int(match.group(2))
    return 1024, 576


def image_dimensions(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for image dimension checks; install the 'Pillow' package"
        ) from exc

    with Image.open(path) as image:
        return image.size


def validate_image_geometry(
    path: Path,
    minimum: tuple[int, int],
    aspect_tolerance: float = 0.015,
) -> tuple[int, int]:
    width, height = image_dimensions(path)
    expected_ratio = 16 / 9
    actual_ratio = width / height
    if abs(actual_ratio - expected_ratio) / expected_ratio > aspect_tolerance:
        raise ValueError(f"{path} is {width}x{height}, not close enough to 16:9")
    if width < minimum[0] or height < minimum[1]:
        raise ValueError(
            f"{path} is {width}x{height}; minimum is {minimum[0]}x{minimum[1]}"
        )
    return width, height
