#!/usr/bin/env python3
"""Run a zero-cost static audit for formulaic copy and generic AI slide patterns."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from deck_utils import (
    iter_slides,
    load_plan,
    max_accent_graphic_area_ratio,
    resolved_graphic_area_ratio,
    resolved_graphic_role,
    resolved_title_render_mode,
)
from validate_plan import validate_plan


FORMULAIC_TITLE_PATTERNS = (
    (
        "not_but",
        re.compile(
            r"(?:不是|不再|不只|[并並]非|不替代|不依[赖賴]|不等[于於]).{1,40}"
            r"(?:而是|而在于|更是)"
        ),
    ),
    ("from_to", re.compile(r"[从從].{1,32}(?:到|走向|[转轉]向).{1,}")),
    ("first_then", re.compile(r"先.{1,32}(?:再|然[后後]).{1,}")),
    ("not_only_but", re.compile(r"不[仅僅].{1,32}(?:而且|[还還]|更).{1,}")),
    ("not_instead", re.compile(r"不用.{1,32}代替")),
)

CLICHE_TERMS = (
    "全面赋能",
    "全面賦能",
    "深度赋能",
    "一站式",
    "全方位",
    "重新定义",
    "重新定義",
    "全面领先",
    "全面領先",
    "行业唯一",
    "行業唯一",
    "引领行业",
    "引領行業",
    "重塑未来",
    "重塑未來",
    "开启新篇章",
    "開啟新篇章",
)

STANDARD_AI_DEVICE_PATTERNS = {
    "central_hub": re.compile(r"中央|中心(?:[节節]点|[圆圓]环|[枢樞]纽)|[环環][绕繞]中央"),
    "icon_badges": re.compile(r"[圆圓]形[图圖][标標]|[图圖][标標]徽章|icon[- ]?badge", re.IGNORECASE),
    "rounded_card_grid": re.compile(r"[圆圓]角卡片|卡片[阵陣]列|卡片矩[阵陣]|card grid|rounded card", re.IGNORECASE),
    "decorative_tech": re.compile(r"[发發]光(?:大[脑腦]|芯片|晶片|机器人|機器人)|[悬懸]浮(?:卡片|[图圖][标標]|物体|物體)|等距世界|isometric world|glowing (?:brain|chip)", re.IGNORECASE),
}

TOPIC_ONLY_TITLE_PATTERN = re.compile(
    r"^(?:[项項]目(?:背景|概[况況]|成效|成果|[总總]结)?|專案(?:背景|概況|成效|成果|總結)?|"
    r"建[设設](?:目[标標]|[内內]容|成效|路[径徑])?|"
    r"平台(?:目[标標]|架构|架構|能力)?|[应應]用(?:[场場]景|成效)?|"
    r"行[业業](?:背景|[现現]状)?|[总總]体目[标標]|[实實]施路[径徑]|"
    r"[项項]目成效|[项項]目成果|專案成效|專案成果|下一步|[总總]结|"
    r"整[体體](?:架构|架構|方案)?|技[术術]架构|技術架構|[业業]務架构|業務架構|"
    r"概[览覽]|[现現]状|背景|目[标標]|策略|方案|架构|架構|机制|機制|[规規][划劃])"
    r"(?:[（(].*?[)）])?$"
)

DEFAULT_THRESHOLDS = {
    "max_formulaic_title_ratio": 0.25,
    "max_same_layout_ratio": 0.45,
    "max_same_layout_run": 2,
    "max_exact_text_items": 14,
    "max_exact_text_characters": 220,
    "max_standard_ai_device_ratio": 0.35,
    "max_typography_first_ratio": 0.35,
    "max_same_material_form_ratio": 0.55,
}


def _number(config: dict[str, Any], key: str) -> float:
    value = config.get(key, DEFAULT_THRESHOLDS[key])
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        value = DEFAULT_THRESHOLDS[key]
    return float(value)


def _integer(config: dict[str, Any], key: str) -> int:
    value = config.get(key, DEFAULT_THRESHOLDS[key])
    if isinstance(value, bool) or not isinstance(value, int):
        value = DEFAULT_THRESHOLDS[key]
    return int(value)


def _repeated_runs(values: list[str], minimum_length: int) -> list[dict[str, Any]]:
    if not values:
        return []
    runs: list[dict[str, Any]] = []
    current_value = values[0]
    current_length = 1
    current_start = 0
    for index, value in enumerate(values[1:], start=1):
        if value == current_value:
            current_length += 1
        else:
            if current_length >= minimum_length:
                runs.append(
                    {
                        "value": current_value,
                        "length": current_length,
                        "start": current_start,
                    }
                )
            current_value = value
            current_length = 1
            current_start = index
    if current_length >= minimum_length:
        runs.append(
            {
                "value": current_value,
                "length": current_length,
                "start": current_start,
            }
        )
    return runs


def audit_plan(plan: dict[str, Any], strict: bool | None = None) -> dict[str, Any]:
    authorship = plan.get("authorship")
    if not isinstance(authorship, dict):
        authorship = {}
    if strict is None:
        strict = authorship.get("static_audit", "warn") == "strict"

    slides = [slide for _, _, slide in iter_slides(plan)]
    warnings: list[dict[str, Any]] = []
    slide_findings: list[dict[str, Any]] = []
    formulaic_title_slides: list[str] = []
    formulaic_opening_slides: list[str] = []
    standard_device_slides: list[str] = []
    layout_values: list[str] = []
    topology_values: list[str] = []
    graphic_role_values: list[str] = []
    accent_graphic_ratios: list[float] = []
    material_form_values: list[str] = []
    topic_only_title_slides: list[str] = []
    max_accent_ratio = max_accent_graphic_area_ratio(plan)

    allowed_titles = {
        item.strip()
        for item in authorship.get("allowed_formulaic_titles", [])
        if isinstance(item, str) and item.strip()
    }
    allowed_terms = {
        item.strip()
        for item in authorship.get("allowed_cliche_terms", [])
        if isinstance(item, str) and item.strip()
    }

    max_items = _integer(authorship, "max_exact_text_items")
    max_characters = _integer(authorship, "max_exact_text_characters")

    for slide in slides:
        slide_id = str(slide.get("id", "unknown"))
        title = str(slide.get("title", ""))
        finding: dict[str, Any] = {"id": slide_id, "issues": []}

        exact_text = slide.get("exact_text", [])
        if not isinstance(exact_text, list):
            exact_text = []
        title_patterns = [
            name
            for name, pattern in FORMULAIC_TITLE_PATTERNS
            if title not in allowed_titles and pattern.search(title)
        ]
        if title_patterns:
            formulaic_title_slides.append(slide_id)
            finding["formulaic_title_patterns"] = title_patterns
        if authorship.get("require_conclusion_titles", False) and (
            TOPIC_ONLY_TITLE_PATTERN.fullmatch(title.strip())
        ):
            topic_only_title_slides.append(slide_id)
            finding["topic_only_title"] = title

        opening_surface = " ".join([title, *[str(item) for item in exact_text[:2]]])
        opening_patterns = [
            name
            for name, pattern in FORMULAIC_TITLE_PATTERNS
            if title not in allowed_titles
            and pattern.search(opening_surface)
            and name not in title_patterns
        ]
        if opening_patterns:
            formulaic_opening_slides.append(slide_id)
            finding["formulaic_opening_patterns"] = opening_patterns

        title_render_mode = resolved_title_render_mode(plan, slide)
        title_declared_in_exact_text = title in [str(item) for item in exact_text]
        visible_title_items = int(
            bool(title)
            and title_render_mode != "none"
            and not title_declared_in_exact_text
        )
        visible_text_items = len(exact_text) + visible_title_items
        visible_text_characters = sum(len(str(item)) for item in exact_text) + (
            len(title) if visible_title_items else 0
        )
        finding["exact_text_items"] = len(exact_text)
        finding["exact_text_characters"] = sum(len(str(item)) for item in exact_text)
        finding["planned_visible_text_items"] = visible_text_items
        finding["planned_visible_text_characters"] = visible_text_characters
        if title_render_mode == "image" and title and not title_declared_in_exact_text:
            finding["issues"].append(
                "title_render_mode=image but title is absent from exact_text"
            )
        if title_render_mode == "native" and title_declared_in_exact_text:
            finding["issues"].append(
                "title_render_mode=native but title is present in exact_text"
            )
        if title_render_mode == "none" and title_declared_in_exact_text:
            finding["issues"].append(
                "title_render_mode=none but title is present in exact_text"
            )
        if visible_text_items > max_items:
            finding["issues"].append(
                f"planned visible copy has {visible_text_items} items; target is <= {max_items}"
            )
        if visible_text_characters > max_characters:
            finding["issues"].append(
                f"planned visible copy has {visible_text_characters} characters; target is <= {max_characters}"
            )

        visible_copy = " ".join([title, *[str(item) for item in exact_text]])
        cliche_terms = [
            term for term in CLICHE_TERMS if term not in allowed_terms and term in visible_copy
        ]
        if cliche_terms:
            finding["cliche_terms"] = cliche_terms

        visual_blob = " ".join(
            str(slide.get(field, ""))
            for field in ("visual_subject", "visual_focus", "visual_reasoning", "prompt")
        )
        graphic_devices = slide.get("graphic_devices", [])
        if isinstance(graphic_devices, list):
            visual_blob += " " + " ".join(str(item) for item in graphic_devices)
        else:
            graphic_devices = []
        graphic_role = resolved_graphic_role(plan, slide)
        graphic_area_ratio = resolved_graphic_area_ratio(plan, slide)
        graphic_role_is_explicit = slide.get("graphic_role") is not None
        graphic_role_values.append(graphic_role)
        finding["graphic_role"] = graphic_role
        finding["planned_graphic_area_ratio"] = graphic_area_ratio
        material_form = str(slide.get("material_form") or "unspecified")
        material_form_values.append(material_form)
        finding["material_form"] = material_form
        semantic_visual_anchor = str(
            slide.get("semantic_visual_anchor") or ""
        ).strip()
        if semantic_visual_anchor:
            finding["semantic_visual_anchor"] = semantic_visual_anchor
        if graphic_role == "accent":
            if graphic_area_ratio is not None:
                accent_graphic_ratios.append(graphic_area_ratio)
            if graphic_area_ratio is None or graphic_area_ratio <= 0:
                finding["issues"].append(
                    "graphic_role=accent requires a positive graphic_area_ratio"
                )
            elif graphic_area_ratio > max_accent_ratio:
                finding["issues"].append(
                    f"accent graphic area ratio {graphic_area_ratio:.2f} exceeds "
                    f"the configured limit of {max_accent_ratio:.2f}"
                )
            if graphic_role_is_explicit and not graphic_devices:
                finding["issues"].append(
                    "graphic_role=accent requires at least one semantic graphic device"
                )
        if graphic_role == "none" and graphic_devices:
            finding["issues"].append(
                "graphic_role=none conflicts with declared graphic_devices"
            )
        if authorship.get("require_semantic_visual_anchor", False):
            if graphic_role in {"accent", "explanatory", "evidence"} and not (
                semantic_visual_anchor
            ):
                finding["issues"].append(
                    f"graphic_role={graphic_role} lacks a semantic_visual_anchor"
                )
            if material_form == "typography" and graphic_role != "none":
                finding["issues"].append(
                    "material_form=typography cannot carry a non-none graphic role"
                )
        device_names = [
            name
            for name, pattern in STANDARD_AI_DEVICE_PATTERNS.items()
            if pattern.search(visual_blob)
        ]
        if device_names:
            standard_device_slides.append(slide_id)
            finding["standard_ai_devices"] = device_names

        visual_source = slide.get("visual_source")
        source_asset_refs = slide.get("source_asset_refs", [])
        if visual_source in {"source_evidence", "native_chart", "mixed"} and not source_asset_refs:
            finding["issues"].append(
                f"visual_source={visual_source} requires source_asset_refs for traceability"
            )
        if (
            slide.get("claim_type") == "fact"
            and visual_source == "generated_visual"
            and not source_asset_refs
        ):
            finding["issues"].append(
                "fact page relies on generated_visual without a source asset reference"
            )

        if authorship.get("require_result_evidence_on_metrics", False) and (
            slide.get("layout_type") == "metrics"
        ):
            evidence = slide.get("result_evidence")
            missing_fields = []
            if not isinstance(evidence, dict):
                missing_fields = ["baseline", "target", "actual", "time_period"]
            else:
                missing_fields = [
                    field
                    for field in ("baseline", "target", "actual", "time_period")
                    if not isinstance(evidence.get(field), str)
                    or not evidence[field].strip()
                ]
            if missing_fields:
                finding["issues"].append(
                    "metrics result_evidence is missing: " + ", ".join(missing_fields)
                )
            elif isinstance(evidence, dict):
                compact_surface = re.sub(
                    r"\s+", "", " ".join([title, *[str(item) for item in exact_text]])
                )
                hidden_fields = [
                    field
                    for field in ("baseline", "target", "actual", "time_period")
                    if re.sub(r"\s+", "", str(evidence[field]))
                    not in compact_surface
                ]
                if hidden_fields:
                    finding["issues"].append(
                        "metrics result_evidence is not visible: "
                        + ", ".join(hidden_fields)
                    )

        topology = str(slide.get("information_topology", "unspecified"))
        layout_family = str(slide.get("layout_family") or topology)
        topology_values.append(topology)
        layout_values.append(layout_family)
        if finding["issues"] or any(
            key in finding
            for key in (
                "formulaic_title_patterns",
                "formulaic_opening_patterns",
                "cliche_terms",
                "standard_ai_devices",
                "topic_only_title",
            )
        ):
            slide_findings.append(finding)

    slide_count = len(slides)
    formulaic_ratio = (
        len(set(formulaic_title_slides)) / slide_count if slide_count else 0.0
    )
    opening_formula_ratio = (
        len(set(formulaic_opening_slides)) / slide_count if slide_count else 0.0
    )
    device_ratio = len(set(standard_device_slides)) / slide_count if slide_count else 0.0
    layout_counts = Counter(layout_values)
    topology_counts = Counter(topology_values)
    material_form_counts = Counter(material_form_values)
    dominant_layout, dominant_layout_count = (
        layout_counts.most_common(1)[0] if layout_counts else ("", 0)
    )
    dominant_layout_ratio = dominant_layout_count / slide_count if slide_count else 0.0
    dominant_material_form, dominant_material_form_count = (
        material_form_counts.most_common(1)[0]
        if material_form_counts
        else ("", 0)
    )
    dominant_material_form_ratio = (
        dominant_material_form_count / slide_count if slide_count else 0.0
    )
    typography_first_count = material_form_counts.get("typography", 0)
    typography_first_ratio = typography_first_count / slide_count if slide_count else 0.0
    max_run = _integer(authorship, "max_same_layout_run")
    repeated_runs = _repeated_runs(layout_values, max_run + 1)
    longest_run = max((item["length"] for item in repeated_runs), default=1 if slides else 0)

    if slide_count >= 5 and formulaic_ratio > _number(
        authorship, "max_formulaic_title_ratio"
    ):
        warnings.append(
            {
                "code": "formulaic_title_ratio",
                "message": (
                    f"{len(set(formulaic_title_slides))}/{slide_count} titles use high-signal "
                    "formulaic structures"
                ),
                "slides": sorted(set(formulaic_title_slides)),
            }
        )
    if slide_count >= 6 and dominant_layout_ratio > _number(
        authorship, "max_same_layout_ratio"
    ):
        warnings.append(
            {
                "code": "dominant_layout_ratio",
                "message": (
                    f"layout family '{dominant_layout}' appears on "
                    f"{dominant_layout_count}/{slide_count} slides"
                ),
            }
        )
    if slide_count >= 4 and repeated_runs:
        rendered_runs = []
        for item in repeated_runs:
            start = int(item["start"])
            length = int(item["length"])
            rendered_runs.append(
                {
                    "layout_family": item["value"],
                    "length": length,
                    "slides": [
                        str(slides[index].get("id", "unknown"))
                        for index in range(start, start + length)
                    ],
                }
            )
        warnings.append(
            {
                "code": "repeated_layout_run",
                "message": f"{len(rendered_runs)} repeated layout runs exceed {max_run}",
                "runs": rendered_runs,
            }
        )
    if slide_count >= 5 and device_ratio > _number(
        authorship, "max_standard_ai_device_ratio"
    ):
        warnings.append(
            {
                "code": "standard_ai_device_ratio",
                "message": (
                    f"{len(set(standard_device_slides))}/{slide_count} slides specify "
                    "common AI-default visual devices"
                ),
                "slides": sorted(set(standard_device_slides)),
            }
        )

    if topic_only_title_slides:
        warnings.append(
            {
                "code": "topic_only_titles",
                "message": "some content-slide titles name a topic instead of stating a conclusion",
                "slides": sorted(set(topic_only_title_slides)),
            }
        )
    if (
        slide_count >= 6
        and "max_same_material_form_ratio" in authorship
        and dominant_material_form_ratio
        > _number(authorship, "max_same_material_form_ratio")
    ):
        warnings.append(
            {
                "code": "dominant_material_form_ratio",
                "message": (
                    f"material form '{dominant_material_form}' appears on "
                    f"{dominant_material_form_count}/{slide_count} slides"
                ),
            }
        )
    if (
        slide_count >= 6
        and "max_typography_first_ratio" in authorship
        and typography_first_ratio > _number(authorship, "max_typography_first_ratio")
    ):
        warnings.append(
            {
                "code": "typography_first_ratio",
                "message": (
                    f"{typography_first_count}/{slide_count} slides rely primarily "
                    "on typography"
                ),
            }
        )

    dense_slide_ids = [
        finding["id"]
        for finding in slide_findings
        if any(
            issue.startswith("planned visible copy has")
            for issue in finding["issues"]
        )
    ]
    if dense_slide_ids:
        warnings.append(
            {
                "code": "dense_generated_copy",
                "message": "some slides exceed planned visible-copy density guardrails",
                "slides": dense_slide_ids,
            }
        )

    provenance_issue_ids = [
        finding["id"]
        for finding in slide_findings
        if any("source asset" in issue for issue in finding["issues"])
    ]
    if provenance_issue_ids:
        warnings.append(
            {
                "code": "weak_visual_provenance",
                "message": "some evidence claims lack declared source material",
                "slides": provenance_issue_ids,
            }
        )

    title_contract_issue_ids = [
        finding["id"]
        for finding in slide_findings
        if any("title_render_mode=" in issue for issue in finding["issues"])
    ]
    if title_contract_issue_ids:
        warnings.append(
            {
                "code": "title_render_contract",
                "message": "some slides mix title rendering modes and exact_text incorrectly",
                "slides": title_contract_issue_ids,
            }
        )

    graphic_balance_issue_ids = [
        finding["id"]
        for finding in slide_findings
        if any(
            "graphic_role=" in issue or "accent graphic area ratio" in issue
            for issue in finding["issues"]
        )
    ]
    if graphic_balance_issue_ids:
        warnings.append(
            {
                "code": "graphic_balance_contract",
                "message": (
                    "some slides either suppress planned graphics or exceed the "
                    "accent-graphic budget"
                ),
                "slides": graphic_balance_issue_ids,
            }
        )

    semantic_anchor_issue_ids = [
        finding["id"]
        for finding in slide_findings
        if any(
            "semantic_visual_anchor" in issue
            or "material_form=typography" in issue
            for issue in finding["issues"]
        )
    ]
    if semantic_anchor_issue_ids:
        warnings.append(
            {
                "code": "semantic_visual_anchor_contract",
                "message": (
                    "some slides use text containers or declared graphics without a "
                    "non-text semantic anchor"
                ),
                "slides": semantic_anchor_issue_ids,
            }
        )

    result_evidence_issue_ids = [
        finding["id"]
        for finding in slide_findings
        if any("metrics result_evidence" in issue for issue in finding["issues"])
    ]
    if result_evidence_issue_ids:
        warnings.append(
            {
                "code": "result_evidence_contract",
                "message": (
                    "some metrics pages do not expose baseline, target, actual, "
                    "and time period"
                ),
                "slides": result_evidence_issue_ids,
            }
        )

    major_codes = {
        "formulaic_title_ratio",
        "dominant_layout_ratio",
        "repeated_layout_run",
        "standard_ai_device_ratio",
        "weak_visual_provenance",
        "title_render_contract",
        "graphic_balance_contract",
        "topic_only_titles",
        "dominant_material_form_ratio",
        "typography_first_ratio",
        "semantic_visual_anchor_contract",
        "result_evidence_contract",
    }
    major_warning_count = sum(item["code"] in major_codes for item in warnings)
    risk_level = "high" if major_warning_count >= 2 else "medium" if warnings else "low"
    errors = validate_plan(plan)
    passed = not errors and (not strict or not warnings)
    return {
        "passed": passed,
        "strict": strict,
        "risk_level": risk_level,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "slide_count": slide_count,
            "formulaic_title_count": len(set(formulaic_title_slides)),
            "formulaic_title_ratio": round(formulaic_ratio, 4),
            "formulaic_opening_copy_count": len(set(formulaic_opening_slides)),
            "formulaic_opening_copy_ratio": round(opening_formula_ratio, 4),
            "layout_family_counts": dict(sorted(layout_counts.items())),
            "topology_counts": dict(sorted(topology_counts.items())),
            "dominant_layout_ratio": round(dominant_layout_ratio, 4),
            "longest_same_layout_run": longest_run,
            "standard_ai_device_slide_count": len(set(standard_device_slides)),
            "standard_ai_device_ratio": round(device_ratio, 4),
            "graphic_role_counts": dict(
                sorted(Counter(graphic_role_values).items())
            ),
            "max_planned_accent_graphic_area_ratio": round(
                max(accent_graphic_ratios, default=0.0), 4
            ),
            "configured_max_accent_graphic_area_ratio": round(
                max_accent_ratio, 4
            ),
            "material_form_counts": dict(sorted(material_form_counts.items())),
            "dominant_material_form_ratio": round(
                dominant_material_form_ratio, 4
            ),
            "typography_first_ratio": round(typography_first_ratio, 4),
            "topic_only_title_count": len(set(topic_only_title_slides)),
        },
        "slide_findings": slide_findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a failing exit status when style warnings are present",
    )
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    report = audit_plan(load_plan(plan_path), strict=args.strict or None)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote {output_path}; passed={report['passed']}; risk={report['risk_level']}")
    else:
        print(rendered, end="")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
