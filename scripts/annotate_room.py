#!/usr/bin/env python3
"""
Room Photo In-Situ Annotation Generator
Draws architectural callout lines, tags, and translucent storage info cards directly onto room photos.
"""

import sys
import os
import json
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    font_candidates = [
        '/Library/Fonts/Arial Unicode.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/PingFang.ttc'
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

def draw_callout_card(draw, x, y, title, items, tag, color_theme, target_pt, font_title, font_body, font_badge):
    tx, ty = target_pt
    # Line from target point to card
    draw.line([(tx, ty), (x + 20, y + 20)], fill=color_theme, width=3)
    draw.ellipse([tx-6, ty-6, tx+6, ty+6], fill=color_theme, outline=(255,255,255,255), width=2)
    
    card_w = 340
    card_h = 24 + len(items) * 22 + 20
    # Card background (translucent dark)
    draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=10, fill=(15, 23, 42, 230), outline=color_theme, width=2)
    
    # Tag
    draw.rounded_rectangle([x + 12, y + 10, x + 12 + 65, y + 32], radius=5, fill=color_theme)
    draw.text((x + 18, y + 12), tag, font=font_badge, fill=(255, 255, 255, 255))
    draw.text((x + 85, y + 10), title, font=font_title, fill=(255, 255, 255, 255))
    
    # Body lines
    for i, line in enumerate(items):
        draw.text((x + 14, y + 42 + i * 20), line, font=font_body, fill=(203, 213, 225, 255))

def annotate_photo(image_path, annotations, output_path, title_text="🔍 实景空间动线与收纳位点对点批注"):
    im = Image.open(image_path).convert('RGB')
    w, h = im.size
    
    overlay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    font_title = get_font(20)
    font_body = get_font(15)
    font_badge = get_font(13)
    
    # Top banner
    draw.rounded_rectangle([w//2 - 280, 20, w//2 + 280, 68], radius=12, fill=(15, 23, 42, 235), outline=(255,255,255,100), width=1)
    draw.text((w//2 - 240, 28), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    for ann in annotations:
        draw_callout_card(
            draw=draw,
            x=ann['x'],
            y=ann['y'],
            title=ann['title'],
            items=ann['items'],
            tag=ann.get('tag', '收纳位'),
            color_theme=tuple(ann.get('color', [59, 130, 246, 255])),
            target_pt=(ann['target_x'], ann['target_y']),
            font_title=font_title,
            font_body=font_body,
            font_badge=font_badge
        )
        
    final_im = Image.alpha_composite(im.convert('RGBA'), overlay).convert('RGB')
    final_im.save(output_path, quality=95)
    print(f"Annotated blueprint saved successfully to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: annotate_room.py <image_path> <annotations_json_path> <output_path>")
        sys.exit(1)
    
    img_in = sys.argv[1]
    json_in = sys.argv[2]
    img_out = sys.argv[3]
    
    with open(json_in, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    annotate_photo(img_in, data.get('annotations', []), img_out, data.get('title', '🔍 空间收纳设计点对点标注'))
