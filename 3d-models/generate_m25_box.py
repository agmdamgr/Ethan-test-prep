#!/usr/bin/env python3
"""Generate a simple screw-together box (base + lid) for M2.5 heat-set inserts.

Base has four corner bosses with 3.5 mm holes (the winner from the insert
test coupon) sized for 4 mm long M2.5 inserts. Lid is a flat plate with
clearance holes and shallow counterbores. Use M2.5 x 6 screws (8 mm also
fits; 12 mm will bottom out).

Requires: pip install numpy trimesh manifold3d shapely
"""

import numpy as np
import trimesh
from shapely.geometry import box as rect
from trimesh.creation import cone, cylinder, extrude_polygon

# ---- parameters (mm) -------------------------------------------------
BOX_L, BOX_W, BOX_H = 60.0, 40.0, 25.0   # external size, lid included
WALL = 2.0
FLOOR = 2.0
LID_T = 2.2
CORNER_R = 3.0

INSERT_HOLE_D = 3.5      # from the test coupon: 3.4-3.6 good, 3.5 = sweet spot
INSERT_HOLE_DEPTH = 7.5  # 4 mm insert + room for a 6 or 8 mm screw tip
BOSS_D = 8.0
BOSS_INSET = 5.0         # boss/screw center from each outer corner

CHAMFER = 0.6            # radial entry chamfer, same as the test coupon

SCREW_CLEAR_D = 2.8
CBORE_D = 5.2
CBORE_DEPTH = 1.0

SECTIONS = 96

WALL_TOP = BOX_H - LID_T
SCREW_XY = [
    (BOSS_INSET, BOSS_INSET),
    (BOX_L - BOSS_INSET, BOSS_INSET),
    (BOX_L - BOSS_INSET, BOX_W - BOSS_INSET),
    (BOSS_INSET, BOX_W - BOSS_INSET),
]


def rounded_rect(x0, y0, x1, y1, r):
    return rect(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=32)


def make_base():
    outer = extrude_polygon(rounded_rect(0, 0, BOX_L, BOX_W, CORNER_R), WALL_TOP)

    cavity = extrude_polygon(
        rounded_rect(WALL, WALL, BOX_L - WALL, BOX_W - WALL, CORNER_R - 1), WALL_TOP)
    cavity.apply_translation((0, 0, FLOOR))

    bosses = []
    for x, y in SCREW_XY:
        b = cylinder(radius=BOSS_D / 2, height=WALL_TOP - FLOOR, sections=SECTIONS)
        b.apply_translation((x, y, FLOOR + (WALL_TOP - FLOOR) / 2))
        bosses.append(b)

    holes = []
    for x, y in SCREW_XY:
        h = cylinder(radius=INSERT_HOLE_D / 2, height=INSERT_HOLE_DEPTH + 0.2,
                     sections=SECTIONS)
        h.apply_translation((x, y, WALL_TOP - INSERT_HOLE_DEPTH / 2 + 0.1))
        holes.append(h)
        # 45-degree entry chamfer: cone base above the boss top, apex down
        r = INSERT_HOLE_D / 2 + CHAMFER + 0.5
        ch = cone(radius=r, height=r, sections=SECTIONS)
        ch.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
        ch.apply_translation((x, y, WALL_TOP + 0.5))
        holes.append(ch)

    shell = trimesh.boolean.difference([outer, cavity], engine="manifold")
    base = trimesh.boolean.union([shell] + bosses, engine="manifold")
    return trimesh.boolean.difference([base] + holes, engine="manifold")


def make_lid():
    plate = extrude_polygon(rounded_rect(0, 0, BOX_L, BOX_W, CORNER_R), LID_T)
    cutters = []
    for x, y in SCREW_XY:
        h = cylinder(radius=SCREW_CLEAR_D / 2, height=LID_T + 2, sections=SECTIONS)
        h.apply_translation((x, y, LID_T / 2))
        cutters.append(h)
        cb = cylinder(radius=CBORE_D / 2, height=CBORE_DEPTH + 0.2, sections=SECTIONS)
        cb.apply_translation((x, y, LID_T - CBORE_DEPTH / 2 + 0.1))
        cutters.append(cb)
    return trimesh.boolean.difference([plate] + cutters, engine="manifold")


def main():
    for name, mesh in (("box-base", make_base()), ("box-lid", make_lid())):
        print(f"{name}: watertight={mesh.is_watertight}, "
              f"volume={mesh.volume / 1000:.1f} cm^3, "
              f"bounds={np.round(mesh.bounds, 2).tolist()}")
        mesh.export(f"{name}.stl")
        print(f"wrote {name}.stl")


if __name__ == "__main__":
    main()
