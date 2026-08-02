#!/usr/bin/env python3
"""Generate palette-controlled slide images from a validated deck plan."""

from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Any

from credential_store import get_provider_secret
from deck_utils import iter_slides, load_plan, palette_description, resolve_path
from validate_plan import validate_plan


OPENAI_ENDPOINT = "https://api.openai.com/v1/images/generations"
MINIMAX_ENDPOINTS = {
    "cn": "https://api.minimaxi.com/v1/image_generation",
    "global": "https://api.minimax.io/v1/image_generation",
}


def build_prompt(plan: dict[str, Any], slide: dict[str, Any]) -> str:
    generation = plan["image_generation"]
    storyline = plan["storyline"]
    facts = "; ".join(slide.get("facts", [])) or "no unsupported numeric claims"
    negative = generation.get(
        "negative_prompt",
        "no watermark, no logo, no duplicated text, no cropped text",
    )
    if generation.get("local_text_overlay"):
        text_constraint = (
            "Do not render any words, letters, numbers, logos, captions, labels, "
            "watermarks, UI text, or pseudo-text. Leave calm negative space for a "
            "professional Chinese typography overlay added later."
        )
    else:
        exact_text = " | ".join(slide["exact_text"])
        text_constraint = (
            f"Render only this concise text, exactly as written: {exact_text}."
        )
    structured_prompt = (
        "Create one complete 16:9 presentation slide image. "
        f"Audience: {plan.get('audience', 'executive audience')}. "
        f"Objective: {plan.get('objective', '')}. "
        f"Deck thesis: {storyline['core_thesis']}. "
        f"Decision request: {storyline['decision_request']}. "
        f"Slide role: {slide['layout_type']}. "
        f"Audience question: {slide['audience_question']}. "
        f"Message: {slide['message']}. "
        f"Claim type: {slide['claim_type']}. "
        f"Information topology: {slide['information_topology']}. "
        f"Visual subject: {slide['visual_subject']}. "
        f"Dominant visual focus: {slide['visual_focus']}. "
        f"Visual reasoning: {slide['visual_reasoning']}. "
        f"Transition to next page: {slide['transition']['to_next']}. "
        f"Verified facts only: {facts}. "
        f"Exact palette: {palette_description(plan['palette'])}. "
        f"Visual style: {generation.get('style', 'clean executive presentation')}. "
        f"{text_constraint} "
        f"Use a pure solid {plan['palette']['background']} background with no "
        "background photo, texture, pattern, glow, or scenic wallpaper. Allow "
        "restrained nodes, connectors, paths, containers, icons, and pale color "
        "blocks when they encode relationships. Use one dominant visual system, "
        "clear hierarchy, generous margins, and a restrained style suitable for "
        "an executive decision meeting. "
        f"Avoid: {negative}."
    )
    custom_prompt = str(slide.get("prompt", "")).strip()
    if custom_prompt:
        return f"{custom_prompt}\n\nMandatory constraints:\n{structured_prompt}"
    return structured_prompt


def post_json(
    url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int,
    attempts: int = 2,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if attempt == attempts or exc.code < 500:
                raise RuntimeError(f"API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if attempt == attempts:
                raise RuntimeError(f"API connection failed: {exc}") from exc
        time.sleep(attempt)
    raise RuntimeError("API request failed")


def generate_openai(
    config: dict[str, Any],
    prompt: str,
    timeout: int,
) -> bytes:
    api_key = get_provider_secret("openai")
    if not api_key:
        raise RuntimeError(
            "OpenAI key is required in OPENAI_API_KEY or macOS Keychain"
        )
    payload = {
        "model": config.get("model", "gpt-image-2"),
        "prompt": prompt,
        "size": config.get("size", "2048x1152"),
        "quality": config.get("quality", "high"),
        "n": 1,
    }
    response = post_json(OPENAI_ENDPOINT, api_key, payload, timeout)
    try:
        encoded = response["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI image response: {response}") from exc
    return base64.b64decode(encoded)


def generate_minimax(
    config: dict[str, Any],
    prompt: str,
    timeout: int,
) -> bytes:
    api_key = get_provider_secret("minimax")
    if not api_key:
        raise RuntimeError(
            "MiniMax key is required in MINIMAX_API_KEY or macOS Keychain"
        )
    payload = {
        "model": config.get("model", "image-01"),
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "base64",
    }
    region = config.get("region", "global")
    response = post_json(MINIMAX_ENDPOINTS[region], api_key, payload, timeout)
    try:
        encoded = response["data"]["image_base64"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected MiniMax image response: {response}") from exc
    return base64.b64decode(encoded)


def save_as_png(image_bytes: bytes, output_path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required to normalize generated images to PNG"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(image_bytes)) as image:
        image.convert("RGB").save(output_path, format="PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", help="Path to deck-plan JSON")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved prompts without calling a provider",
    )
    parser.add_argument(
        "--confirm-paid-call",
        action="store_true",
        help="Required acknowledgement before non-dry-run API calls",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate images that already exist",
    )
    parser.add_argument("--limit", type=int, help="Generate at most N pending images")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))

    config = plan["image_generation"]
    provider = config["provider"]
    source_directory = config.get("source_directory")
    pending: list[tuple[dict[str, Any], Path, str]] = []
    for _, _, slide in iter_slides(plan):
        output_value = slide["image"]
        if source_directory:
            output_value = str(Path(source_directory) / f"{slide['id']}.png")
        output_path = resolve_path(output_value, plan_path.parent)
        assert output_path is not None
        if output_path.exists() and not args.overwrite:
            continue
        pending.append((slide, output_path, build_prompt(plan, slide)))

    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1")
        pending = pending[: args.limit]

    print(
        f"Provider={provider} model={config['model']} "
        f"quality={config.get('quality', 'provider-default')} pending={len(pending)}"
    )
    if args.dry_run:
        for slide, output_path, prompt in pending:
            print(f"\n[{slide['id']}] -> {output_path}\n{prompt}")
        return
    if not pending:
        print("No pending images.")
        return
    if not args.confirm_paid_call:
        raise SystemExit(
            "Paid API call blocked. Re-run with --confirm-paid-call after user approval."
        )

    generators = {
        "openai": generate_openai,
        "minimax": generate_minimax,
    }
    generator = generators[provider]
    for index, (slide, output_path, prompt) in enumerate(pending, start=1):
        print(f"Generating {index}/{len(pending)}: {slide['id']}")
        image_bytes = generator(config, prompt, args.timeout)
        save_as_png(image_bytes, output_path)
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
