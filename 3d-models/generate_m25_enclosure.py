#!/usr/bin/env python3
"""Generate a project enclosure (base + lid) built around M2.5 heat-set inserts.

Features, all printable without supports:
- four corner bosses, Ø3.5 x 7.5 mm chamfered insert holes (M2.5 x 6 or 8 screws)
- four PCB standoffs with chamfered insert holes (M2.5 x 6 only — 8 bottoms out)
- vent slots in both long walls
- U-shaped cable port in one end wall, closed off by the lid
- wall-mount ears with countersunk holes for #6 / M3.5 wood screws
- lid with registration lip (interrupted at the bosses and the cable port)
  and counterbored screw holes

Insert holes are Ø3.5 per the PETG test coupon results.
Requires: pip install numpy trimesh manifold3d shapely
"""

import numpy as np
import trimesh
from shapely.geometry import box as rect
from trimesh.creation import box, cone, cylinder, extrude_polygon

# ---- overall (mm) -----------------------------------------------------
BOX_L, BOX_W, BOX_H = 80.0, 50.0, 30.0   # external, lid included
WALL = 2.0
FLOOR = 2.0
LID_T = 2.2
CORNER_R = 3.0

# ---- inserts / screws -------------------------------------------------
INSERT_HOLE_D = 3.5
INSERT_HOLE_DEPTH = 7.5   # corner bosses: fits 6 or 8 mm screws
CHAMFER = 0.6
BOSS_D = 8.0
BOSS_INSET = 5.0

# ---- PCB standoffs ----------------------------------------------------
STANDOFF_D = 7.0
STANDOFF_H = 5.0          # PCB floats 5 mm above the floor
STANDOFF_HOLE_DEPTH = 5.5 # 4 mm insert + tip room for a 6 mm screw (not 8!)
PCB_PATTERN_L = 56.0      # mounting hole pattern, centered in the cavity
PCB_PATTERN_W = 26.0

# ---- vents ------------------------------------------------------------
VENT_N = 6
VENT_W = 2.0
VENT_PITCH = 6.0
VENT_Z0, VENT_Z1 = 8.0, 22.0

# ---- cable port (in the x = BOX_L end wall) ---------------------------
PORT_W = 12.0             # semicircle-bottomed U, cut from the wall top
PORT_DEPTH = 8.0

# ---- lid --------------------------------------------------------------
SCREW_CLEAR_D = 2.8
CBORE_D = 5.2
CBORE_DEPTH = 1.0
LIP_H = 1.5
LIP_W = 1.2
LIP_CLEAR = 0.25
BOSS_CLEAR = 0.3

# ---- mount ears -------------------------------------------------------
EAR_L = 10.0              # how far each ear sticks out
EAR_W = 14.0
EAR_T = 3.0
EAR_HOLE_D = 4.2
EAR_CSK_D = 8.4           # 45-degree countersink for a flat-head screw

SECTIONS = 96
WALL_TOP = BOX_H - LID_T
SCREW_XY = [
    (BOSS_INSET, BOSS_INSET),
    (BOX_L - BOSS_INSET, BOSS_INSET),
    (BOX_L - BOSS_INSET, BOX_W - BOSS_INSET),
    (BOSS_INSET, BOX_W - BOSS_INSET),
]
STANDOFF_XY = [
    ((BOX_L - PCB_PATTERN_L) / 2, (BOX_W - PCB_PATTERN_W) / 2),
    ((BOX_L + PCB_PATTERN_L) / 2, (BOX_W - PCB_PATTERN_W) / 2),
    ((BOX_L + PCB_PATTERN_L) / 2, (BOX_W + PCB_PATTERN_W) / 2),
    ((BOX_L - PCB_PATTERN_L) / 2, (BOX_W + PCB_PATTERN_W) / 2),
]


def rounded_rect(x0, y0, x1, y1, r):
    return rect(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=32)


def insert_hole(x, y, top, depth):
    """Chamfered insert hole cutters at (x, y), entry at z=top."""
    h = cylinder(radius=INSERT_HOLE_D / 2, height=depth + 0.2, sections=SECTIONS)
    h.apply_translation((x, y, top - depth / 2 + 0.1))
    r = INSERT_HOLE_D / 2 + CHAMFER + 0.5
    ch = cone(radius=r, height=r, sections=SECTIONS)
    ch.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
    ch.apply_translation((x, y, top + 0.5))
    return [h, ch]


