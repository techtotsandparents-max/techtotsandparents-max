"""
Convert a portrait photo into a CLEAN, colorful ASCII-art SVG
"""
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "avi-ascii.svg")

COLS = 240
ROWS = 120
CELL_W = 3.116
CELL_H = 6.233
RAMP = ".`:-=+*cs#%@"  # removed leading space! sparse -> dense

CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.0          
SHARPEN = True

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.11
STAGGER = 0.11

# 1. Grayscale for luminance
im = Image.open(SRC).convert("L")
if SHARPEN:
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

# 2. Color for tspans
color_im = Image.open(SRC.replace(".png", "-color.png")).convert("RGB")
color_im = color_im.resize((COLS, ROWS), Image.LANCZOS)
cpx = color_im.load()

# 3. Mask for explicit background removal
mask_im = Image.open(SRC.replace(".png", "-mask.png")).convert("L")
mask_im = mask_im.resize((COLS, ROWS), Image.LANCZOS)
mpx = mask_im.load()

STATIC = bool(os.environ.get("STATIC"))

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        # If it's background (mask is black/transparent), it MUST be a space
        if mpx[x, y] < 128:
            chars.append(" ")
            continue
            
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        
        # CRITICAL: cap luminance so face pixels NEVER produce invisible chars.
        # Without this, bright skin (forehead, nose, cheeks) maps to "." which
        # is invisible on the dark background, creating holes/blank spots.
        # Capping at 0.65 ensures the sparsest face char is "+" (clearly visible).
        lum = min(lum, 0.65)
        
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + PAD * 0.35

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">techtotsandparents-max@github: ~$ ./portrait.sh</text>')

font_size = CELL_H * 0.86
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    # build colored tspans
    tspan_parts = []
    current_color = None
    current_chars = []
    
    for x, char in enumerate(line):
        if char == " ":
            hex_c = INK
        else:
            r, g, b = cpx[x, ry]
            r = max(50, r)
            g = max(60, g)
            b = max(70, b)
            hex_c = f"#{r:02x}{g:02x}{b:02x}"
            
        if hex_c != current_color:
            if current_chars:
                tspan_parts.append(f'<tspan fill="{current_color}">{html.escape("".join(current_chars))}</tspan>')
            current_color = hex_c
            current_chars = [char]
        else:
            current_chars.append(char)
            
    if current_chars:
        tspan_parts.append(f'<tspan fill="{current_color}">{html.escape("".join(current_chars))}</tspan>')
        
    safe = "".join(tspan_parts)

    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'techtotsandparents-max@github:~$ whoami <tspan fill="{INK}">Rahul Tripathi</tspan></text>')
parts.append(f'<rect x="{PAD+227}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
