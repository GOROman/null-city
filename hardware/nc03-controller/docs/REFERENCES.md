# Primary references

Retrieved 2026-11-16; check the actual purchased module revision before assembly.

| Reference | Used for |
|---|---|
| [Seeed XIAO nRF52840 series](https://wiki.seeedstudio.com/XIAO_BLE/) | Plus physical pad labels, GPIOs, USB, battery pads |
| [Seeed Plus schematic/PCB project](https://files.seeedstudio.com/wiki/XIAO-BLE/Seeed_Studio_XlAO_nRF52840_Plus_KiCAD_file.zip) | Pin/function cross-check and charging architecture |
| [Seeed official module land pattern](https://github.com/Seeed-Studio/OPL_Kicad_Library/blob/master/Seeed%20Studio%20XIAO%20Series%20Library/XIAO-nRF52840-Plus-SMD.kicad_mod) | 29-pad SMD land pattern; Plus underside pads must be soldered |
| [Nordic nRF52840](https://www.nordicsemi.com/Products/nRF52840) | USB full-speed device and BLE capability |
| [Nordic HID connection parameters](https://nrfconnectdocs.nordicsemi.com/addons/addon-hid/latest/applications/nrf_desktop/doc/ble_conn_params.html) | BLE connection interval vs proprietary LLPM |
| [NXP PCA9685](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf) | TSSOP28 pinout, open-drain LED sinks, OE, I²C 0x40 |
| [TI TPS22918](https://www.ti.com/lit/ds/symlink/tps22918.pdf) | SOT-23-6 pinout, switched USB LED rail, CT soft start, QOD |
| [TI SN74LV1T125](https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf) | SOT-23-5 pinout, 3.3V to 5V RGB data translation, input tolerance |
| [Brook Wingman FGC 2 FAQ](https://www.brookaccessory.com/faq/Wingman_FGC_2/) | Example of PS5 external conversion; vendor device/firmware compatibility must be tested |

A matching USB descriptor alone does not establish PS4/PS5 support. This custom device is not on any converter compatibility list. No authentication material or third-party USB VID/PID is included. Switch refers to the original Nintendo Switch target; Switch 2 is not validated. BLE HID over GATT on PC is a different protocol from Switch/PlayStation wireless controllers.
