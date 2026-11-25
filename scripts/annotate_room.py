#!/usr/bin/env python3
"""
Room Photo In-Situ Annotation Generator (v2.0)
Draws architectural callout lines, tags, and translucent storage info cards directly onto room photos.
Includes auto-clamping to image boundaries and smart anchor attachment so lines never cross text.
"""

import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont


def get_font(size):
    font_candidates = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size, index=0)
            except Exception:
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    continue
    return ImageFont.load_default()


def nearest_card_edge(tx, ty, x, y, w, h):
    """Attach callout line to the closest side midpoint of the card so line never crosses card."""
    candidates = [
        (x, y + h // 2),          # left middle
        (x + w, y + h // 2),      # right middle
        (x + w // 2, y),          # top middle
        (x + w // 2, y + h),      # bottom middle
    ]
    return min(candidates, key=lambda pt: (pt[0] - tx) ** 2 + (pt[1] - ty) ** 2)


def draw_callout_card(draw, img_w, img_h, ann, font_title, font_body, font_badge):
    tx, ty = int(ann["target_x"]), int(ann["target_y"])
    items = ann.get("items", [])
    title = ann["title"]
    tag = ann.get("tag", "收纳位")
    color_theme = tuple(ann.get("color", [59, 130, 246, 255]))

    card_w = min(350, max(240, int(img_w * 0.28)))
    card_h = 48 + len(items) * 21 + 12

    # Clamp coordinates strictly inside canvas margins (keeping top banner clear)
    x = max(16, min(img_w - card_w - 16, int(ann["x"])))
    y = max(84, min(img_h - card_h - 16, int(ann["y"])))

    ax, ay = nearest_card_edge(tx, ty, x, y, card_w, card_h)
    draw.line([(tx, ty), (ax, ay)], fill=color_theme, width=3)
    draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=color_theme, outline=(255, 255, 255, 255), width=2)

    draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=10, fill=(15, 23, 42, 232), outline=color_theme, width=2)
    draw.rounded_rectangle([x + 12, y + 10, x + 78, y + 32], radius=5, fill=color_theme)
    draw.text((x + 18, y + 12), tag, font=font_badge, fill=(255, 255, 255, 255))
    draw.text((x + 86, y + 10), title, font=font_title, fill=(255, 255, 255, 255))

    for i, line in enumerate(items):
        draw.text((x + 14, y + 42 + i * 21), line, font=font_body, fill=(203, 213, 225, 255))


def annotate_photo(image_path, annotations, output_path, title_text="🔍 实景空间动线与收纳位点对点批注"):
    im = Image.open(image_path).convert("RGB")
    w, h = im.size

    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    scale = max(0.85, min(1.4, w / 1280.0))
    font_title = get_font(int(18 * scale))
    font_body = get_font(int(14 * scale))
    font_badge = get_font(int(12 * scale))

    banner_w = min(w - 32, int(580 * scale))
    bx0 = (w - banner_w) // 2
    draw.rounded_rectangle([bx0, 18, bx0 + banner_w, 66], radius=12, fill=(15, 23, 42, 235), outline=(255, 255, 255, 110), width=1)
    draw.text((bx0 + 24, 28), title_text, font=font_title, fill=(255, 255, 255, 255))

    for ann in annotations:
        draw_callout_card(draw, w, h, ann, font_title, font_body, font_badge)

    final_im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final_im.save(output_path, quality=95)
    print(f"Annotated blueprint saved successfully to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: annotate_room.py <image_path> <annotations_json_path> <output_path>")
        sys.exit(1)

    with open(sys.argv[2], "r", encoding="utf-8") as f:
        data = json.load(f)

    annotate_photo(sys.argv[1], data.get("annotations", []), sys.argv[3], data.get("title", "🔍 空间收纳设计点对点标注"))