def make_base():
    solids = [extrude_polygon(rounded_rect(0, 0, BOX_L, BOX_W, CORNER_R), WALL_TOP)]

    # mount ears, print flat on the bed
    for x0, x1 in ((-EAR_L, CORNER_R + 1), (BOX_L - CORNER_R - 1, BOX_L + EAR_L)):
        ear = extrude_polygon(
            rounded_rect(x0, (BOX_W - EAR_W) / 2, x1, (BOX_W + EAR_W) / 2, 2.5), EAR_T)
        solids.append(ear)

    # carve the cavity out of the shell FIRST, then add bosses/standoffs —
    # the other order would mow them down with the cavity cut
    cavity = extrude_polygon(
        rounded_rect(WALL, WALL, BOX_L - WALL, BOX_W - WALL, CORNER_R - 1), WALL_TOP)
    cavity.apply_translation((0, 0, FLOOR))
    shell = trimesh.boolean.union(solids, engine="manifold")
    shell = trimesh.boolean.difference([shell, cavity], engine="manifold")

    posts = []
    for x, y in SCREW_XY:
        b = cylinder(radius=BOSS_D / 2, height=WALL_TOP - FLOOR, sections=SECTIONS)
        b.apply_translation((x, y, FLOOR + (WALL_TOP - FLOOR) / 2))
        posts.append(b)
    for x, y in STANDOFF_XY:
        s = cylinder(radius=STANDOFF_D / 2, height=STANDOFF_H + FLOOR, sections=SECTIONS)
        s.apply_translation((x, y, (STANDOFF_H + FLOOR) / 2))
        posts.append(s)
    base = trimesh.boolean.union([shell] + posts, engine="manifold")

    cutters = []

    for x, y in SCREW_XY:
        cutters += insert_hole(x, y, WALL_TOP, INSERT_HOLE_DEPTH)
    for x, y in STANDOFF_XY:
        cutters += insert_hole(x, y, FLOOR + STANDOFF_H, STANDOFF_HOLE_DEPTH)

    # vent slots through both long walls
    x_first = BOX_L / 2 - (VENT_N - 1) * VENT_PITCH / 2
    for i in range(VENT_N):
        v = box(extents=(VENT_W, BOX_W + 2, VENT_Z1 - VENT_Z0))
        v.apply_translation((x_first + i * VENT_PITCH, BOX_W / 2,
                             (VENT_Z0 + VENT_Z1) / 2))
        cutters.append(v)

    # cable port: rectangle from the wall top + semicircular bottom
    pr = PORT_W / 2
    p = box(extents=(WALL + 2, PORT_W, PORT_DEPTH - pr + 1))
    p.apply_translation((BOX_L - WALL / 2, BOX_W / 2,
                         WALL_TOP - (PORT_DEPTH - pr) / 2 + 0.5))
    cutters.append(p)
    c = cylinder(radius=pr, height=WALL + 2, sections=SECTIONS)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    c.apply_translation((BOX_L - WALL / 2, BOX_W / 2, WALL_TOP - PORT_DEPTH + pr))
    cutters.append(c)

    # ear holes with 45-degree countersinks
    for ex in (-EAR_L / 2, BOX_L + EAR_L / 2):
        h = cylinder(radius=EAR_HOLE_D / 2, height=EAR_T + 2, sections=SECTIONS)
        h.apply_translation((ex, BOX_W / 2, EAR_T / 2))
        cutters.append(h)
        r = EAR_CSK_D / 2 + 0.5
        cs = cone(radius=r, height=r, sections=SECTIONS)
        cs.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
        cs.apply_translation((ex, BOX_W / 2, EAR_T + 0.5))
        cutters.append(cs)

    return trimesh.boolean.difference([base] + cutters, engine="manifold")


def make_lid():
    plate = extrude_polygon(rounded_rect(0, 0, BOX_L, BOX_W, CORNER_R), LID_T)
    plate.apply_translation((0, 0, LIP_H))

    outer = rounded_rect(WALL + LIP_CLEAR, WALL + LIP_CLEAR,
                         BOX_L - WALL - LIP_CLEAR, BOX_W - WALL - LIP_CLEAR,
                         CORNER_R - 1 - LIP_CLEAR)
    ring = outer.difference(outer.buffer(-LIP_W))
    lip = extrude_polygon(ring, LIP_H + 0.1)

    cutters = []
    top = LIP_H + LID_T
    for x, y in SCREW_XY:
        h = cylinder(radius=SCREW_CLEAR_D / 2, height=top + 2, sections=SECTIONS)
        h.apply_translation((x, y, top / 2))
        cutters.append(h)
        cb = cylinder(radius=CBORE_D / 2, height=CBORE_DEPTH + 0.2, sections=SECTIONS)
        cb.apply_translation((x, y, top - CBORE_DEPTH / 2 + 0.1))
        cutters.append(cb)
        bc = cylinder(radius=BOSS_D / 2 + BOSS_CLEAR, height=LIP_H + 1,
                      sections=SECTIONS)
        bc.apply_translation((x, y, (LIP_H - 1) / 2))
        cutters.append(bc)

    # interrupt the lip across the cable port so cables get the full opening
    pc = box(extents=(2 * LIP_CLEAR + LIP_W + 1, PORT_W, LIP_H + 1))
    pc.apply_translation((BOX_L - WALL - (LIP_CLEAR + LIP_W + 1) / 2 + 0.5,
                          BOX_W / 2, (LIP_H - 1) / 2))
    cutters.append(pc)

    lid = trimesh.boolean.union([plate, lip], engine="manifold")
    return trimesh.boolean.difference([lid] + cutters, engine="manifold")


def main():
    for name, mesh in (("enclosure-base", make_base()),
                       ("enclosure-lid", make_lid())):
        print(f"{name}: watertight={mesh.is_watertight}, "
              f"volume={mesh.volume / 1000:.1f} cm^3, "
              f"bounds={np.round(mesh.bounds, 2).tolist()}")
        mesh.export(f"{name}.stl")
        print(f"wrote {name}.stl")


if __name__ == "__main__":
    main()
