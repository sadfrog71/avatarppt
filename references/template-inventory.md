# Template Inventory

Template asset:

`assets/parallel-digital-standard-template.pptx`

Source analyzed from:

`/Users/mark.ma/Documents/08公司介绍/公司ppt模板/平行数字ppt模板（标准化） (1).pptx`

## Dimensions

- PPTX slide size: `12192000 x 6858000 EMU`
- Aspect ratio: 16:9
- Equivalent size: `13.333 x 7.5 in`

## Slides

Slides are listed 1-based for human use and 0-based for scripting.

- Slide 1 / index 0: Cover page.
  - Main text: `平行数字PPT模板`
  - Footer: `平行数字  交叉现实`
  - Dark blue-gray background with large cyan brand arc.

- Slide 2 / index 1: Catalogue page.
  - Text: `CATALOGUE`, `目录`, section names.
  - Default section placeholders: `第一节`, `第二节`, `第三节`, `第四节`.

- Slide 3 / index 2: Chapter divider page.
  - Use this as the reusable chapter page.
  - Replace text only.
  - Main title text box:
    - Shape name: `文本框 4`
    - Original text: `MAIN TITLE`
    - Position: `x=445135`, `y=1374140`, `w=10552430`, `h=2168525`
    - Text color: white
  - Subtitle text box:
    - Shape name: `文本框 5`
    - Original text: `内容标题`
    - Position: `x=508635`, `y=3352165`, `w=4189095`, `h=553085`
    - Text color: white
  - Footer:
    - Shape name: `文本框 6`
    - Original text: `平行数字  交叉现实`
    - Color: `#1DB5CD`

- Slide 4 / index 3: Simple title/content template page.
  - Text: `公司简介`
  - This skill normally does not use it because content pages are inserted as full-slide images.

- Slide 5 / index 4: Closing page.
  - Main text: `THANK   YOU`
  - Contact/address text and logo.

## Template Colors

- Deep template blue: `#005AAC`
- Template cyan: `#1DB5CD`
- Additional text/line blue: `#005D7F`
- Chapter/cover text: white on dark background

## Integration Rule

Keep chapter pages native to the template. Do not cover them with generated
images. Content-slide visuals can be full-slide images because their visual
content is intentionally rasterized. For new plans, keep the content title out
of the bitmap by default: reserve the top title zone and let the assembler add
an editable native title above the full-slide image. Use an image-rendered title
only when `title_render_mode=image` is explicitly declared.
