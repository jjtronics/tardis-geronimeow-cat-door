# TARDIS Geronimeow — printing, shopping list and assembly

**[Version française](../IMPRESSION_ET_MONTAGE.md)**

This guide covers printing, what to buy and the assembly order. The full
[V8 guide](../../tardis_v8/README.en.md) adds the cam tuning, wiring and ESPHome setup,
and the [Creality Print guide](CREALITY_PRINT_GUIDE.md) shows each step in the slicer
with screenshots.

> **Status:** no part has been printed yet. Validate the test coupon and the 1:1
> prototype before printing the large parts.

## Before printing

1. Measure your door (thickness, where the opening should be). The files are built for
   a **40 mm** door; the length of the M4 screws depends on it.
2. Open the plates in `tardis_v8/3mf/` with Creality Print 7.3.1. Each file is a
   complete project: K1 Max 0.4 mm, 0.20 mm Standard, Hyper PLA (CR-TPU for the
   stops), purge × 1.3. Prime tower, supports and brims are already set.
3. CFS slots: 1 blue, 2 ivory, 3 black, 4 brass. TPU goes through the external spool.
4. Do not move the prime tower and do not delete the "support fourreau" volumes on the
   front frame: they are the only supports needed.
5. Print `00_Eprouvette_jeux`, `01_Prototype_mecanique_75mm`, `10_Cames_reglables` and
   `07_Petites_pieces_bleu` first, then `11_Gabarit_porte`.

Small parts, and parts taller than they are wide, get a 5 mm brim (per-object
setting) that peels off by hand. The cams print with 0.1 mm layers, 100 % infill.

**Other slicers:** every part is in `tardis_v8/stl/`, in its assembled position. Lay
the parts flat as shown in the 3MF plates, decorated side up. Screw caps go head down,
the lock blade and the TPU stops lie flat. Only the axle sleeves of the front frame
need supports.

## The 12 plates

| Plate | Contents |
| --- | --- |
| `00_Eprouvette_jeux` | test coupon: axle, M4 screw, cap, pin, magnet pocket, M3 pilot hole, reed pocket, lock channel, D-key |
| `01_Prototype_mecanique_75mm` | bottom of the frame and of the flaps at 1:1 scale: hinge, cam, lock, magnets |
| `02_Battant_gauche`, `03_Battant_droit` | two multicolour half-shells and two pins per flap |
| `04_Facade_avant` | front frame with the POLICE BOX sign |
| `05_Facade_arriere` | rear front, sign, USB-C window |
| `06_Tunnel` | tunnel with an ivory trim line |
| `07_Petites_pieces_bleu` | screw caps, lock blade, knob and turn button, ESP cradle, magnet shims, lantern bases and cages |
| `08_Diffuseurs_ivoire` | two lantern diffusers |
| `09_Butees_TPU` | four soft stops (TPU) |
| `10_Cames_reglables` | cams with 3.5, 4.5 and 5.5 mm rise, two of each |
| `11_Gabarit_porte` | door cutting and drilling template |

Left and right are seen from the front (outside). Keep the front and rear screw caps
apart: their inner shapes differ.

## Shopping list

### Mechanics

| Qty | Item | Notes |
| ---: | --- | --- |
| 2 + 2 | Ø3 mm steel rod | cut to **39.4 mm** (lower axles) and **24.3 mm** (upper axles), deburred |
| 8 | clips for Ø3 mm shafts | DIN 6799 e-clips size 2.3 (file a groove) or Ø3 push-on Starlock washers |
| 4 | **Ø6 × 2 mm** neodymium magnets | N35 recommended: stronger magnets (N52) may hold too hard |
| 2 | **Ø6 × 3 mm** neodymium magnets | N35 to N52, for the sensor |
| 2 (+1) | normally open reed switches | 2 × 14 mm glass body, 10 to 20 AT |
| 1 | M3 × 18 screw | lock knob, screwed into the blade |
| 1 | M3 × 12 screw | turn-button pivot, with an M3 washer if needed |
| 4 | M4 × 70 low-head screws | with 4 washers (≤ 8 mm OD) and 4 nuts (≤ 3.2 mm); length for a 40 mm door |
| — | glue and tape | cyanoacrylate (magnets, pins), PLA glue (half-shells), foam double-sided tape, heat-shrink |
| — | optional | dry graphite for the cam ramps |

