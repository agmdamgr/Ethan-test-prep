#!/usr/bin/env python3
"""Generate an M2.5 heat-set insert test coupon as an STL.

A small block with a row of through-holes in several diameters so you can
find which hole size grips your inserts best. Each hole gets a 45-degree
chamfer on top (helps the insert start straight) and its diameter engraved
next to it as 7-segment digits.

Requires: pip install numpy trimesh manifold3d
"""

import numpy as np
import trimesh
from trimesh.creation import box, cylinder, cone

# ---- parameters (mm) -------------------------------------------------
HOLE_DIAMETERS = [3.2, 3.4, 3.5, 3.6, 3.8]  # typical M2.5 insert hole ~3.4-3.6
HOLE_SPACING = 13.0
BLOCK_THICKNESS = 8.0          # deeper than a standard 5.7 mm long insert
BLOCK_WIDTH = 16.0
MARGIN = 8.0                   # block edge to first/last hole center
CHAMFER = 0.6                  # radial chamfer at hole entry
ENGRAVE_DEPTH = 0.5
DIGIT_W, DIGIT_H, SEG_T = 2.2, 4.0, 0.6
SECTIONS = 96                  # cylinder facets

BLOCK_LENGTH = (len(HOLE_DIAMETERS) - 1) * HOLE_SPACING + 2 * MARGIN
TOP = BLOCK_THICKNESS

# 7-segment layout: a top, b top-right, c bottom-right, d bottom,
# e bottom-left, f top-left, g middle
SEGMENTS = {
    "a": ((DIGIT_W / 2, DIGIT_H - SEG_T / 2), (DIGIT_W, SEG_T)),
    "d": ((DIGIT_W / 2, SEG_T / 2), (DIGIT_W, SEG_T)),
    "g": ((DIGIT_W / 2, DIGIT_H / 2), (DIGIT_W, SEG_T)),
    "f": ((SEG_T / 2, DIGIT_H * 0.75), (SEG_T, DIGIT_H / 2)),
    "e": ((SEG_T / 2, DIGIT_H * 0.25), (SEG_T, DIGIT_H / 2)),
    "b": ((DIGIT_W - SEG_T / 2, DIGIT_H * 0.75), (SEG_T, DIGIT_H / 2)),
    "c": ((DIGIT_W - SEG_T / 2, DIGIT_H * 0.25), (SEG_T, DIGIT_H / 2)),
}
DIGITS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcfgd",
}


def engrave_box(cx, cy, sx, sy):
    """Box sunk ENGRAVE_DEPTH into the top surface at (cx, cy)."""
    b = box(extents=(sx, sy, ENGRAVE_DEPTH + 0.2))
    b.apply_translation((cx, cy, TOP - ENGRAVE_DEPTH / 2 + 0.1))
    return b


def label_cutters(text, cx, cy):
    """7-segment engraving for `text` (digits and '.'), centered at (cx, cy)."""
    dot = SEG_T * 1.2
    widths = [dot if ch == "." else DIGIT_W for ch in text]
    gap = 0.8
    total = sum(widths) + gap * (len(text) - 1)
    x = cx - total / 2
    cutters = []
    for ch, w in zip(text, widths):
        if ch == ".":
            cutters.append(engrave_box(x + w / 2, cy - DIGIT_H / 2 + dot / 2, dot, dot))
        else:
            for seg in DIGITS[ch]:
                (sx_c, sy_c), (sx, sy) = SEGMENTS[seg]
                cutters.append(engrave_box(x + sx_c, cy + sy_c - DIGIT_H / 2, sx, sy))
        x += w + gap
    return cutters


def main():
    block = box(extents=(BLOCK_LENGTH, BLOCK_WIDTH, BLOCK_THICKNESS))
    block.apply_translation((BLOCK_LENGTH / 2, BLOCK_WIDTH / 2, BLOCK_THICKNESS / 2))

    hole_y = BLOCK_WIDTH - 5.5
    label_y = 4.0
    cutters = []
    for i, d in enumerate(HOLE_DIAMETERS):
        cx = MARGIN + i * HOLE_SPACING
        hole = cylinder(radius=d / 2, height=BLOCK_THICKNESS + 2, sections=SECTIONS)
        hole.apply_translation((cx, hole_y, BLOCK_THICKNESS / 2))
        cutters.append(hole)

        # 45-degree entry chamfer: cone base above the top surface, apex down
        r = d / 2 + CHAMFER + 0.5
        ch = cone(radius=r, height=r, sections=SECTIONS)
        ch.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
        ch.apply_translation((cx, hole_y, TOP + 0.5))
        cutters.append(ch)

        cutters.extend(label_cutters(f"{d:.1f}", cx, label_y))

    # first mesh minus the union of the rest
    result = trimesh.boolean.difference([block] + cutters, engine="manifold")
    print(f"watertight: {result.is_watertight}, volume: {result.volume / 1000:.1f} cm^3")
    print(f"bounds (mm): {np.round(result.bounds, 2).tolist()}")
    out = "m25-insert-test.stl"
    result.export(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
