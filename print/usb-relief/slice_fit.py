"""Slice the USB guide test region and both retaining bridges before the full case."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[2]
profiles=root/'print/h3c';out=root/'print/usb-relief'
sys.path.insert(0,str(profiles))
from preserve_overrides import preserve
models=[out/'FIT_USB_S_guide.stl',root/'STL/PRINT_USB_bridge_1.stl',root/'STL/PRINT_USB_bridge_2.stl']
cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
     '--load-settings',f'{profiles}/machine.json;{profiles}/panel_fast.json',
     '--load-filaments',str(profiles/'pla.json'),'--arrange','1','--ensure-on-bed','--slice','0',
     '--export-3mf',str(out/'USB_S_guide_fit.3mf'),*map(str,models)]
with (out/'slice.log').open('w') as log:
    subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
preserve(out/'USB_S_guide_fit.3mf')
