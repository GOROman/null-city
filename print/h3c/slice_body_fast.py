"""Slice the updated lower case and both USB bridges as a separate fast job."""
from pathlib import Path
import subprocess
from preserve_overrides import preserve

root=Path(__file__).resolve().parents[2]
out=root/'print/h3c'
models=[root/'STL/PRINT_01_lower_tray.stl',*sorted((root/'STL').glob('PRINT_USB_bridge_*.stl'))]
cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
     '--load-settings',f'{out}/machine.json;{out}/body_fast.json',
     '--load-filaments',str(out/'pla.json'),'--arrange','1','--ensure-on-bed','--slice','0',
     '--export-3mf',str(out/'01_lower_tray_fast.3mf'),*map(str,models)]
with (out/'01_lower_tray_fast_slice.log').open('w') as log:
    subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
preserve(out/'01_lower_tray_fast.3mf')
