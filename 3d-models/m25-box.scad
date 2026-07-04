// Simple screw-together box for M2.5 heat-set inserts (4 mm long)
// Base has four corner bosses with 3.5 mm insert holes (winner from the
// insert test coupon). Lid is a flat counterbored plate.
// Screws: M2.5 x 6 recommended, 8 mm also fits, 12 mm bottoms out.
//
// Render the base:  part = "base";
// Render the lid:   part = "lid";

part = "base"; // [base, lid]

box_l = 60; box_w = 40; box_h = 25; // external, lid included
wall = 2;
floor_t = 2;
lid_t = 2.2;
corner_r = 3;

insert_hole_d = 3.5;   // from test coupon: 3.4-3.6 good, 3.5 = sweet spot
insert_hole_depth = 7.5; // 4 mm insert + tip room for 6 or 8 mm screws
boss_d = 8;
boss_inset = 5;        // screw center from each outer corner

chamfer = 0.6;         // radial entry chamfer, same as the test coupon

screw_clear_d = 2.8;
cbore_d = 5.2;
cbore_depth = 1.0;

lip_h = 1.5;      // registration lip on lid underside, nests into the cavity
lip_w = 1.2;
lip_clear = 0.25; // per-side gap to the cavity wall
boss_clear = 0.3; // lip cutout gap around each boss

wall_top = box_h - lid_t;
screw_xy = [[boss_inset, boss_inset],
            [box_l - boss_inset, boss_inset],
            [box_l - boss_inset, box_w - boss_inset],
            [boss_inset, box_w - boss_inset]];
$fn = 96;

module rounded_rect(l, w, r) {
    offset(r = r) square([l - 2 * r, w - 2 * r], center = false);
}

module base() {
    difference() {
        union() {
            // shell
            difference() {
                linear_extrude(wall_top)
                    translate([corner_r, corner_r]) rounded_rect(box_l, box_w, corner_r);
                translate([0, 0, floor_t])
                    linear_extrude(wall_top)
                        translate([wall + corner_r - 1, wall + corner_r - 1])
                            rounded_rect(box_l - 2 * wall, box_w - 2 * wall, corner_r - 1);
            }
            // corner bosses
            for (p = screw_xy)
                translate([p[0], p[1], floor_t])
                    cylinder(d = boss_d, h = wall_top - floor_t);
        }
        // insert holes with 45-degree entry chamfer
        for (p = screw_xy) {
            translate([p[0], p[1], wall_top - insert_hole_depth])
                cylinder(d = insert_hole_d, h = insert_hole_depth + 1);
            translate([p[0], p[1], wall_top - chamfer])
                cylinder(d1 = insert_hole_d,
                         d2 = insert_hole_d + 2 * chamfer + 0.02, h = chamfer + 0.01);
        }
    }
}

module lid() {
    lip_l = box_l - 2 * (wall + lip_clear);
    lip_ww = box_w - 2 * (wall + lip_clear);
    lip_r = corner_r - 1 - lip_clear;
    difference() {
        union() {
            // plate on top of the lip: lip z 0..lip_h, plate above
            translate([0, 0, lip_h])
                linear_extrude(lid_t)
                    translate([corner_r, corner_r]) rounded_rect(box_l, box_w, corner_r);
            // lip ring, nests inside the cavity
            translate([wall + lip_clear, wall + lip_clear])
                linear_extrude(lip_h + 0.1)
                    difference() {
                        translate([lip_r, lip_r]) rounded_rect(lip_l, lip_ww, lip_r);
                        translate([lip_w + lip_r, lip_w + lip_r])
                            rounded_rect(lip_l - 2 * lip_w, lip_ww - 2 * lip_w,
                                         max(lip_r - lip_w, 0.1));
                    }
        }
        for (p = screw_xy) {
            translate([p[0], p[1], -1])
                cylinder(d = screw_clear_d, h = lip_h + lid_t + 2);
            translate([p[0], p[1], lip_h + lid_t - cbore_depth])
                cylinder(d = cbore_d, h = cbore_depth + 1);
            // clear the lip around each corner boss
            translate([p[0], p[1], -1])
                cylinder(d = boss_d + 2 * boss_clear, h = lip_h + 1);
        }
    }
}

if (part == "base") base();
else lid();
