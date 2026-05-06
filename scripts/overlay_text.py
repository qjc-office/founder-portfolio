#!/usr/bin/env python3
"""Composite hanja/text overlay onto a portrait via Pillow.

Default placement: top-right corner, small (Wallpaper-magazine tone — restrained,
not screaming).

Why Pillow not the AI model:
- AI image models (Flux, Imagen) cannot reliably render hanja / Korean glyphs.
- Pillow + Nanum Myeongjo guarantees pixel-perfect typography.
- Post-processing keeps sanity: AI generates the photo, code stamps the name.

Usage:
    overlay_text.py --source generated/editorial.png --text 鄭常綠 \\
        --position top-right --out generated/editorial_signed.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[overlay] missing Pillow; run scripts/bootstrap.sh", file=sys.stderr)
    sys.exit(2)


# Probed in order. First existing font wins.
FONT_CANDIDATES = [
    # macOS (Nanum if installed via Homebrew or manually)
    "/System/Library/Fonts/Supplemental/NanumMyeongjo.ttf",
    "/Library/Fonts/NanumMyeongjo.ttf",
    "/Library/Fonts/NanumMyeongjoBold.ttf",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleMyungjo.ttf",
    # Linux (Ubuntu/Debian fonts-nanum, fonts-noto-cjk)
    "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
    "/usr/share/fonts/opentype/source-han-serif/SourceHanSerifKR-Regular.otf",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]

# (x_fraction, y_fraction, Pillow text anchor).
# Pillow anchor: 'l/m/r' = left/middle/right horizontal,
#                't/m/b' = top/middle/baseline vertical.
POSITION_PRESETS: dict[str, tuple[float, float, str]] = {
    "top-right":    (0.94, 0.06, "rt"),  # Wallpaper magazine tone — small, restrained
    "bottom-left":  (0.06, 0.94, "lb"),  # 한국 사대부 톤 — anchored bottom
    "center":       (0.50, 0.50, "mm"),  # 인감 도장 풍 — centered watermark
    "top-left":     (0.06, 0.06, "lt"),
    "bottom-right": (0.94, 0.94, "rb"),
}


def find_font() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    raise FileNotFoundError(
        "No suitable Korean/CJK serif font found.\n"
        "  macOS:  brew install --cask font-nanum-myeongjo\n"
        "  Ubuntu: apt install fonts-nanum\n"
        "  Or set --font-path to a specific .ttf/.otf file."
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--source", type=Path, required=True, help="Source image path")
    p.add_argument("--text", required=True, help="Text to overlay (e.g. '鄭常綠')")
    p.add_argument(
        "--position",
        default="top-right",
        choices=list(POSITION_PRESETS),
        help="Placement preset (default: top-right — Wallpaper magazine tone)",
    )
    p.add_argument(
        "--font-size",
        type=int,
        default=0,
        help="Font size in px (0 = auto, derives image_height // 18)",
    )
    p.add_argument(
        "--color",
        default="#9F0824",
        help="Text color (default: 朱印 red #9F0824)",
    )
    p.add_argument(
        "--font-path",
        default=None,
        help="Override auto-detected font with specific .ttf/.otf path",
    )
    p.add_argument(
        "--padding",
        type=float,
        default=0.0,
        help="Outer padding fraction (0..0.1) added inward from --position anchor",
    )
    p.add_argument("--out", type=Path, required=True, help="Output image path")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.source.exists():
        print(f"[overlay] ERROR: source not found: {args.source}", file=sys.stderr)
        return 2

    img = Image.open(args.source).convert("RGBA")
    w, h = img.size
    fx, fy, anchor = POSITION_PRESETS[args.position]

    # Apply optional inner padding (push the anchor away from the edge).
    if args.padding > 0:
        if anchor[0] == "l": fx += args.padding
        elif anchor[0] == "r": fx -= args.padding
        if anchor[1] == "t": fy += args.padding
        elif anchor[1] == "b": fy -= args.padding

    x, y = int(w * fx), int(h * fy)

    font_size = args.font_size if args.font_size > 0 else max(24, h // 18)
    try:
        font_path = args.font_path or find_font()
    except FileNotFoundError as e:
        print(f"[overlay] ERROR: {e}", file=sys.stderr)
        return 2
    font = ImageFont.truetype(font_path, font_size)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.text((x, y), args.text, font=font, fill=args.color, anchor=anchor)

    composed = Image.alpha_composite(img, overlay).convert("RGB")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    composed.save(args.out, quality=95)
    size_kb = args.out.stat().st_size // 1024
    print(f"✓ Overlay saved: {args.out} ({size_kb} KB, "
          f"text='{args.text}', position={args.position}, font_size={font_size})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
