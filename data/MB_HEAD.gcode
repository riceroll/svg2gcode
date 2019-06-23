G90
M83
; **** Replicator 2X start.gcode ****
M73 P0 ; Enable build progress
G162 X Y F3000 ; Home XY maximum
G161 Z F1200 ; Home Z minimum
G92 Z-5 ; Set Z to -5
G1 Z0 ; Move Z to 0
G161 Z F100 ; Home Z slowly
M132 X Y Z A B ; Recall home offsets
M135 T0 ; Load right extruder offsets
G1 X-130 Y-75 Z30 F9000 ; Move to wait position off table
G130 X20 Y20 Z20 A20 B20 ; Lower stepper Vrefs while heating
M127 ; Set fan speed
M104 S190 T0 ; Heat right extruder
M133 T0 ; Stabilize extruder temperature
G130 X127 Y127 Z40 A127 B127 ; Default stepper Vref
G92 A0 B0 ; Zero extruders
G1 X100 Y-70 F9000 ; Move to front right corner of bed
G1 Z0.3 F6000 ; Move down to purge
G1 X-90 Y-70 E24 F2000 ; Extrude a line of filament across the front edge of the bed
G1 X-100 Y-70 F180 ; Wait for ooze
G1 X-110 Y-70 F5000 ; Fast wipe
G1 Z0.5 F100 ; Lift
G92 A0 B0 ; Zero extruders
M73 P1 ;@body (notify GPX body has started)
; **** end of start.gcode ****
G1 E-1.0000 F1200
