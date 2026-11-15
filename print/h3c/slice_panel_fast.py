"""Build the separate fast prototype panel without replacing the standard project."""
from pathlib import Path
import subprocess
from preserve_overrides import preserve

root = Path(__file__).resolve().parents[2]
out = root / 'print/h3c'
cmd = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
       '--load-settings', f'{out}/machine.json;{out}/panel_fast.json',
       '--load-filaments', str(out / 'pla.json'),
       '--arrange', '1', '--ensure-on-bed', '--slice', '0',
       '--export-3mf', str(out / '03_control_panel_fast.3mf'),
       str(root / 'STL/PRINT_03_control_panel.stl')]
with (out / '03_control_panel_fast_slice.log').open('w') as log:
    subprocess.run(cmd, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
preserve(out / '03_control_panel_fast.3mf')
