"""
Prepare a portrait photo for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. boost LOCAL contrast (CLAHE) so a flatly-lit face gains highlights and
     shadows -- this is what turns a dark blob into a recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py <input.jpg> [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# Pad image to a square with a 15% margin to ensure the face doesn't touch the edges
img = Image.open(INP).convert("RGBA")
w, h = img.size
new_dim = int(max(w, h) * 1.15)
padded = Image.new("RGBA", (new_dim, new_dim), (0, 0, 0, 0))
padded.paste(img, ((new_dim - w) // 2, (new_dim - h) // 2))

# 1. cut out the subject
cut = remove(padded)
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])                 # 0 = background

# 2. local-contrast the luminance (CLAHE)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
# Use a gentler CLAHE so we don't blow out the bright new photo
clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
gray = clahe.apply(gray)
# Remove the extreme global lift so facial features (eyes/beard) stay dark and visible
gray = cv2.convertScaleAbs(gray, alpha=1.0, beta=5)

# 3. paste onto white using the alpha mask (feathered a hair to avoid a halo)
mask = (alpha.astype(np.float32) / 255.0)

# Fill any holes in the mask (e.g. bright spots that the AI mistakenly removed)
mask_uint8 = (mask * 255).astype(np.uint8)

# Use a morphological close to ensure small gaps are filled, then find contours
kernel = np.ones((5, 5), np.uint8)
mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel)
contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(mask_uint8, contours, -1, 255, -1)
mask = mask_uint8.astype(np.float32) / 255.0

# apply the CLAHE enhanced luminance back to the color image
gray_norm = gray.astype(np.float32) / 255.0
# Retain at least 70% of the original color brightness even in deep shadows
enhanced_rgb = rgb.astype(np.float32) * (gray_norm[:, :, None] * 0.5 + 0.7)
enhanced_rgb = np.clip(enhanced_rgb, 0, 255).astype(np.uint8)

# save color version on dark background
bg_color = np.array([13, 17, 23], dtype=np.float32)
mask_3d = mask[:, :, None]
out_color = enhanced_rgb.astype(np.float32) * mask_3d + bg_color * (1.0 - mask_3d)
out_color = np.clip(out_color, 0, 255).astype(np.uint8)
Image.fromarray(out_color, mode="RGB").save(OUT.replace(".png", "-color.png"))

mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
out = np.clip(out, 0, 255).astype(np.uint8)

Image.fromarray(out, mode="L").save(OUT)
Image.fromarray((mask * 255).astype(np.uint8), mode="L").save(OUT.replace(".png", "-mask.png"))
print("wrote", OUT, out.shape)
