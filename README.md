# avatarppt

`avatarppt` is a Codex skill for building image-based PPTX decks with the Parallel Digital standard template.

It keeps chapter divider pages native to the template and inserts generated full-slide PNG content pages by chapter.

## What It Does

- Uses `assets/parallel-digital-standard-template.pptx` as the base template.
- Reuses the template chapter page and only replaces its title/subtitle text.
- Inserts content pages as full-bleed 16:9 PNG images.
- Guides content images toward a blue-white enterprise technology style that adapts to the user's topic.
- Keeps Chinese text deterministic by rendering final slide text outside the image model.

## Project Structure

```text
avatarppt/
├── SKILL.md
├── assets/
│   └── parallel-digital-standard-template.pptx
├── references/
│   ├── image-style-guide.md
│   └── template-inventory.md
├── scripts/
│   └── assemble_deck.py
├── evals/
│   └── evals.json
└── manifest.example.json
```

## Assemble A Deck

Prepare full-slide PNG images first, then create a manifest:

```bash
python scripts/assemble_deck.py manifest.example.json
```

The script creates a PPTX with this order:

1. Cover page
2. Catalogue page
3. Chapter divider page
4. Content image slides
5. Closing page

Each chapter repeats steps 3-4.

## Notes

- Content images should be 16:9, ideally `2560x1440`.
- Chapter pages are not rasterized.
- The user-provided source template is copied into `assets/` so the project is self-contained.
