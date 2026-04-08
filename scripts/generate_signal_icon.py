#!/usr/bin/env python3
"""
Generate signal unit icon PNG from SVG coordinates.
SVG: viewBox="21 46 158 108" — blue rectangle + signal decorator path.
Output: signal_unit.png (96x96, transparent background)
"""

from PIL import Image, ImageDraw

# Target canvas
W, H = 48, 48
PADDING = 4

# SVG coordinate space
SVG_X, SVG_Y, SVG_W, SVG_H = 21, 46, 158, 108

# Scale to fit with padding
scale = min((W - PADDING * 2) / SVG_W, (H - PADDING * 2) / SVG_H)
scaled_w = SVG_W * scale
scaled_h = SVG_H * scale
x_off = (W - scaled_w) / 2
y_off = (H - scaled_h) / 2

def tx(sx):
    return (sx - SVG_X) * scale + x_off

def ty(sy):
    return (sy - SVG_Y) * scale + y_off

# SVG rectangle: M25,50 l150,0 0,100 -150,0 z
rect = [tx(25), ty(50), tx(175), ty(150)]

# SVG decorator: M25,50 100,110 100,90 175,150
deco = [(tx(25), ty(50)), (tx(100), ty(110)), (tx(100), ty(90)), (tx(175), ty(150))]

stroke_w = max(2, int(4 * scale))

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Fill rectangle
draw.rectangle(rect, fill=(128, 224, 255, 255))

# Rectangle border
draw.rectangle(rect, outline=(0, 0, 0, 255), width=stroke_w)

# Decorator path (no fill, black stroke)
draw.line(deco, fill=(0, 0, 0, 255), width=stroke_w)

img.save("signal_unit.png")
print("Generated: signal_unit.png (48x48)")
