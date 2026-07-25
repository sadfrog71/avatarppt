#!/usr/bin/env python3
"""Compose high-visual UI-style slide PNGs over GPT Image canvases."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

from deck_utils import iter_slides, load_plan, resolve_path
from validate_plan import validate_plan


CANVAS = (1280, 720)
DEFAULT_OUTPUT_SIZE = (1920, 1080)


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


def parse_size(value: Any, fallback: tuple[int, int]) -> tuple[int, int]:
    if not isinstance(value, str) or "x" not in value:
        return fallback
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except ValueError:
        return fallback
    if width <= 0 or height <= 0:
        return fallback
    if abs((width / height) - (16 / 9)) > 0.02:
        return fallback
    return width, height


def text_width(draw: Any, text: str, font: Any) -> int:
    return math.ceil(draw.textlength(text, font=font))


def wrap_text(draw: Any, text: str, font: Any, max_width: int) -> list[str]:
    tokens = re.findall(r"[\u4e00-\u9fff]|[^\u4e00-\u9fff\s]+|\s+", text)
    if not tokens:
        tokens = list(text)
    lines: list[str] = []
    current = ""
    for token in tokens:
        candidate = current + token
        if current and text_width(draw, candidate, font) > max_width:
            lines.append(current.strip())
            current = token
        else:
            current = candidate
    if current.strip():
        lines.append(current.strip())
    return lines or [""]


class UIComposer:
    def __init__(self, plan: dict[str, Any], slide: dict[str, Any], source_path: Path):
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

        self.Image = Image
        self.ImageDraw = ImageDraw
        self.ImageEnhance = ImageEnhance
        self.ImageFilter = ImageFilter
        self.ImageFont = ImageFont
        self.plan = plan
        self.slide = slide
        self.display = slide.get("designer", {})
        self.generation = plan.get("image_generation", {})
        self.palette = plan["palette"]
        self.primary = hex_rgb(self.palette["primary"])
        self.secondary = hex_rgb(self.palette["secondary"])
        self.accent = hex_rgb(self.palette["accent"])
        self.background = hex_rgb(self.palette["background"])
        self.text = hex_rgb(self.palette["text"])
        self.muted = hex_rgb(self.palette.get("muted", "#687D8D"))
        self.font_regular = find_font(False)
        self.font_bold = find_font(True)

        with Image.open(source_path) as source:
            visual = fit_cover(source.convert("RGB"), CANVAS)
        visual = ImageEnhance.Color(visual).enhance(float(self.generation.get("visual_saturation", 1.04)))
        visual = ImageEnhance.Contrast(visual).enhance(float(self.generation.get("visual_contrast", 1.02)))
        base = Image.new("RGB", CANVAS, self.background)
        base = Image.blend(
            base,
            visual,
            max(0.0, min(1.0, float(self.generation.get("visual_opacity", 0.96)))),
        ).convert("RGBA")
        self.base = base
        self.draw = ImageDraw.Draw(self.base, "RGBA")
        self.draw_header()

    def font(self, size: int, bold: bool = False) -> Any:
        return self.ImageFont.truetype(self.font_bold if bold else self.font_regular, size)

    def rounded(self, box: tuple[int, int, int, int], radius: int, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int] | None = None, width: int = 1) -> None:
        self.draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def card(self, box: tuple[int, int, int, int], alpha: int = 92, radius: int = 16) -> None:
        x0, y0, x1, y1 = box
        actual_alpha = int(self.generation.get("panel_alpha", alpha))
        self.draw.rounded_rectangle((x0 + 2, y0 + 6, x1 + 2, y1 + 6), radius=radius, fill=(0, 44, 90, 14))
        self.rounded(box, radius, (255, 255, 255, actual_alpha), (*self.primary, 58), 1)

    def draw_text_box(self, text: str, xy: tuple[int, int], width: int, size: int, *, bold: bool = False, fill: tuple[int, int, int] | None = None, line_gap: float = 1.28, max_lines: int | None = None) -> int:
        font = self.font(size, bold)
        lines = wrap_text(self.draw, text, font, width)
        if max_lines is not None:
            lines = lines[:max_lines]
        x, y = xy
        for line in lines:
            self.draw.text((x, y), line, font=font, fill=(*(fill or self.text), 255))
            y += math.ceil(size * line_gap)
        return y

    def draw_readability_veil(self, box: tuple[int, int, int, int], alpha: int = 42) -> None:
        self.rounded(box, 18, (255, 255, 255, alpha), (255, 255, 255, 64), 1)

    def draw_header(self) -> None:
        title = self.display.get("title") or self.slide.get("title") or self.slide["exact_text"][0]
        statement = self.display.get("statement") or self.slide.get("message", "")
        header_alpha = int(self.generation.get("header_alpha", 118))
        self.draw.rectangle((0, 0, CANVAS[0], 114), fill=(255, 255, 255, header_alpha))
        self.draw.rectangle((0, 0, 10, CANVAS[1]), fill=(*self.primary, 255))
        self.draw.rectangle((10, 0, 16, CANVAS[1]), fill=(*self.accent, 255))
        self.draw.rounded_rectangle((48, 34, 180, 40), radius=3, fill=(*self.accent, 255))
        self.draw_text_box(title, (48, 48), 850, 32, bold=True, fill=self.secondary, max_lines=1)
        if statement:
            self.draw_text_box(statement, (48, 86), 980, 15, fill=self.muted, max_lines=1)

    def chip(self, text: str, box: tuple[int, int, int, int], *, fill: tuple[int, int, int] | None = None, dark: bool = False) -> None:
        color = fill or self.primary
        bg = (*color, 232 if dark else 28)
        fg = (255, 255, 255) if dark else self.secondary
        self.rounded(box, 999, bg, (*color, 140), 1)
        font = self.font(17, True)
        x0, y0, x1, y1 = box
        tw = text_width(self.draw, text, font)
        self.draw.text((x0 + max(14, (x1 - x0 - tw) // 2), y0 + (y1 - y0 - 20) // 2), text, font=font, fill=(*fg, 255))

    def kpi(self, value: str, label: str, box: tuple[int, int, int, int], *, accent: bool = False) -> None:
        x0, y0, x1, y1 = box
        self.card(box, alpha=190, radius=18)
        color = self.accent if accent else self.primary
        self.draw.rounded_rectangle((x0, y0, x0 + 8, y1), radius=4, fill=(*color, 255))
        self.draw_text_box(value, (x0 + 24, y0 + 22), x1 - x0 - 42, 34, bold=True, fill=color, max_lines=1)
        self.draw_text_box(label, (x0 + 26, y0 + 64), x1 - x0 - 50, 15, fill=self.muted, max_lines=2)

    def render_opener(self) -> None:
        metrics = self.display.get("metrics", [])
        chips = self.display.get("chips", [])
        self.draw_readability_veil((58, 168, 474, 454), 58)
        self.draw_text_box(self.display.get("hero", self.display.get("statement", "")), (84, 204), 354, 24, bold=True, fill=self.secondary, max_lines=5)
        y = 356
        for chip in chips[:4]:
            self.chip(chip, (86, y, 268, y + 31), fill=self.accent if y == 356 else self.primary)
            y += 46
        x = 540
        for index, item in enumerate(metrics[:3]):
            self.kpi(item["value"], item["label"], (x + index * 218, 530, x + index * 218 + 190, 632), accent=index == 0)

    def render_comparison(self) -> None:
        left = self.display.get("left", {})
        right = self.display.get("right", {})
        center = self.display.get("center", [])
        boxes = [(62, 196, 392, 526), (888, 196, 1218, 526)]
        for box, data, color in ((boxes[0], left, self.primary), (boxes[1], right, self.accent)):
            self.card(box, alpha=92, radius=20)
            x0, y0, x1, _ = box
            self.draw_text_box(data.get("title", ""), (x0 + 24, y0 + 28), 270, 22, bold=True, fill=color, max_lines=1)
            self.draw_text_box(data.get("subtitle", ""), (x0 + 24, y0 + 62), 266, 14, fill=self.muted, max_lines=1)
            y = y0 + 112
            for item in data.get("items", [])[:4]:
                self.draw.ellipse((x0 + 28, y + 8, x0 + 38, y + 18), fill=(*color, 255))
                self.draw_text_box(item, (x0 + 52, y), x1 - x0 - 72, 16, bold=False, fill=self.text, max_lines=1)
                y += 42
        self.draw.line((624, 190, 656, 546), fill=(*self.secondary, 70), width=2)
        y = 270
        for item in center[:3]:
            self.chip(item, (552, y, 728, y + 38), fill=self.secondary, dark=True)
            y += 64

    def render_overview(self) -> None:
        nodes = self.display.get("nodes", [])
        pillars = self.display.get("pillars", [])
        center = (640, 358)
        self.draw.ellipse((520, 238, 760, 478), fill=(*self.primary, 30), outline=(*self.primary, 120), width=2)
        self.draw_text_box(self.display.get("center", "核心判断"), (568, 322), 150, 31, bold=True, fill=self.secondary, max_lines=2)
        positions = [(86, 168), (328, 166), (878, 166), (1038, 326), (198, 438)]
        for index, node in enumerate(nodes[:5]):
            x, y = positions[index]
            self.card((x, y, x + 230, y + 96), alpha=104, radius=18)
            self.draw.line((x + 230, y + 48, center[0], center[1]), fill=(*self.accent, 90), width=2)
            self.draw_text_box(node, (x + 22, y + 29), 180, 20, bold=True, fill=self.secondary, max_lines=1)
        x = 290
        for index, item in enumerate(pillars[:3]):
            self.chip(item, (x + index * 235, 590, x + index * 235 + 196, 632), fill=self.accent if index == 1 else self.primary, dark=index == 1)

    def render_metrics(self) -> None:
        metrics = self.display.get("metrics", [])
        cols = 3 if len(metrics) <= 6 else 4
        start_x = 70
        start_y = 162
        w = 360 if cols == 3 else 270
        h = 128
        gap_x = 38 if cols == 3 else 24
        gap_y = 30
        for index, item in enumerate(metrics):
            row = index // cols
            col = index % cols
            x = start_x + col * (w + gap_x)
            y = start_y + row * (h + gap_y)
            self.kpi(item["value"], item["label"], (x, y, x + w, y + h), accent=index in (0, 2))
        note = self.display.get("note")
        if note:
            self.chip(note, (330, 620, 950, 660), fill=self.secondary, dark=True)

    def render_system(self) -> None:
        layers = self.display.get("layers", [])
        metrics = self.display.get("metrics", [])
        self.draw.ellipse((505, 186, 775, 456), fill=(*self.primary, 34), outline=(*self.primary, 130), width=2)
        self.draw_text_box(self.display.get("center", "AI中枢"), (570, 300), 160, 33, bold=True, fill=self.secondary, max_lines=2)
        if layers:
            x = 80
            for index, layer in enumerate(layers[:4]):
                y = 162 + index * 112
                self.card((x, y, 468, y + 84), alpha=104, radius=16)
                self.draw_text_box(layer.get("title", ""), (x + 24, y + 18), 170, 22, bold=True, fill=self.primary if index != 3 else self.accent, max_lines=1)
                self.draw_text_box(layer.get("desc", ""), (x + 198, y + 20), 230, 16, fill=self.muted, max_lines=2)
                self.draw.line((468, y + 42, 505, 321), fill=(*self.accent, 80), width=2)
        x = 820
        for index, item in enumerate(self.display.get("nodes", [])[:6]):
            y = 164 + index * 68
            self.chip(item, (x, y, x + 340, y + 38), fill=self.primary if index % 2 == 0 else self.accent)
        for index, item in enumerate(metrics[:3]):
            self.kpi(item["value"], item["label"], (780 + index * 150, 574, 916 + index * 150, 662), accent=index == 0)

    def render_process(self) -> None:
        steps = self.display.get("steps", [])
        count = min(len(steps), 6)
        start_x = 78
        gap = (1120 - 128) // max(count - 1, 1)
        y = 244
        for index, step in enumerate(steps[:count]):
            x = start_x + index * gap
            color = self.accent if index == count - 1 else self.primary
            if index < count - 1:
                self.draw.line((x + 64, y, x + gap - 20, y), fill=(*self.primary, 118), width=4)
            self.draw.ellipse((x, y - 48, x + 96, y + 48), fill=(*color, 228), outline=(255, 255, 255, 210), width=3)
            self.draw_text_box(str(index + 1), (x + 35, y - 21), 50, 30, bold=True, fill=(255, 255, 255), max_lines=1)
            self.card((x - 22, y + 76, x + 150, y + 220), alpha=108, radius=16)
            self.draw_text_box(step.get("title", ""), (x - 4, y + 98), 136, 18, bold=True, fill=self.secondary, max_lines=2)
            self.draw_text_box(step.get("desc", ""), (x - 4, y + 150), 136, 15, fill=self.muted, max_lines=3)
        for index, item in enumerate(self.display.get("metrics", [])[:3]):
            self.kpi(item["value"], item["label"], (82 + index * 380, 555, 410 + index * 380, 656), accent=index == 0)

    def render_roadmap(self) -> None:
        stages = self.display.get("stages", [])
        for index, stage in enumerate(stages[:3]):
            x = 92 + index * 390
            y = 178
            self.card((x, y, x + 318, y + 376), alpha=108, radius=24)
            self.draw.ellipse((x + 98, y - 42, x + 220, y + 80), fill=(*(self.accent if index == 1 else self.primary), 236), outline=(255, 255, 255, 220), width=4)
            self.draw_text_box(str(index + 1), (x + 140, y - 15), 60, 36, bold=True, fill=(255, 255, 255), max_lines=1)
            self.draw_text_box(stage.get("title", ""), (x + 34, y + 88), 248, 24, bold=True, fill=self.secondary, max_lines=1)
            self.draw_text_box(stage.get("target", ""), (x + 34, y + 130), 248, 19, fill=self.primary, max_lines=2)
            self.draw_text_box(stage.get("method", ""), (x + 34, y + 204), 248, 17, fill=self.text, max_lines=2)
            self.chip(stage.get("rhythm", ""), (x + 34, y + 304, x + 250, y + 342), fill=self.accent if index == 1 else self.primary)

    def render(self) -> Any:
        layout = self.display.get("layout", self.slide.get("layout_type", "opener"))
        if layout == "comparison":
            self.render_comparison()
        elif layout == "overview":
            self.render_overview()
        elif layout == "metrics":
            self.render_metrics()
        elif layout == "system":
            self.render_system()
        elif layout == "process":
            self.render_process()
        elif layout == "roadmap":
            self.render_roadmap()
        else:
            self.render_opener()
        output_size = parse_size(
            self.generation.get("composition_size") or self.generation.get("output_size"),
            DEFAULT_OUTPUT_SIZE,
        )
        if output_size != CANVAS:
            return self.base.resize(output_size, self.Image.Resampling.LANCZOS)
        return self.base


def compose_slide(plan: dict[str, Any], slide: dict[str, Any], source_path: Path, output_path: Path) -> None:
    composer = UIComposer(plan, slide, source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    composer.render().convert("RGB").save(output_path, "PNG", optimize=True)


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
    generation = plan["image_generation"]
    source_directory = generation.get("source_directory")
    if not source_directory:
        raise SystemExit("image_generation.source_directory is required")

    slides = [slide for _, _, slide in iter_slides(plan)]
    if args.limit is not None:
        slides = slides[: args.limit]

    for slide in slides:
        source_path = resolve_path(str(Path(source_directory) / f"{slide['id']}.png"), plan_path.parent)
        output_path = resolve_path(slide["image"], plan_path.parent)
        assert source_path is not None and output_path is not None
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        compose_slide(plan, slide, source_path, output_path)
        print(f"Composed UI {slide['id']} -> {output_path}")


if __name__ == "__main__":
    main()
