// Project enclosure built around M2.5 heat-set inserts (4 mm long)
// Features: corner bosses, PCB standoffs, vent slots, U-shaped cable port,
// wall-mount ears with countersinks, lid with interrupted registration lip.
// Insert holes are 3.5 mm per the PETG test coupon results.
// Screws: corners M2.5 x 6 or 8; PCB standoffs M2.5 x 6 ONLY (8 bottoms out).
//
// Render the base:  part = "base";
// Render the lid:   part = "lid";

part = "base"; // [base, lid]

// overall (external, lid included)
box_l = 80; box_w = 50; box_h = 30;
wall = 2;
floor_t = 2;
lid_t = 2.2;
corner_r = 3;

// inserts / screws
insert_hole_d = 3.5;
insert_hole_depth = 7.5;   // corner bosses
chamfer = 0.6;
boss_d = 8;
boss_inset = 5;

// PCB standoffs
standoff_d = 7;
standoff_h = 5;
standoff_hole_depth = 5.5; // 4 mm insert + tip room for a 6 mm screw
pcb_pattern_l = 56;        // mounting hole pattern, centered
pcb_pattern_w = 26;

// vents
vent_n = 6;
vent_w = 2;
vent_pitch = 6;
vent_z0 = 8; vent_z1 = 22;

// cable port (x = box_l end wall)
port_w = 12;
port_depth = 8;

// lid
screw_clear_d = 2.8;
cbore_d = 5.2;
cbore_depth = 1.0;
lip_h = 1.5;
lip_w = 1.2;
lip_clear = 0.25;
boss_clear = 0.3;

// mount ears
ear_l = 10;
ear_w = 14;
ear_t = 3;
ear_hole_d = 4.2;
ear_csk_d = 8.4;

wall_top = box_h - lid_t;
screw_xy = [[boss_inset, boss_inset],
            [box_l - boss_inset, boss_inset],
            [box_l - boss_inset, box_w - boss_inset],
            [boss_inset, box_w - boss_inset]];
standoff_xy = [[(box_l - pcb_pattern_l) / 2, (box_w - pcb_pattern_w) / 2],
               [(box_l + pcb_pattern_l) / 2, (box_w - pcb_pattern_w) / 2],
               [(box_l + pcb_pattern_l) / 2, (box_w + pcb_pattern_w) / 2],
               [(box_l - pcb_pattern_l) / 2, (box_w + pcb_pattern_w) / 2]];
$fn = 96;

module rounded_rect(l, w, r) {
    offset(r = r) square([l - 2 * r, w - 2 * r], center = false);
}

module insert_hole(depth) { // origin at the hole entry, z- down
    translate([0, 0, -depth]) cylinder(d = insert_hole_d, h = depth + 1);
    translate([0, 0, -chamfer])
        cylinder(d1 = insert_hole_d,
                 d2 = insert_hole_d + 2 * chamfer + 0.02, h = chamfer + 0.01);
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
            // mount ears
            for (x0 = [-ear_l, box_l - corner_r - 1])
                translate([x0, (box_w - ear_w) / 2])
                    linear_extrude(ear_t)
                        translate([2.5, 2.5])
                            rounded_rect(ear_l + corner_r + 1, ear_w, 2.5);
            // corner bosses and PCB standoffs
            for (p = screw_xy)
                translate([p[0], p[1], floor_t])
                    cylinder(d = boss_d, h = wall_top - floor_t);
            for (p = standoff_xy)
                cylinder_at(p, standoff_d, floor_t + standoff_h);
        }
        // insert holes
        for (p = screw_xy)
            translate([p[0], p[1], wall_top]) insert_hole(insert_hole_depth);
        for (p = standoff_xy)
            translate([p[0], p[1], floor_t + standoff_h])
                insert_hole(standoff_hole_depth);
        // vent slots through both long walls
        for (i = [0 : vent_n - 1])
            translate([box_l / 2 - (vent_n - 1) * vent_pitch / 2
                       + i * vent_pitch - vent_w / 2, -1, vent_z0])
                cube([vent_w, box_w + 2, vent_z1 - vent_z0]);
        // cable port: rectangle from the wall top + semicircular bottom
        translate([box_l - wall - 1, (box_w - port_w) / 2,
                   wall_top - port_depth + port_w / 2])
            cube([wall + 2, port_w, port_depth]);
        translate([box_l - wall - 1, box_w / 2, wall_top - port_depth + port_w / 2])
            rotate([0, 90, 0]) cylinder(d = port_w, h = wall + 2);
        // ear holes with 45-degree countersinks
        for (ex = [-ear_l / 2, box_l + ear_l / 2]) {
            translate([ex, box_w / 2, -1]) cylinder(d = ear_hole_d, h = ear_t + 2);
            translate([ex, box_w / 2, ear_t - (ear_csk_d - ear_hole_d) / 2])
                cylinder(d1 = ear_hole_d, d2 = ear_csk_d + 0.02,
                         h = (ear_csk_d - ear_hole_d) / 2 + 0.01);
        }
    }
}

module cylinder_at(p, d, h) { translate([p[0], p[1], 0]) cylinder(d = d, h = h); }

module lid() {
    lip_l = box_l - 2 * (wall + lip_clear);
    lip_ww = box_w - 2 * (wall + lip_clear);
    lip_r = corner_r - 1 - lip_clear;
    difference() {
        union() {
            translate([0, 0, lip_h])
                linear_extrude(lid_t)
                    translate([corner_r, corner_r]) rounded_rect(box_l, box_w, corner_r);
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
            translate([p[0], p[1], -1])
                cylinder(d = boss_d + 2 * boss_clear, h = lip_h + 1);
        }
        // interrupt the lip across the cable port
        translate([box_l - wall - lip_clear - lip_w - 1,
                   (box_w - port_w) / 2, -1])
            cube([lip_w + 2 * lip_clear + 2, port_w, lip_h + 1]);
    }
}

if (part == "base") base();
else lid();
