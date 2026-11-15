"""Regenerate six functional source plates and optional caps and the sliced project using absolute paths."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[2]
out=root/'print/h3c'
for script in ('slice_plates.py','combine_plates.py'):
 subprocess.run([sys.executable,str(out/script)],cwd=root,check=True)
cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--export-3mf',str(out/'NC03_H3C_6plates_lighting_sliced.3mf'),str(out/'NC03_H3C_6plates_lighting.3mf')]
with (out/'combined_slice.log').open('w') as log:subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
print(out/'NC03_H3C_6plates_lighting_sliced.3mf')
