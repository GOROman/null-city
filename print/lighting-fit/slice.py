"""Slice four lighting-fit sections; use translucent PLA for this dimensional trial."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[2];out=root/'print/lighting-fit';settings=root/'print/h3c'
sys.path.insert(0,str(settings))
from preserve_overrides import preserve
subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--debug','3','--load-settings',f'{settings}/machine.json;{settings}/diffusers.json','--load-filaments',str(settings/'pla.json'),'--arrange','1','--ensure-on-bed','--slice','0','--export-3mf',str(out/'Lighting_seat_fit.3mf'),*map(str,sorted(out.glob('*.stl')))],cwd=root,check=True,timeout=180)
preserve(out/'Lighting_seat_fit.3mf')
