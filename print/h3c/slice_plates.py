from pathlib import Path
import subprocess
from preserve_overrides import preserve
root=Path(__file__).resolve().parents[2]
out=root/'print/h3c'
jobs=[('01_lower_tray','body','pla',[root/'STL/PRINT_01_lower_tray.stl',*sorted((root/'STL').glob('PRINT_USB_bridge_*.stl'))]),('02_upper_frame','body','pla',[root/'STL/PRINT_02_upper_frame.stl']),('03_control_panel','body','pla',[root/'STL/PRINT_03_control_panel.stl']),('04_caps','caps','pla',sorted((root/'STL').glob('PRINT_*cap*.stl'))),('05_TPU_feet','feet','tpu',sorted((root/'STL').glob('PRINT_TPU*.stl')))]
for name,process,material,models in jobs:
 cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--load-settings',f'{out}/machine.json;{out}/{process}.json','--load-filaments',str(out/(material+'.json')),'--arrange','1','--ensure-on-bed','--slice','0','--export-3mf',str(out/(name+'.3mf')),*map(str,models)]
 with (out/(name+'_slice.log')).open('w') as log:
  result=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT)
 print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
 preserve(out/(name+'.3mf'))
