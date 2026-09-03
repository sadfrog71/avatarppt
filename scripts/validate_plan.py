#!/usr/bin/env python3
"""Validate an image-avatar-ppt deck plan before paid API calls."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from deck_utils import (
    DEFAULT_BODY_FONT_SIZE_PT,
    DEFAULT_CAPTION_FONT_SIZE_PT,
    DEFAULT_MAX_ACCENT_GRAPHIC_AREA_RATIO,
    DEFAULT_MAX_IMAGE_AREA_RATIO,
    DEFAULT_MINIMUM_FONT_SIZE_PT,
    DEFAULT_TITLE_FONT_SIZE_PT,
    HEX_COLOR,
    iter_slides,
    load_plan,
)


REQUIRED_PALETTE_KEYS = (
    "primary",
    "secondary",
    "accent",
    "background",
    "text",
)
ALLOWED_PROVIDERS = {"openai", "minimax"}
ALLOWED_MINIMAX_REGIONS = {"cn", "global"}
ALLOWED_COMPOSITION_MODES = {
    "direct_imagegen_slide",
    "designed_canvas",
    "ui_designer",
    "overlay_panels",
}
ALLOWED_CLAIM_TYPES = {"fact", "inference", "proposal", "decision"}
ALLOWED_THESIS_EXPRESSIONS = {"implicit", "explicit"}
ALLOWED_AUTHORSHIP_MODES = {"balanced", "editorial", "strict"}
ALLOWED_STATIC_AUDIT_MODES = {"warn", "strict"}
ALLOWED_VISUAL_SOURCES = {
    "source_evidence",
    "native_chart",
    "native_diagram",
    "generated_visual",
    "mixed",
}
ALLOWED_TITLE_RENDER_MODES = {"image", "native", "none"}
ALLOWED_GRAPHIC_ROLES = {"accent", "explanatory", "evidence", "none"}
ALLOWED_EDITABLE_TEXT_ROLES = {
    "heading",
    "body",
    "metric",
    "label",
    "caption",
    "note",
}
ALLOWED_TEXT_ALIGNMENTS = {"left", "center", "right"}
ALLOWED_VERTICAL_ALIGNMENTS = {"top", "middle", "bottom"}
ALLOWED_PRIMARY_LANGUAGES = {"zh-Hant", "zh-Hans", "en", "mixed"}
ALLOWED_MATERIAL_FORMS = {
    "typography",
    "source_evidence",
    "data_visual",
    "diagram",
    "illustration",
    "table",
    "mixed",
}
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

    language = plan.get("language")
    if language is not None:
        if not isinstance(language, dict):
            errors.append("top-level 'language' must be an object")
        else:
            if language.get("primary", "zh-Hant") not in ALLOWED_PRIMARY_LANGUAGES:
                errors.append(
                    "language.primary must be zh-Hant, zh-Hans, en, or mixed"
                )
            preserve_terms = language.get("preserve_terms")
            if preserve_terms is not None and (
                not isinstance(preserve_terms, list)
                or not preserve_terms
                or any(
                    not isinstance(item, str) or not item.strip()
                    for item in preserve_terms
                )
            ):
                errors.append(
                    "language.preserve_terms must be a non-empty array of strings"
                )

    storyline = plan.get("storyline")
    if not isinstance(storyline, dict):
        errors.append("top-level 'storyline' must be an object")
    else:
        for field in ("core_thesis", "decision_request"):
            if not isinstance(storyline.get(field), str) or not storyline[field].strip():
                errors.append(f"storyline.{field} is required")
        audience_priority = storyline.get("audience_priority")
        if not isinstance(audience_priority, list) or not audience_priority:
            errors.append("storyline.audience_priority must be a non-empty array")
        elif any(
            not isinstance(item, str) or not item.strip()
            for item in audience_priority
        ):
            errors.append(
                "storyline.audience_priority contains an empty/non-string item"
            )
        story_arc = storyline.get("story_arc")
        if not isinstance(story_arc, list) or not 3 <= len(story_arc) <= 6:
            errors.append("storyline.story_arc must contain 3 to 6 moves")
        else:
            for move_index, move in enumerate(story_arc):
                prefix = f"storyline.story_arc[{move_index}]"
                if not isinstance(move, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                for field in ("move", "question", "answer"):
                    if not isinstance(move.get(field), str) or not move[field].strip():
                        errors.append(f"{prefix}.{field} is required")

    storyline_review = plan.get("storyline_review")
    if not isinstance(storyline_review, dict):
        errors.append("top-level 'storyline_review' must be an object")
    else:
        if storyline_review.get("status") != "pass":
            errors.append("storyline_review.status must be 'pass' before generation")
        for field in (
            "thesis_alignment",
            "executive_relevance",
            "flow",
            "visual_consistency",
        ):
            if not isinstance(storyline_review.get(field), str) or not storyline_review[
                field
            ].strip():
                errors.append(f"storyline_review.{field} is required")
        open_issues = storyline_review.get("open_issues")
        if not isinstance(open_issues, list):
            errors.append("storyline_review.open_issues must be an array")
        elif open_issues:
            errors.append("storyline_review.open_issues must be empty before generation")

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

    typography = plan.get("typography")
    minimum_font_size_pt = DEFAULT_MINIMUM_FONT_SIZE_PT
    body_font_size_pt = DEFAULT_BODY_FONT_SIZE_PT
    prefer_editable = False
    if typography is not None:
        if not isinstance(typography, dict):
            errors.append("top-level 'typography' must be an object")
        else:
            font_defaults = {
                "minimum_font_size_pt": DEFAULT_MINIMUM_FONT_SIZE_PT,
                "body_font_size_pt": DEFAULT_BODY_FONT_SIZE_PT,
                "title_font_size_pt": DEFAULT_TITLE_FONT_SIZE_PT,
                "caption_font_size_pt": DEFAULT_CAPTION_FONT_SIZE_PT,
            }
            resolved_fonts: dict[str, float] = {}
            for field, fallback in font_defaults.items():
                value = typography.get(field, fallback)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or value <= 0
                ):
                    errors.append(f"typography.{field} must be a positive number")
                    resolved_fonts[field] = fallback
                else:
                    resolved_fonts[field] = float(value)
            minimum_font_size_pt = resolved_fonts["minimum_font_size_pt"]
            body_font_size_pt = resolved_fonts["body_font_size_pt"]
            if minimum_font_size_pt < 18:
                errors.append("typography.minimum_font_size_pt must be at least 18")
            if body_font_size_pt < 20:
                errors.append("typography.body_font_size_pt must be at least 20")
            if resolved_fonts["title_font_size_pt"] < body_font_size_pt:
                errors.append(
                    "typography.title_font_size_pt must be no smaller than body_font_size_pt"
                )
            if resolved_fonts["caption_font_size_pt"] < minimum_font_size_pt:
                errors.append(
                    "typography.caption_font_size_pt must be no smaller than minimum_font_size_pt"
                )
            font_name = typography.get("font_name")
            if font_name is not None and (
                not isinstance(font_name, str) or not font_name.strip()
            ):
                errors.append("typography.font_name must be a non-empty string")
            prefer_value = typography.get("prefer_editable_text", True)
            if not isinstance(prefer_value, bool):
                errors.append("typography.prefer_editable_text must be a boolean")
            else:
                prefer_editable = prefer_value

    authorship = plan.get("authorship")
    if authorship is not None:
        if not isinstance(authorship, dict):
            errors.append("top-level 'authorship' must be an object")
        else:
            if authorship.get("mode", "editorial") not in ALLOWED_AUTHORSHIP_MODES:
                errors.append("authorship.mode must be balanced, editorial, or strict")
            if authorship.get("static_audit", "warn") not in ALLOWED_STATIC_AUDIT_MODES:
                errors.append("authorship.static_audit must be warn or strict")
            for field in (
                "max_formulaic_title_ratio",
                "max_same_layout_ratio",
                "max_standard_ai_device_ratio",
                "max_typography_first_ratio",
                "max_same_material_form_ratio",
            ):
                value = authorship.get(field)
                if value is not None and (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not 0 <= value <= 1
                ):
                    errors.append(f"authorship.{field} must be a number from 0 to 1")
            for field in (
                "max_same_layout_run",
                "max_exact_text_items",
                "max_exact_text_characters",
            ):
                value = authorship.get(field)
                if value is not None and (
                    isinstance(value, bool) or not isinstance(value, int) or value < 1
                ):
                    errors.append(f"authorship.{field} must be a positive integer")
            for field in ("allowed_formulaic_titles", "allowed_cliche_terms"):
                value = authorship.get(field)
                if value is not None and (
                    not isinstance(value, list)
                    or any(not isinstance(item, str) or not item.strip() for item in value)
                ):
                    errors.append(f"authorship.{field} must be an array of strings")
            for field in (
                "require_conclusion_titles",
                "require_semantic_visual_anchor",
                "require_result_evidence_on_metrics",
            ):
                value = authorship.get(field)
                if value is not None and not isinstance(value, bool):
                    errors.append(f"authorship.{field} must be a boolean")

    max_accent_graphic_area_ratio = DEFAULT_MAX_ACCENT_GRAPHIC_AREA_RATIO
    max_image_area_ratio = DEFAULT_MAX_IMAGE_AREA_RATIO
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
        composition_mode = generation.get("composition_mode", "overlay_panels")
        if composition_mode not in ALLOWED_COMPOSITION_MODES:
            errors.append("image_generation.composition_mode is not supported")
        if generation.get("background_mode", "solid") != "solid":
            errors.append("image_generation.background_mode must be 'solid'")
        configured_graphic_ratio = generation.get(
            "max_accent_graphic_area_ratio",
            DEFAULT_MAX_ACCENT_GRAPHIC_AREA_RATIO,
        )
        if (
            isinstance(configured_graphic_ratio, bool)
            or not isinstance(configured_graphic_ratio, (int, float))
            or not 0 < configured_graphic_ratio <= 0.30
        ):
            errors.append(
                "image_generation.max_accent_graphic_area_ratio must be a number "
                "greater than 0 and no greater than 0.30"
            )
        else:
            max_accent_graphic_area_ratio = float(configured_graphic_ratio)
        configured_image_ratio = generation.get(
            "max_image_area_ratio",
            DEFAULT_MAX_IMAGE_AREA_RATIO,
        )
        if (
            isinstance(configured_image_ratio, bool)
            or not isinstance(configured_image_ratio, (int, float))
            or not 0 < configured_image_ratio <= 0.30
        ):
            errors.append(
                "image_generation.max_image_area_ratio must be a number "
                "greater than 0 and no greater than 0.30"
            )
        else:
            max_image_area_ratio = float(configured_image_ratio)
        allow_nonwhite = generation.get("allow_nonwhite_background", False)
        if not isinstance(allow_nonwhite, bool):
            errors.append(
                "image_generation.allow_nonwhite_background must be a boolean"
            )
        palette_config = plan.get("palette")
        background = (
            palette_config.get("background")
            if isinstance(palette_config, dict)
            else None
        )
        if (
            isinstance(background, str)
            and background.upper() != "#FFFFFF"
            and allow_nonwhite is not True
        ):
            errors.append(
                "palette.background must be #FFFFFF unless "
                "image_generation.allow_nonwhite_background is true"
            )
        if composition_mode == "direct_imagegen_slide" and generation.get(
            "local_text_overlay"
        ):
            errors.append(
                "direct_imagegen_slide cannot use image_generation.local_text_overlay"
            )
        if prefer_editable and composition_mode == "direct_imagegen_slide":
            errors.append(
                "typography.prefer_editable_text=true conflicts with "
                "image_generation.composition_mode=direct_imagegen_slide"
            )
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
        deck_style_review = vision.get("deck_style_review")
        if deck_style_review is not None and not isinstance(deck_style_review, bool):
            errors.append("vision_review.deck_style_review must be a boolean")
        contact_sheet = vision.get("contact_sheet")
        if contact_sheet is not None and (
            not isinstance(contact_sheet, str) or not contact_sheet.strip()
        ):
            errors.append("vision_review.contact_sheet must be a non-empty path")

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

        for field in (
            "title",
            "audience_question",
            "message",
            "narrative_role",
            "content_boundary",
            "thesis_connection",
            "visual_subject",
            "visual_focus",
            "information_topology",
            "visual_reasoning",
        ):
            if not isinstance(slide.get(field), str) or not slide[field].strip():
                errors.append(f"{prefix}.{field} is required")

        claim_type = slide.get("claim_type")
        if claim_type not in ALLOWED_CLAIM_TYPES:
            errors.append(
                f"{prefix}.claim_type must be fact, inference, proposal, or decision"
            )

        thesis_expression = slide.get("thesis_expression")
        if thesis_expression not in ALLOWED_THESIS_EXPRESSIONS:
            errors.append(
                f"{prefix}.thesis_expression must be implicit or explicit"
            )

        transition = slide.get("transition")
        if not isinstance(transition, dict):
            errors.append(f"{prefix}.transition must be an object")
        else:
            for field in ("from_previous", "to_next"):
                if not isinstance(transition.get(field), str) or not transition[
                    field
                ].strip():
                    errors.append(f"{prefix}.transition.{field} is required")

        speaker_notes = slide.get("speaker_notes")
        if speaker_notes is not None and (
            not isinstance(speaker_notes, str) or not speaker_notes.strip()
        ):
            errors.append(f"{prefix}.speaker_notes must be a non-empty string")

        layout = slide.get("layout_type")
        if layout not in ALLOWED_LAYOUTS:
            errors.append(f"{prefix}.layout_type is not supported")

        visual_source = slide.get("visual_source")
        if visual_source is not None and visual_source not in ALLOWED_VISUAL_SOURCES:
            errors.append(
                f"{prefix}.visual_source must be source_evidence, native_chart, "
                "native_diagram, generated_visual, or mixed"
            )
        title_render_mode = slide.get("title_render_mode")
        if (
            title_render_mode is not None
            and title_render_mode not in ALLOWED_TITLE_RENDER_MODES
        ):
            errors.append(f"{prefix}.title_render_mode must be image, native, or none")
        graphic_role = slide.get("graphic_role")
        if graphic_role is not None and graphic_role not in ALLOWED_GRAPHIC_ROLES:
            errors.append(
                f"{prefix}.graphic_role must be accent, explanatory, evidence, or none"
            )
        material_form = slide.get("material_form")
        if material_form is not None and material_form not in ALLOWED_MATERIAL_FORMS:
            errors.append(
                f"{prefix}.material_form must be typography, source_evidence, "
                "data_visual, diagram, illustration, table, or mixed"
            )
        semantic_visual_anchor = slide.get("semantic_visual_anchor")
        if semantic_visual_anchor is not None and (
            not isinstance(semantic_visual_anchor, str)
            or not semantic_visual_anchor.strip()
        ):
            errors.append(
                f"{prefix}.semantic_visual_anchor must be a non-empty string"
            )
        require_anchor = isinstance(authorship, dict) and authorship.get(
            "require_semantic_visual_anchor", False
        )
        if require_anchor:
            if material_form is None:
                errors.append(f"{prefix}.material_form is required by authorship")
            if graphic_role in {"accent", "explanatory", "evidence"} and not (
                isinstance(semantic_visual_anchor, str)
                and semantic_visual_anchor.strip()
            ):
                errors.append(
                    f"{prefix}.semantic_visual_anchor is required for "
                    f"graphic_role={graphic_role}"
                )
        if graphic_role == "none" and isinstance(semantic_visual_anchor, str):
            errors.append(
                f"{prefix}.semantic_visual_anchor conflicts with graphic_role=none"
            )
        graphic_area_ratio = slide.get("graphic_area_ratio")
        if graphic_area_ratio is not None and (
            isinstance(graphic_area_ratio, bool)
            or not isinstance(graphic_area_ratio, (int, float))
            or not 0 <= graphic_area_ratio <= 1
        ):
            errors.append(f"{prefix}.graphic_area_ratio must be a number from 0 to 1")
        elif isinstance(graphic_area_ratio, (int, float)) and not isinstance(
            graphic_area_ratio, bool
        ):
            if (
                graphic_role == "accent"
                and not 0 < graphic_area_ratio <= max_accent_graphic_area_ratio
            ):
                errors.append(
                    f"{prefix}.graphic_area_ratio must be greater than 0 and no "
                    f"greater than the configured accent limit of "
                    f"{max_accent_graphic_area_ratio:.2f}"
                )
            if graphic_role == "none" and graphic_area_ratio != 0:
                errors.append(
                    f"{prefix}.graphic_area_ratio must be 0 when graphic_role is none"
                )
        image_area_ratio = slide.get("image_area_ratio")
        if image_area_ratio is None:
            if prefer_editable:
                errors.append(
                    f"{prefix}.image_area_ratio is required when editable text is preferred"
                )
        elif (
            isinstance(image_area_ratio, bool)
            or not isinstance(image_area_ratio, (int, float))
            or not 0 <= image_area_ratio <= 1
        ):
            errors.append(f"{prefix}.image_area_ratio must be a number from 0 to 1")
        elif image_area_ratio > max_image_area_ratio:
            errors.append(
                f"{prefix}.image_area_ratio must be no greater than the configured "
                f"image limit of {max_image_area_ratio:.2f}"
            )
        layout_family = slide.get("layout_family")
        if layout_family is not None and (
            not isinstance(layout_family, str) or not layout_family.strip()
        ):
            errors.append(f"{prefix}.layout_family must be a non-empty string")
        for field in ("source_asset_refs", "graphic_devices"):
            value = slide.get(field)
            if value is not None and (
                not isinstance(value, list)
                or any(not isinstance(item, str) or not item.strip() for item in value)
            ):
                errors.append(f"{prefix}.{field} must be an array of strings")

        result_evidence = slide.get("result_evidence")
        require_result_evidence = isinstance(authorship, dict) and authorship.get(
            "require_result_evidence_on_metrics", False
        )
        if result_evidence is not None:
            if not isinstance(result_evidence, dict):
                errors.append(f"{prefix}.result_evidence must be an object")
            else:
                for field in ("baseline", "target", "actual", "time_period"):
                    if field not in result_evidence:
                        errors.append(f"{prefix}.result_evidence.{field} is required")
                    elif result_evidence[field] is not None and (
                        not isinstance(result_evidence[field], str)
                        or not result_evidence[field].strip()
                    ):
                        errors.append(
                            f"{prefix}.result_evidence.{field} must be a non-empty "
                            "string or null"
                        )
                source_ref = result_evidence.get("source_ref")
                if source_ref is not None and (
                    not isinstance(source_ref, str) or not source_ref.strip()
                ):
                    errors.append(
                        f"{prefix}.result_evidence.source_ref must be a non-empty string"
                    )
        elif require_result_evidence and layout == "metrics":
            errors.append(
                f"{prefix}.result_evidence is required for metrics slides"
            )

        exact_text = slide.get("exact_text")
        if not isinstance(exact_text, list) or not exact_text:
            errors.append(f"{prefix}.exact_text must be a non-empty array")
        elif any(not isinstance(item, str) or not item.strip() for item in exact_text):
            errors.append(f"{prefix}.exact_text contains an empty/non-string item")
        elif len(exact_text) != len(set(exact_text)):
            errors.append(f"{prefix}.exact_text must not contain duplicate items")
        elif thesis_expression == "implicit" and isinstance(storyline, dict):
            visible_text = "\n".join(exact_text)
            for field in ("core_thesis", "decision_request"):
                value = storyline.get(field)
                if isinstance(value, str) and value.strip() and value.strip() in visible_text:
                    errors.append(
                        f"{prefix}.exact_text leaks storyline.{field} while "
                        "thesis_expression is implicit"
                    )

        editable_text = slide.get("editable_text")
        if editable_text is None:
            if prefer_editable:
                errors.append(
                    f"{prefix}.editable_text is required when typography.prefer_editable_text=true"
                )
        elif not isinstance(editable_text, list) or not editable_text:
            errors.append(f"{prefix}.editable_text must be a non-empty array")
        else:
            editable_strings: list[str] = []
            for item_index, item in enumerate(editable_text):
                item_prefix = f"{prefix}.editable_text[{item_index}]"
                if not isinstance(item, dict):
                    errors.append(f"{item_prefix} must be an object")
                    continue
                text = item.get("text")
                if not isinstance(text, str) or not text.strip():
                    errors.append(f"{item_prefix}.text is required")
                else:
                    editable_strings.append(text)
                role = item.get("role", "body")
                if role not in ALLOWED_EDITABLE_TEXT_ROLES:
                    errors.append(
                        f"{item_prefix}.role must be heading, body, metric, label, "
                        "caption, or note"
                    )
                for field in ("x", "y", "width", "height"):
                    value = item.get(field)
                    if (
                        isinstance(value, bool)
                        or not isinstance(value, (int, float))
                        or not 0 <= value <= 1
                    ):
                        errors.append(
                            f"{item_prefix}.{field} must be a normalized number from 0 to 1"
                        )
                x = item.get("x")
                y = item.get("y")
                width = item.get("width")
                height = item.get("height")
                if all(
                    not isinstance(value, bool) and isinstance(value, (int, float))
                    for value in (x, y, width, height)
                ):
                    if width <= 0 or height <= 0:
                        errors.append(f"{item_prefix}.width and height must be positive")
                    if x + width > 1.0001 or y + height > 1.0001:
                        errors.append(f"{item_prefix} extends beyond the slide canvas")
                font_size = item.get("font_size_pt")
                if (
                    isinstance(font_size, bool)
                    or not isinstance(font_size, (int, float))
                ):
                    errors.append(f"{item_prefix}.font_size_pt must be a number")
                else:
                    required_size = (
                        minimum_font_size_pt
                        if role in {"caption", "label", "note"}
                        else body_font_size_pt
                    )
                    if font_size < required_size:
                        errors.append(
                            f"{item_prefix}.font_size_pt must be at least "
                            f"{required_size:g} for role={role}"
                        )
                bold = item.get("bold")
                if bold is not None and not isinstance(bold, bool):
                    errors.append(f"{item_prefix}.bold must be a boolean")
                alignment = item.get("alignment")
                if alignment is not None and alignment not in ALLOWED_TEXT_ALIGNMENTS:
                    errors.append(
                        f"{item_prefix}.alignment must be left, center, or right"
                    )
                vertical = item.get("vertical_alignment")
                if (
                    vertical is not None
                    and vertical not in ALLOWED_VERTICAL_ALIGNMENTS
                ):
                    errors.append(
                        f"{item_prefix}.vertical_alignment must be top, middle, or bottom"
                    )
                color = item.get("color")
                if color is not None and (
                    not isinstance(color, str)
                    or (
                        color not in {"primary", "secondary", "accent", "text", "muted"}
                        and not HEX_COLOR.fullmatch(color)
                    )
                ):
                    errors.append(
                        f"{item_prefix}.color must be a palette key or six-digit hex color"
                    )
            if prefer_editable and isinstance(exact_text, list):
                planned = [str(item) for item in exact_text]
                missing = [
                    item for item in planned if editable_strings.count(item) != 1
                ]
                unplanned = [item for item in editable_strings if item not in planned]
                if missing:
                    errors.append(
                        f"{prefix}.editable_text must contain each exact_text item exactly once: "
                        + ", ".join(missing)
                    )
                if unplanned:
                    errors.append(
                        f"{prefix}.editable_text contains text outside exact_text: "
                        + ", ".join(unplanned)
                    )
                if (
                    title_render_mode == "native"
                    and isinstance(slide.get("title"), str)
                    and slide["title"] in editable_strings
                ):
                    errors.append(
                        f"{prefix}.editable_text duplicates the native title"
                    )

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
