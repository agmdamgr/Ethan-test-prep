# M2.5 heat-set insert models

## Test coupon

A small block (68 × 16 × 8 mm, ~8 g of filament) with five through-holes in
different diameters — **3.2, 3.4, 3.5, 3.6, 3.8 mm** — each labeled next to
the hole. Press an M2.5 insert into each and find the size that grips best.

### Test results (2026-07-03, PLA)

| Hole  | Result                                     |
| ----- | ------------------------------------------ |
| 3.2   | Too tight (even though the insert package calls for 3.2) |
| 3.4–3.6 | Good grip                                 |
| 3.8   | Falls straight through                     |

**Use Ø3.5 mm** in CAD for this printer/filament combo — middle of the
working range, so print-to-print variation won't push it off either cliff.
The package's 3.2 spec assumes an exactly-sized (machined) hole; FDM
printers typically print holes 0.1–0.2 mm undersized, which is why the
modeled 3.4–3.6 holes land on spec. Re-test if switching material or
putting inserts in vertical walls.

### Files

- `m25-insert-test.stl` — ready to slice and print
- `m25-insert-test.scad` — editable OpenSCAD source (change diameters/sizes here)
- `generate_m25_insert_test.py` — Python generator that produced the STL
  (`pip install numpy trimesh manifold3d`, then run it)

## Screw-together box

Simple 60 × 40 × 25 mm box: base with four Ø8 mm corner bosses (Ø3.5 mm ×
7.5 mm deep insert holes, sized for 4 mm long M2.5 inserts) and a flat
2.2 mm lid with counterbored clearance holes.

- **Screws: M2.5 × 6 mm recommended** (~4.8 mm of engagement — full insert
  depth plus tip clearance). 8 mm also fits. 12 mm bottoms out — don't.
- Set inserts flush with the boss tops before first assembly.

### Files

- `box-base.stl`, `box-lid.stl` — ready to slice and print
- `m25-box.scad` — editable OpenSCAD source; set `part = "base"` or `"lid"`
- `generate_m25_box.py` — Python generator that produced the STLs
  (`pip install numpy trimesh manifold3d shapely`)

### Printing

- Both parts print flat, no supports (base open side up, lid counterbores up).
- 3–4 walls so bosses are solid plastic where the inserts grip.

## Setting inserts

1. Iron at ~200–230 °C (PLA) / ~230–250 °C (PETG), ideally with an insert tip.
2. Rest the insert in the chamfered hole, press slowly and straight down
   until flush. Let it cool before loading it.
3. Best fit seats with light steady pressure and doesn't spin under torque.
