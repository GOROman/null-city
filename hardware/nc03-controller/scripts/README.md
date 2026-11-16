# Rebuilding / verification

Use KiCad **10.0.8** (CLI and bundled Python/pcbnew/wx) and Freerouting **2.5.0**. `generate.py` additionally needs Python 3 with `sexpdata==1.0.2`; install in a virtualenv. The router is a local CLI, not a cloud upload. Download it from its [official release](https://github.com/freerouting/freerouting/releases/tag/v2.5.0). Java runtime is required for the JAR.

The checked-in routed PCB is authoritative. These commands **overwrite it**; use a copy/branch for regeneration. Replace executable paths with the local installation. `board.py` reads KiCad's standard footprint libraries; use `KICAD_FOOTPRINT_DIR` if they are elsewhere. Local footprint copies preserve their package geometry and move generic silk outlines to Fab.

```sh
python3 scripts/generate.py
# KIPY means KiCad's bundled Python interpreter, with pcbnew and wx available.
"$KIPY" scripts/board.py
java -Djava.awt.headless=true -jar /path/to/freerouting-2.5.0.jar \
  -de checks/NC03_Controller.dsn -do checks/NC03_Controller.ses \
  -mp 15 --router.automatic_neckdown=false --router.optimizer.enabled=false \
  --gui.enabled=false
"$KIPY" scripts/finish_board.py checks/NC03_Controller.ses
kicad-cli sch erc NC03_Controller.kicad_sch --exit-code-violations -o checks/ERC.rpt
kicad-cli pcb drc NC03_Controller.kicad_pcb --schematic-parity \
  --exit-code-violations -o checks/DRC.rpt
python3 scripts/verify_netlist.py
```

Run these commands with `hardware/nc03-controller` as the working directory. KiCad command-line export does not require a global library setup: the project-local symbol and footprint tables are included. Intermediate DSN/SES and editor state are ignored. Do not commit manufacturing output until the validation gates in README are met.
