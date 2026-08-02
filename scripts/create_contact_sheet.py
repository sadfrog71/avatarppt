#!/usr/bin/env python3
"""Create an ordered contact sheet for deck-level visual review."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from deck_utils import iter_slides, load_plan, resolve_path
from validate_plan import validate_plan


def load_label_font(size: int) -> Any:
    from PIL import ImageFont

    candidates = (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def create_contact_sheet(
    plan_path: Path,
    output_path: Path,
    columns: int,
    thumb_width: int,
) -> None:
    from PIL import Image, ImageDraw, ImageOps

    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise ValueError("\n".join(f"ERROR: {error}" for error in errors))

    slides = [slide for _, _, slide in iter_slides(plan)]
    if not slides:
        raise ValueError("deck plan contains no content slides")

    thumb_height = round(thumb_width * 9 / 16)
    label_height = max(36, round(thumb_width * 0.085))
    gap = max(16, round(thumb_width * 0.04))
    margin = gap
    rows = math.ceil(len(slides) / columns)
    cell_width = thumb_width
    cell_height = thumb_height + label_height
    sheet_width = margin * 2 + columns * cell_width + (columns - 1) * gap
    sheet_height = margin * 2 + rows * cell_height + (rows - 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#EEF1F4")
    draw = ImageDraw.Draw(sheet)
    font = load_label_font(max(15, round(label_height * 0.38)))

    for index, slide in enumerate(slides):
        image_path = resolve_path(slide["image"], plan_path.parent)
        assert image_path is not None
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        row, column = divmod(index, columns)
        x = margin + column * (cell_width + gap)
        y = margin + row * (cell_height + gap)
        with Image.open(image_path) as source:
            thumb = ImageOps.fit(
                source.convert("RGB"),
                (thumb_width, thumb_height),
                method=Image.Resampling.LANCZOS,
            )
        sheet.paste(thumb, (x, y))
        draw.rectangle(
            (x, y + thumb_height, x + thumb_width, y + cell_height),
            fill="#FFFFFF",
        )
        label = f"{index + 1:02d}  {slide['id']}  {slide['title']}"
        try:
            draw.text(
                (x + 12, y + thumb_height + label_height * 0.22),
                label,
                font=font,
                fill="#1F2937",
            )
        except UnicodeEncodeError:
            draw.text(
                (x + 12, y + thumb_height + label_height * 0.22),
                f"{index + 1:02d}  {slide['id']}",
                font=font,
                fill="#1F2937",
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument(
        "--output",
        default="outputs/contact-sheet.png",
        help="Output PNG path, resolved relative to the plan",
    )
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--thumb-width", type=int, default=480)
    args = parser.parse_args()

    if args.columns < 1:
        raise SystemExit("--columns must be at least 1")
    if args.thumb_width < 320:
        raise SystemExit("--thumb-width must be at least 320")

    plan_path = Path(args.plan).resolve()
    output_path = resolve_path(args.output, plan_path.parent)
    assert output_path is not None
    create_contact_sheet(plan_path, output_path, args.columns, args.thumb_width)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
