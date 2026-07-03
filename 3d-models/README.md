# M2.5 heat-set insert test coupon

A small block (68 × 16 × 8 mm, ~8 g of filament) with five through-holes in
different diameters — **3.2, 3.4, 3.5, 3.6, 3.8 mm** — each labeled next to
the hole. Press an M2.5 insert into each and find the size that grips best.
Typical starting point for M2.5 brass inserts is **3.4–3.6 mm**, but it varies
with insert brand, printer, and material.

## Files

- `m25-insert-test.stl` — ready to slice and print
- `m25-insert-test.scad` — editable OpenSCAD source (change diameters/sizes here)
- `generate_m25_insert_test.py` — Python generator that produced the STL
  (`pip install numpy trimesh manifold3d`, then run it)

## Printing

- Print flat, labels up. No supports needed.
- 3–4 perimeters/walls recommended so the insert grips plastic, not infill.
- Any common material works; PETG/ABS take heat a bit better than PLA.

## Using it

1. Set your soldering iron to ~200–230 °C (PLA) / ~230–250 °C (PETG), ideally
   with an insert tip.
2. Rest the insert in the chamfered hole, press slowly and straight down until
   flush. Let it cool before loading it.
3. Thread in an M2.5 screw and try to pull it out / torque it. The best hole
   size seats with light steady pressure and doesn't spin under torque.
