"""Slice the diagnostic coupon with the existing H3C PLA profiles."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
profiles = root / 'print/h3c'
out = root / 'print/fit'
cmd = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
       '--load-settings', f'{profiles}/machine.json;{profiles}/caps.json',
       '--load-filaments', str(profiles / 'pla.json'),
       '--arrange', '1', '--ensure-on-bed', '--slice', '0',
       '--export-3mf', str(out / 'FIT_ONLY_direct_40x40.3mf'),
       str(out / 'FIT_ONLY_direct_40x40.stl')]
with (out / 'coupon_slice.log').open('w') as log:
    result = subprocess.run(cmd, cwd=root, stdout=log, stderr=subprocess.STDOUT)
raise SystemExit(result.returncode)
