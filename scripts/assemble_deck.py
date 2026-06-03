#!/usr/bin/env python3
"""Assemble a Parallel Digital template deck from chapter text and PNG slides.

The script keeps template chapter pages native/editable and inserts content
images as full-bleed slides.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from pptx import Presentation


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "assets" / "parallel-digital-standard-template.pptx"


def resolve_path(value: str | None, base_dir: Path) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path


def replace_text_preserve_style(shape: Any, new_text: str) -> None:
    """Replace text while keeping the first run's style when possible."""
    if not getattr(shape, "has_text_frame", False):
        return

    paragraphs = shape.text_frame.paragraphs
    first_run = None
    for paragraph in paragraphs:
        if paragraph.runs:
            first_run = paragraph.runs[0]
            break

    if first_run is None:
        shape.text = new_text
        return

    used = False
    for paragraph in paragraphs:
        for run in paragraph.runs:
            if not used:
                run.text = new_text
                used = True
            else:
                run.text = ""


def replace_matching_text(slide: Any, replacements: dict[str, str]) -> None:
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue
        text = shape.text.strip()
        name = getattr(shape, "name", "")
        for key, value in replacements.items():
            if text == key or name == key:
                replace_text_preserve_style(shape, value)


def duplicate_slide(prs: Presentation, source_slide: Any) -> Any:
    """Duplicate a slide's shapes onto a new slide using the same layout."""
    new_slide = prs.slides.add_slide(source_slide.slide_layout)

    for shape in list(new_slide.shapes):
        new_slide.shapes._spTree.remove(shape.element)

    for shape in source_slide.shapes:
        new_el = copy.deepcopy(shape.element)
        new_slide.shapes._spTree.insert_element_before(new_el, "p:extLst")

    return new_slide


def delete_slide_by_id(prs: Presentation, slide_id: int) -> None:
    for idx, slide in enumerate(prs.slides):
        if slide.slide_id == slide_id:
            sld_id = prs.slides._sldIdLst[idx]
            rel_id = sld_id.rId
            prs.part.drop_rel(rel_id)
            prs.slides._sldIdLst.remove(sld_id)
            return


def reorder_slides(prs: Presentation, ordered_slide_ids: list[int]) -> None:
    sld_id_list = prs.slides._sldIdLst
    elem_by_id = {int(elem.get("id")): elem for elem in list(sld_id_list)}

    for elem in list(sld_id_list):
        sld_id_list.remove(elem)

    for slide_id in ordered_slide_ids:
        elem = elem_by_id.get(slide_id)
        if elem is not None:
            sld_id_list.append(elem)


def add_full_bleed_image_slide(prs: Presentation, image_path: Path) -> Any:
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    slide.shapes.add_picture(
        str(image_path),
        0,
        0,
        width=prs.slide_width,
        height=prs.slide_height,
    )
    return slide


def update_cover(slide: Any, manifest: dict[str, Any]) -> None:
    replacements: dict[str, str] = {}
    if manifest.get("cover_title"):
        replacements["平行数字PPT模板"] = manifest["cover_title"]
        replacements["文本框 8"] = manifest["cover_title"]
    if manifest.get("footer"):
        replacements["平行数字  交叉现实"] = manifest["footer"]
    if replacements:
        replace_matching_text(slide, replacements)


def update_catalogue(slide: Any, sections: list[dict[str, Any]], footer: str | None) -> None:
    replacements: dict[str, str] = {}
    chinese_slots = ["第一节", "第二节", "第三节", "第四节"]
    for idx, section in enumerate(sections[:4]):
        subtitle = section.get("subtitle") or section.get("main_title") or chinese_slots[idx]
        replacements[chinese_slots[idx]] = subtitle
    if footer:
        replacements["平行数字  交叉现实"] = footer
    if replacements:
        replace_matching_text(slide, replacements)


def build_deck(manifest_path: Path) -> Path:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_dir = manifest_path.parent

    template_path = resolve_path(manifest.get("template"), base_dir) or DEFAULT_TEMPLATE
    output_path = resolve_path(manifest.get("output"), base_dir)
    if output_path is None:
        raise ValueError("manifest must include an output path")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation(str(template_path))
    if len(prs.slides) < 5:
        raise ValueError("template must contain at least 5 slides")

    cover_id = prs.slides[0].slide_id
    catalogue_id = prs.slides[1].slide_id
    source_section_id = prs.slides[2].slide_id
    unused_content_id = prs.slides[3].slide_id
    closing_id = prs.slides[4].slide_id
    source_section_slide = prs.slides[2]

    include_cover = manifest.get("include_cover", True)
    include_catalogue = manifest.get("include_catalogue", True)
    include_closing = manifest.get("include_closing", True)
    footer = manifest.get("footer")
    sections = manifest.get("sections", [])

    ordered_ids: list[int] = []

    if include_cover:
        update_cover(prs.slides[0], manifest)
        ordered_ids.append(cover_id)

    if include_catalogue:
        update_catalogue(prs.slides[1], sections, footer)
        ordered_ids.append(catalogue_id)

    for section in sections:
        section_slide = duplicate_slide(prs, source_section_slide)
        replace_matching_text(
            section_slide,
            {
                "MAIN TITLE": section.get("main_title", ""),
                "文本框 4": section.get("main_title", ""),
                "内容标题": section.get("subtitle", ""),
                "文本框 5": section.get("subtitle", ""),
                "平行数字  交叉现实": footer or "平行数字  交叉现实",
            },
        )
        ordered_ids.append(section_slide.slide_id)

        for item in section.get("slides", []):
            image_path = resolve_path(item.get("image"), base_dir)
            if image_path is None or not image_path.exists():
                raise FileNotFoundError(f"missing content image: {item.get('image')}")
            content_slide = add_full_bleed_image_slide(prs, image_path)
            ordered_ids.append(content_slide.slide_id)

    if include_closing:
        if footer:
            replace_matching_text(prs.slides[4], {"平行数字  交叉现实": footer})
        ordered_ids.append(closing_id)

    keep_ids = set(ordered_ids)
    for slide in list(prs.slides):
        if slide.slide_id not in keep_ids:
            delete_slide_by_id(prs, slide.slide_id)

    reorder_slides(prs, ordered_ids)
    prs.save(str(output_path))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to assembly manifest JSON")
    args = parser.parse_args()

    output = build_deck(Path(args.manifest).resolve())
    print(f"Created {output}")


if __name__ == "__main__":
    main()
