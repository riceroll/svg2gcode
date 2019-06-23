G90
M82
M106 S0 ; fan off
M204 S1500 ; default acceleration
M205 X15.00 ; maximum X Y jerk
T0
G1 X20 Y5 Z5 F15000.0 ; heating location
M140 S0
M104 S195 T0 ; heat left
M109 S195 T0 ; stabilize left
G1 Z0.2
G92 E0 ; zero extruder
G1 E30
G92 E0 ; zero extruder
G1 X120 E15 F1000 ; purge right extruder
G92 E0
G1 E-6.2500 F1500
M218 T0 X0.0 Y0.0 ; reset extruder offset
T0
M218 T0 X-18.0 Y0.0 ; set extruder offset
