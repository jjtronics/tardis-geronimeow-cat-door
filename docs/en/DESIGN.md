# Design choices — V8

**[Version française](../CONCEPTION.md)**

## One tunnel, two fronts

Both fronts frame the same tunnel. Two double-swing flaps pivot on four axles on the
outdoor side. They are decorated on both faces, so from indoors they are seen set back
inside the tunnel. The tunnel length follows the door thickness, 40 mm by default
(`door_depth`).

Each front measures 244 × 314.5 mm including its lantern. The tunnel is 190 × 200 mm
inside and 194.8 × 204.8 mm outside. The door cut-out (template) adds 0.7 mm per side,
i.e. 196.2 × 206.2 mm, plus a 36 × 11 mm notch under the tunnel for the ESP32.

The doors have six-pane windows and three moulded panels. The sign plate, the
medallion and the knobs appear on both faces. The windows are decorative, printed in
ivory filament: they are not glazed.

## Hinges and gravity return

The flaps turn on Ø3 steel axles in Ø3.4 mm bores. The axles are held in the frame by
clips; the flap slides up along them.

Under each flap, a **separate V-shaped cam** sits on the axle and is locked by a D-key
on the frame knuckle: one position only, and the same cam left and right. Opened by an
angle φ, the flap rises by `r · |φ| / 90°`. Its weight brings it back to centre with a
constant torque, in both directions, without a spring.

Three slopes are supplied: r = 3.5, 4.5 (default) and 5.5 mm. The underside of the flap
knuckle is not a copy of one cam but the **envelope** of all three: gentle slope up to
60° on either side of the bottom of the V, steep beyond. For any cam in the range, the
flap rests on the ±60° lines at the same height. It therefore rises according to the
fitted cam, with nothing else to change. The flap is shortened by 5 mm at the top to
leave room for the maximum lift (5.2 mm with the 5.5 mm cam).

Free swing goes up to ±80°; four TPU stops take the load at ±85°. The anti-pinch centre
gap is 2.4 mm.

## Central lock

A printed 10 × 4 mm blade slides vertically in the middle of the sill, in a channel
guided to 0.2 mm (0.4 mm on the front face, which prints as a bridge). Raised, it enters
4 mm into a pocket at the bottom corner of each flap. These pockets are closed front
and back, so neither flap can turn (blocked from 0.5°).

A knob screwed to the blade (M3 × 18) sticks out through a vertical slot in the base. A
pivoting **turn latch** (M3 × 12) turns a quarter turn under the knob to hold it up.
Turned up, it frees the knob and the blade drops below the sill under its own weight. A
side notch in the slot would not work: the guided blade cannot shift sideways.

## Wind-proof magnets

A Ø6 × 2 magnet sits flush under each flap, 20 mm from the free edge, above another one
in a 6 mm well in the sill. 1 mm shims under the sill magnet set the gap from 1 to
5 mm, and therefore the holding force. The right value is found on the prototype: the
flap must hold against the wind and open with a light push.

## Passage sensor and lighting

A Ø6 × 3 magnet at the top of each flap closes a reed switch in the lintel, 9 mm above.
The two reed switches are in series: the loop opens as soon as either flap opens.
Plastic lets the magnetic field through, so nothing is visible.

The lanterns take 5 mm WS2812B LEDs. Under each LED, the lantern foot has a 9 × 13.5 mm
connection chamber, 5 mm high, open underneath and towards the back. It houses the
bent legs, the heat-shrunk joints and the 100 nF capacitor. Its 45° pointed roof prints
without bridge or support (a flat roof triggered Creality Print's "floating overhang"
warning). A 4.5 × 2.5 mm groove on the back of each front, against the door, routes the
lantern and sensor wires to a printed cradle under the tunnel. The cradle holds an
ESP32-C3 SuperMini whose USB-C socket is reached through a window in the rear front.
The supplied ESPHome configuration handles the lights, the sensor, a counter and a
flash on every passage.

## Half-shell flaps

The relief on both faces prevents printing a whole flap flat. Each flap is made of two
multicolour half-shells, printed with their gluing faces on the bed. Ø2 × 3 mm pins in
2.2 mm holes align the half-shells. The glue carries the load; the nominal glue gap is
0.1 mm. The lock and magnet pockets are centred on the gluing plane, so each half-shell
carries half of them.

## Fixing the fronts

Four M4 screws go through both fronts and the door, 214 mm apart horizontally and
146 mm vertically. For a 40 mm door: 70 mm low-head screws (head Ø ≤ 7.6 mm, height
≤ 2.2 mm), washers Ø ≤ 8 mm and nuts ≤ 3.2 mm. The rear caps are hollowed to take the
screw ends.

## Print files

`generate.py` builds the volumes in Blender, in millimetres, and lays the parts out on
twelve K1 Max plates. It writes them directly as complete Creality Print projects
(printer, profile, colours, prime tower away from the parts), with per-object settings:
0.1 mm layers for the cams, a 5 mm brim for small parts (13 mm apart so the brims do not
fuse), supports limited to the axle sleeves. Each part is oriented to avoid overhangs:
caps head down, lock blade and TPU stops lying flat, brass knobs flaring into a cone
towards their face, lantern roofs hollowed as a 45° cone underneath.

## Limits

The parameters at the top of the file do not make everything adaptive: changing the
opening width or height means reviewing mouldings, holes and clearances, then running
the checks again. The checks work on rigid volumes at nominal dimensions. Cam friction,
magnet strength, reed switch threshold, gluing and fatigue must be validated on the
prototype.
