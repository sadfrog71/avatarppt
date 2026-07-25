# Provider Contract

Provider details are isolated here so API changes do not bloat the main workflow.

## OpenAI Image Generation

- Endpoint: `POST https://api.openai.com/v1/images/generations`
- API key: `OPENAI_API_KEY`, falling back to Keychain service `imageavatarppt.openai.api-key`
- Default model: `gpt-image-2`
- Recommended PPT size: `2048x1152`
- Response image: `data[0].b64_json`
- Supported quality values: `low`, `medium`, `high`, `auto`

Use the Image API for one-shot slide generation. The OpenAI guide allows custom `gpt-image-2` sizes within its documented constraints; `2048x1152` is a documented 16:9 size.

## MiniMax Image Generation

- Endpoint: `POST https://api.minimax.io/v1/image_generation`
- API key: `MINIMAX_API_KEY`, falling back to Keychain service `imageavatarppt.minimax.api-key`
- Default model: `image-01`
- Set `aspect_ratio` to `16:9`
- Set `response_format` to `base64`
- Response images: `data.image_base64`

MiniMax supports an optional `subject_reference` array. Add it only when the user supplied a reference image and the provider contract supports the requested use.

## Kimi Vision Review

- Endpoint: `POST https://api.kimi.com/coding/`
- API key: `KIMI_API_KEY` or `MOONSHOT_API_KEY`, falling back to Keychain service `imageavatarppt.kimi.api-key`
- Default model: `kimi-k3`
- Send image input as a base64 data URL in an `image_url` message part.
- Keep `message.content` as a JSON array, not a serialized JSON string.

Use Kimi to check:

- expected text presence and obvious text corruption;
- layout collisions, clipping, and readability;
- palette adherence;
- semantic match between the slide message and the rendered visual.

Kimi's documented vision API understands images; it is not the image-generation adapter in this skill.

## Official References

- OpenAI Image Generation: `https://developers.openai.com/api/docs/guides/image-generation`
- MiniMax Image Generation: `https://platform.minimax.io/docs/guides/image-generation`
- Kimi Vision: `https://platform.kimi.com/docs/guide/use-kimi-vision-model`
- Kimi API Overview: `https://platform.kimi.com/docs/api/overview`

## Paid Call Gate

Before any non-dry-run request:

1. Count pending images or reviews.
2. State provider, model, size, and quality.
3. Ask for confirmation.
4. Never retry a paid request more than twice automatically.

## Credential Storage

- Prefer macOS Keychain over plaintext `.env` files.
- Store or rotate a key interactively with `python scripts/store_credentials.py <openai|minimax|kimi>`.
- Check availability without revealing values with `python scripts/check_credentials.py minimax kimi`.
- Never place keys in `deck-plan.json`, shell history, logs, source code, or generated artifacts.
- Environment variables take precedence over Keychain values for temporary overrides.
