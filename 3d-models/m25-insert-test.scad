// M2.5 heat-set insert test coupon
// A row of through-holes in different diameters — press an insert into each
// and find the size that grips best. Typical M2.5 insert hole is 3.4–3.6 mm.
// Tweak the parameters below and re-render for other insert sizes.

hole_diameters = [3.2, 3.4, 3.5, 3.6, 3.8];
hole_spacing   = 13;
thickness      = 8;    // deeper than a standard 5.7 mm long insert
width          = 16;
margin         = 8;    // block edge to first/last hole center
chamfer        = 0.6;  // radial entry chamfer
engrave_depth  = 0.5;

length = (len(hole_diameters) - 1) * hole_spacing + 2 * margin;
hole_y = width - 5.5;
$fn = 96;

difference() {
    cube([length, width, thickness]);
    for (i = [0 : len(hole_diameters) - 1]) {
        d = hole_diameters[i];
        x = margin + i * hole_spacing;
        translate([x, hole_y, -1])
            cylinder(d = d, h = thickness + 2);
        // 45-degree entry chamfer
        translate([x, hole_y, thickness - chamfer])
            cylinder(d1 = d, d2 = d + 2 * chamfer + 0.02, h = chamfer + 0.01);
        // size label
        translate([x, 4, thickness - engrave_depth])
            linear_extrude(engrave_depth + 0.1)
                text(str(d), size = 4, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}
