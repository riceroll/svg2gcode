; **** Replicator 2X end.gcode ****
G1 Z155 F1000 ; send Z axis to bottom of machine
M140 S0 T0 ; cool down HBP
M104 S120 T0 ; cool down right extruder
M104 S120 T1 ; cool down left extruder
M127 ; stop blower fan
G162 X Y F3000 ; home XY maximum
; **** end of end.gcode ****
