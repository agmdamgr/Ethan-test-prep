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
    difference() {
        linear_extrude(lid_t)
            translate([corner_r, corner_r]) rounded_rect(box_l, box_w, corner_r);
        for (p = screw_xy) {
            translate([p[0], p[1], -1])
                cylinder(d = screw_clear_d, h = lid_t + 2);
            translate([p[0], p[1], lid_t - cbore_depth])
                cylinder(d = cbore_d, h = cbore_depth + 1);
        }
    }
}

if (part == "base") base();
else lid();
