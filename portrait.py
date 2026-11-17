"""Turn a photo into dark_mode.svg / light_mode.svg ASCII portraits.
usage: python3 portrait.py photo.jpg [cols]
"""
import sys
from html import escape
from PIL import Image, ImageOps

RAMP = " .,:;'-~=+*!|/\\%#@"  # light -> dense
LINE, CHAR = 16, 8.4  # px per row / per column at font-size 14

def ascii_rows(path, cols=56):
    img = ImageOps.exif_transpose(Image.open(path)).convert("L")
    rows = round(img.height / img.width * cols * CHAR / LINE)
    img = ImageOps.autocontrast(img.resize((cols, rows)))
    px = img.tobytes()
    return ["".join(RAMP[(255 - p) * (len(RAMP) - 1) // 255] for p in px[r * cols:(r + 1) * cols]) for r in range(rows)]

def svg(rows, fg, bg, invert):
    if invert:  # dark bg: bright pixels should be dense
        rows = ["".join(RAMP[len(RAMP) - 1 - RAMP.index(c)] for c in r) for r in rows]
    w, h = round(len(rows[0]) * CHAR + 30), len(rows) * LINE + 30
    spans = "\n".join(f'<tspan x="15" y="{25 + i * LINE}">{escape(r)}</tspan>' for i, r in enumerate(rows))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="Consolas,Menlo,monospace" font-size="14px">\n'
            f'<style>text,tspan{{white-space:pre}}</style>\n<rect width="{w}" height="{h}" fill="{bg}" rx="12"/>\n'
            f'<text fill="{fg}">\n{spans}\n</text>\n</svg>\n')

if __name__ == "__main__":
    rows = ascii_rows(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 56)
    assert rows and all(len(r) == len(rows[0]) for r in rows)
    open("dark_mode.svg", "w").write(svg(rows, "#c9d1d9", "#0d1117", invert=True))
    open("light_mode.svg", "w").write(svg(rows, "#24292f", "#ffffff", invert=False))
    print(f"wrote {len(rows)} rows x {len(rows[0])} cols")
