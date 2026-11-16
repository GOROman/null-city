# Firmware integration contract — A0

This directory specifies firmware behavior; **no flashable gamepad firmware is delivered with A0**. The PCB alone does not implement USB, BLE, Switch or PlayStation protocols. Bring up the XIAO before ordering a populated board.

## GPIO and input path

Use the physical nRF port/pin values in `pinmap.csv`, not Arduino digital pin numbers: Seeed cores expose differing Arduino numbers. The non-Sense **Plus** module is required; the extra edge/underside contacts must be soldered. D16/P0.31 remains the module battery ADC and has no carrier trace. D14/P0.09 and D15/P0.10 must be configured for GPIO rather than NFC (e.g. the relevant nRF Connect SDK/Zephyr board setting); verify before selecting profiles. Do not write UICR blindly at runtime.

- Sample all 12 direct GPIO inputs at 4 kHz using a hardware timer, or timestamp GPIO edges. Active low. Each line has a 10k pull-up, 330Ω series resistor and 1nF capacitor. Press RC time is approximately 0.33µs and release approximately 10µs; firmware filtering dominates.
- Candidate eager debounce: report a new press immediately, inhibit bounce for 3–5ms; release after 1ms stable. Validate against the actual Seimitsu switches; no measured latency claim is made. Do not delay every report by a blanket 5–10ms sleep.
- SOCD: left+right neutral, up+down neutral. Eight-direction hat, neutral value 8. Do not add turbo or macros.
- USB target: 1ms interrupt-IN polling, submit only the freshest complete input state. 1ms USB polling is not a claim of 1ms end-to-end latency.
- PC BLE target: HOGP gamepad notifications, request 7.5ms connection interval and peripheral latency 0 during play. The central may choose a longer interval. USB and BLE must not emit duplicate inputs.
- Animation: queue nonblocking I²C/DMA work at lower priority than input capture; use PWM/EasyDMA for WS2812 data, never disable interrupts for an entire LED frame. No busy-wait animations in the scan callback.

## Selectors

J10 connects to a **break-before-make SPDT ON–OFF–ON** switch, common to GND. Connector pin 1 to the PC throw, pin 3 to the Switch throw; center position is `PS/ADAPTER`.

| MODE_PC_N | MODE_SWITCH_N | Requested profile |
|---|---|---|
| 0 | 1 | PC HID |
| 1 | 0 | Original Nintendo Switch USB protocol |
| 1 | 1 | PS external-converter profile |
| 0 | 0 | Fault: release all inputs and refuse profile activation |

J11 pin 1 (`LINK_USB_N`) has a pull-up: **open=USB, short to pin 2 GND=BLE**. Use a maintained SPST switch. BLE is a PC HOGP target only; selecting Switch or PS with BLE must show unsupported status and avoid claiming compatibility. Do not infer Switch Bluetooth support from BLE support: they use different protocols.

Debounce selector changes for 20ms, send an all-released report over the old transport, stop its reports, disconnect/detach, then start the newly selected profile. Descriptor changes require USB re-enumeration. Default disconnected J10 is PS/ADAPTER, not PC; this must be explicit on the panel legend. A startup override (hold B1 for PC) is acceptable but not implemented here.

## Console support gates

- Original Switch wired mode needs an appropriate protocol implementation and real-console testing; generic PC HID is insufficient. No copied vendor IDs or authentication keys are provided.
- PS4/PS5 native support is **not implemented by this PCB**. PS mode prepares a USB profile for a separately selected, compatible authenticated converter. The custom controller must be tested with that converter and console/game/firmware. A generic custom HID is not automatically accepted by a Brook or other adapter.
- Do not label PS tested, PS native, Switch tested, Switch 2 supported, or BLE console supported until corresponding hardware tests pass. PS4/PS5 converter selection remains open.
- The two existing menu buttons provide Start and Select/1P. Home, Capture/Share and touchpad-click need deliberate button chords or a separate auxiliary button board; do not silently remove the primary buttons to add these. J17 exposes I²C for a future auxiliary input expander, not an implemented expansion board.

## LED power and drivers

`D13/P1.01 LED_ENABLE` is active high and pulled down with 100k. Keep low at boot, during USB unconfigured/suspend states, battery operation and faults. A host-aware policy may restore it only after enumeration and power-budget acceptance; suspend/resume behavior needs firmware validation. The TPS22918 is a load switch, **not a current regulator or USB negotiator**. F1 is a fault PTC, not an accurate 350mA operating limit.

1. Initialize PCA9685 at 7-bit I²C address `0x40`. MODE2 must use open-drain outputs. Set all 16 outputs fully OFF before enabling the shared LED supply: OE is tied low, and reset outputs default LOW.
2. Drive RGB data low; then enable the LED rail. Supply only from USB VBUS. No battery boost is fitted, so LEDs are off on battery in A0.
3. Set an initial software budget of **150mA for all addressable RGB pixels together** and no more than about 50mA for the 16 indicator LEDs; count MCU/radio and battery charging current as well. Stay below the actually granted USB current, with margin. Select/cap charging current using the purchased module revision's official instructions; budget worst-case charger current rather than assuming a small value.
4. Use low-current strips or cap brightness/pixel count. The RGB connector is not for full-brightness metre-long strips. A fuse cannot substitute for the firmware budget.
5. To switch the rail off, set RGB data low and all PCA outputs OFF before deasserting LED_ENABLE. The TI translator's inputs tolerate voltage independently of its supply; validate leakage with USB removed. QOD discharges the switched output through the TPS22918 internal path.

Current square-window deck: connect 16 off-board NeoPixel/WS2812-compatible pixel modules in series on J14, followed by front/side strips. Allocate the 150mA RGB budget across the entire chain. No carrier PCB change is needed; pixel count and order must be configured in firmware. The PCA9685/J12/J13 circuits described above are legacy options for the old round-window monochrome LEDs and can remain unpopulated. Do not connect those sink outputs to pixel DIN. Pixel-module physical fit, current and firmware are unverified.

## Required measurements

Oscilloscope: switch contact to USB report/host receipt; p50/p95/p99 on USB and BLE; LED off vs animation at maximum budget; jitter and dropped reports. Test 8-direction SOCD, menu/system functions, selector faults/live changes, USB unplug/replug/suspend, BLE bond/reconnect, LED inrush and supply droop, battery charging/leakage, and the chosen console/converter versions. Record firmware commit, OS and instruments. Do not present scan rate as measured input latency.
