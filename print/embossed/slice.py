"""Slice the optional embossed panel using the existing fast PLA settings."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
profiles = root / 'print/h3c'
out = root / 'print/embossed'
sys.path.insert(0, str(profiles))
from preserve_overrides import preserve

cmd = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
       '--load-settings', f'{profiles}/machine.json;{profiles}/panel_fast.json',
       '--load-filaments', str(profiles / 'pla.json'),
       '--arrange', '1', '--ensure-on-bed', '--slice', '0',
       '--export-3mf', str(out / '03_control_panel_embossed.3mf'),
       str(out / 'PRINT_03_control_panel_embossed.stl')]
with (out / 'slice.log').open('w') as log:
    subprocess.run(cmd, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
preserve(out / '03_control_panel_embossed.3mf')
