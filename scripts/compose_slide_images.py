#!/usr/bin/env python3
"""Compose exact plan text over generated visual backgrounds."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from deck_utils import (
    image_rendered_text,
    iter_slides,
    load_plan,
    prefer_editable_text,
    resolve_path,
    resolved_title_render_mode,
    typography_policy,
)
from validate_plan import validate_plan


CANVAS = (1280, 720)
POINT_TO_PIXEL = 96 / 72


def pt_to_px(value: float) -> int:
    return math.ceil(value * POINT_TO_PIXEL)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def find_font(bold: bool) -> str:
    candidates = (
        [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("No suitable Chinese font found")


def fit_cover(image: Any, size: tuple[int, int]) -> Any:
    from PIL import Image

    source_ratio = image.width / image.height
    target_ratio = size[0] / size[1]
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    else:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize(size, Image.Resampling.LANCZOS)


def wrap_text(draw: Any, text: str, font: Any, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def item_weight(text: str) -> float:
    ascii_count = sum(1 for char in text if ord(char) < 128)
    return max(1.0, len(text) - ascii_count * 0.35)


def split_balanced(items: list[str], columns: int) -> list[list[str]]:
    if columns == 1:
        return [items]
    total = sum(item_weight(item) for item in items)
    target = total / columns
    groups: list[list[str]] = [[]]
    running = 0.0
    for item in items:
        weight = item_weight(item)
        remaining_groups = columns - len(groups)
        remaining_items = len(items) - sum(len(group) for group in groups)
        if (
            len(groups) < columns
            and groups[-1]
            and running + weight > target
            and remaining_items > remaining_groups
        ):
            groups.append([])
            running = 0.0
        groups[-1].append(item)
        running += weight
    while len(groups) < columns:
        groups.append([])
    if columns == 2 and groups[0] and groups[1] and is_heading(groups[0][-1]):
        groups[1].insert(0, groups[0].pop())
    return groups


def is_heading(text: str) -> bool:
    return (
        len(text) <= 13
        or text.endswith("：")
        or ("｜" in text and len(text) <= 24)
        or text.startswith(("阶段", "核心", "目标", "结论", "关键"))
    )


def fit_body_font(
    draw: Any,
    groups: list[list[str]],
    font_path: str,
    column_width: int,
    available_height: int,
    minimum_size: int,
    preferred_size: int,
) -> int:
    for size in range(max(25, preferred_size), minimum_size - 1, -1):
        font = __import__("PIL.ImageFont", fromlist=["ImageFont"]).truetype(
            font_path, size
        )
        line_height = math.ceil(size * 1.42)
        group_heights = []
        for group in groups:
            height = 0
            for item in group:
                lines = wrap_text(draw, item, font, column_width - 48)
                height += len(lines) * line_height + 15
            group_heights.append(height)
        if max(group_heights, default=0) <= available_height:
            return size
    raise ValueError(
        f"visible copy does not fit at the required minimum body size of "
        f"{minimum_size}px; split the slide or shorten the copy"
    )


def compose_slide(
    plan: dict[str, Any],
    slide: dict[str, Any],
    source_path: Path,
    output_path: Path,
) -> None:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

    generation = plan.get("image_generation", {})
    typography = typography_policy(plan)
    composition_mode = generation.get("composition_mode", "overlay_panels")
    designed_canvas = composition_mode == "designed_canvas"
    palette = plan["palette"]
    background = hex_rgb(palette["background"])
    primary = hex_rgb(palette["primary"])
    secondary = hex_rgb(palette["secondary"])
    accent = hex_rgb(palette["accent"])
    text_color = hex_rgb(palette["text"])
    muted = hex_rgb(palette.get("muted", "#687D8D"))

    with Image.open(source_path) as source:
        visual = fit_cover(source.convert("RGB"), CANVAS)

    visual_saturation = float(
        generation.get("visual_saturation", 0.92 if designed_canvas else 0.72)
    )
    visual_blur = float(generation.get("visual_blur", 0.45 if designed_canvas else 2.2))
    visual_opacity = float(generation.get("visual_opacity", 0.82 if designed_canvas else 0.18))
    panel_alpha = int(generation.get("panel_alpha", 226 if designed_canvas else 250))
    header_alpha = int(generation.get("header_alpha", 242 if designed_canvas else 255))
    visual = ImageEnhance.Color(visual).enhance(visual_saturation)
    if visual_blur > 0:
        visual = visual.filter(ImageFilter.GaussianBlur(radius=visual_blur))
    base = Image.new("RGB", CANVAS, background)
    base = Image.blend(base, visual, max(0.0, min(1.0, visual_opacity))).convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")

    title_render_mode = resolved_title_render_mode(plan, slide)
    rendered_text = image_rendered_text(plan, slide)

    if title_render_mode != "none":
        draw.rectangle((29, 0, CANVAS[0], 144), fill=(255, 255, 255, header_alpha))
    draw.rectangle((0, 0, 18, CANVAS[1]), fill=(*primary, 255))
    draw.rectangle((18, 0, 29, CANVAS[1]), fill=(*accent, 255))
    if title_render_mode != "none":
        draw.rectangle((48, 36, 1232, 126), fill=(255, 255, 255, header_alpha))

    title_font_path = find_font(True)
    body_font_path = find_font(False)
    bold_font_path = find_font(True)
    items = list(rendered_text)
    if title_render_mode == "image":
        declared_title = str(slide.get("title", ""))
        title = declared_title if declared_title in items else (items[0] if items else "")
        if title:
            items.remove(title)
            draw.rectangle((48, 126, 214, 132), fill=(*accent, 255))
            title_size = pt_to_px(typography["title_font_size_pt"])
            title_font = ImageFont.truetype(title_font_path, title_size)
            minimum_title_size = pt_to_px(typography["body_font_size_pt"])
            while (
                draw.textlength(title, font=title_font) > 1134
                and title_size > minimum_title_size
            ):
                title_size -= 1
                title_font = ImageFont.truetype(title_font_path, title_size)
            draw.text((66, 58), title, font=title_font, fill=(*secondary, 255))

    columns = 1 if len(items) <= 6 else 2
    left, top, right, bottom = (
        48,
        154 if title_render_mode != "none" else 48,
        1232,
        674,
    )
    if designed_canvas and columns == 1:
        anchor = str(generation.get("single_column_anchor", "left"))
        width = int(generation.get("single_column_width", 720))
        if anchor == "right":
            left = CANVAS[0] - 48 - width
            right = CANVAS[0] - 48
        else:
            right = left + width
    gutter = 24
    column_width = (right - left - gutter * (columns - 1)) // columns
    groups = split_balanced(items, columns)
    body_size = fit_body_font(
        draw,
        groups,
        body_font_path,
        column_width,
        bottom - top - 32,
        pt_to_px(typography["body_font_size_pt"]),
        pt_to_px(typography["body_font_size_pt"]),
    )
    body_font = ImageFont.truetype(body_font_path, body_size)
    bold_font = ImageFont.truetype(bold_font_path, body_size)
    line_height = math.ceil(body_size * 1.42)

    for column_index, group in enumerate(groups):
        x0 = left + column_index * (column_width + gutter)
        x1 = x0 + column_width
        draw.rounded_rectangle(
            (x0, top, x1, bottom),
            radius=8,
            fill=(255, 255, 255, panel_alpha),
            outline=(*primary, 72 if designed_canvas else 45),
            width=1,
        )
        y = top + 20
        for item in group:
            heading = is_heading(item)
            font = bold_font if heading else body_font
            color = secondary if heading else text_color
            marker = accent if heading else primary
            lines = wrap_text(draw, item, font, column_width - 56)
            draw.rounded_rectangle(
                (x0 + 20, y + body_size * 0.36, x0 + 29, y + body_size * 0.72),
                radius=3,
                fill=(*marker, 255),
            )
            for line_index, line in enumerate(lines):
                draw.text(
                    (x0 + 40, y + line_index * line_height),
                    line,
                    font=font,
                    fill=(*color, 255),
                )
            y += len(lines) * line_height + 15
            if y < bottom - 12:
                draw.line(
                    (x0 + 40, y - 7, x1 - 20, y - 7),
                    fill=(*muted, 28),
                    width=1,
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output_path, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument("--limit", type=int, help="Compose at most N slides")
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    if prefer_editable_text(plan):
        raise SystemExit(
            "typography.prefer_editable_text=true: do not rasterize copy with "
            "compose_slide_images.py; keep the generated visual text-free and let "
            "assemble_deck.py add slide.editable_text as native PowerPoint text"
        )
    generation = plan["image_generation"]
    source_directory = generation.get("source_directory")
    if not source_directory:
        raise SystemExit("image_generation.source_directory is required")

    slides = [slide for _, _, slide in iter_slides(plan)]
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1")
        slides = slides[: args.limit]

    for slide in slides:
        source_path = resolve_path(
            str(Path(source_directory) / f"{slide['id']}.png"),
            plan_path.parent,
        )
        output_path = resolve_path(slide["image"], plan_path.parent)
        assert source_path is not None and output_path is not None
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        compose_slide(plan, slide, source_path, output_path)
        print(f"Composed {slide['id']} -> {output_path}")


if __name__ == "__main__":
    main()