### Lighting and sensor (optional)

| Qty | Item | Notes |
| ---: | --- | --- |
| 1 | ESP32-C3 SuperMini | 22.5 × 18 mm, USB-C; check its size before printing the cradle |
| 2 (+1) | WS2812B F5 5 mm addressable RGB LEDs | check the pinout with your seller |
| 2 | 330 Ω resistors, ¼ W | on each data line, at the ESP end |
| 2 | 100 nF ceramic capacitors | 0805 SMD recommended (or small through-hole), fits in the lantern foot |
| 2 × 60 cm | thin 3-core wire, AWG 28 to 30 | 5 V, ground, data (one per lantern) |
| 60 cm | thin 2-core wire, AWG 28 to 30 | reed switch loop |
| 1 | USB-C cable and 5 V 1 A charger | power, indoor side |
| optional | 74AHCT125 module | only if a lantern flickers |

Tools: jigsaw, drill (Ø3, Ø5 and Ø10 bits), fine file, wire stripper, fine-tip
soldering iron, multimeter.

## Assembly

1. **Validate** the test coupon and the 75 mm prototype: cam (choice of rise), magnets
   (number of shims), lock, sensor.
2. **Cut the door** with the template (plate 11): window along the saw line, Ø3.2
   pilot holes, then drill Ø5 for the M4 screws.
3. **Flaps**: glue the magnets (Ø6 × 2 at the bottom, Ø6 × 3 at the top), minding the
   marked polarity. Do not glue the half-shells yet: they close around the axle and its
   upper clip in step 6.
4. **Front frame**: shims and sill magnets, reed switches in the lintel, wires in the
   grooves, lantern with its LED (solder joints and capacitor in the connection
   chamber of the foot).
5. **Lock**: blade in its channel, knob screwed on (M3 × 18), turn button on its pivot
   (M3 × 12).
6. **Cams and flaps**: cams on their D-keys, axles and clips. Put the front half-shell
   on its cam, insert the pins, then glue the rear half-shell. Each flap must come back
   to centre by itself, in both directions.
7. **Electronics**: solder, test on the bench, ESP in its cradle, cradle in the door
   notch.
8. **Tunnel, rear front**, M4 screws, washers, nuts, caps, TPU stops.
9. Flash the ESPHome configuration (see below) and run at least **50 cycles** by hand in FREE and
   LOCKED modes before leaving your cat alone.

## Electronics (optional)

| ESP32-C3 pin | Connected to |
| --- | --- |
| 5V, GND | both lanterns, reed switch loop (GND) |
| GPIO 3 | front lantern data, through 330 Ω |
| GPIO 4 | rear lantern data, through 330 Ω |
| GPIO 5 | the two reed switches in series, to GND (internal pull-up) |

A 100 nF capacitor is soldered across 5 V and GND on each LED, inside the lantern foot.
The wiring diagram is in [`tardis_v8/images/schema_eclairage.png`](../../tardis_v8/images/schema_eclairage.png).

ESPHome setup:

1. Install ESPHome (Home Assistant add-on, or `pip install esphome`).
2. Copy [`secrets.yaml.example`](../../tardis_v8/esphome/secrets.yaml.example) to
   `secrets.yaml` next to the configuration and fill it in: Wi-Fi, API encryption key
   (`openssl rand -base64 32`), OTA and fallback hotspot passwords. Never commit it.
3. Plug the ESP in over USB and run `esphome run chatiere-tardis.yaml`.

Home Assistant then finds two RGB lights with breathing, beacon, flash, candle and
colour-cycle effects, a cat passage sensor, a passage counter kept across reboots, a
"flash on passage" switch and a counter reset button. Entity names are in French
("Lanterne avant", "Passage du chat"…); rename them in the YAML if you like. WLED also works for the lights only (two WS281x
outputs of 1 LED on GPIO 3 and 4).

The [assembly video](../../tardis_v8/visualisations/montage_complet_V8.mp4) follows this
order, with close-ups of each mechanism (French captions).
