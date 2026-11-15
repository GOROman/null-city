from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[2]
out=root/'print/h3c'
jobs=[('01_lower_tray','body','pla',[root/'STL/PRINT_01_lower_tray.stl']),('02_upper_frame','body','pla',[root/'STL/PRINT_02_upper_frame.stl']),('03_mounting_plate','body','pla',[root/'STL/PRINT_03_mounting_plate.stl']),('04_top_panel','caps','pla',[root/'STL/PRINT_04_top_panel.stl']),('05_TPU_feet','feet','tpu',sorted((root/'STL').glob('PRINT_TPU*.stl'))),('06_light_diffusers','caps','pla',sorted((root/'STL').glob('PRINT_light_*.stl'))),('optional_caps','caps','pla',sorted((root/'STL').glob('PRINT_*cap*.stl')))]
for name,process,material,models in jobs:
 cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--load-settings',f'{out}/machine.json;{out}/{process}.json','--load-filaments',str(out/(material+'.json')),'--arrange','1','--ensure-on-bed','--slice','0','--export-3mf',str(out/(name+'.3mf')),*map(str,models)]
 with (out/(name+'_slice.log')).open('w') as log:
  result=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT)
 print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
