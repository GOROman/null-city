"""Rebuild every README render from the current assembly with Blender."""
from pathlib import Path
import argparse
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--blender',default=shutil.which('blender') or '/Applications/Blender.app/Contents/MacOS/Blender')
args=parser.parse_args()
for script in ('render_readme.py','render_lighting.py','render_usb_relief.py'):
    print('Rendering',script,flush=True)
    subprocess.run([args.blender,'--background',str(root/'NULL_CITY_NC03.blend'),'--threads','6','--python-exit-code','1','--python',str(root/'scripts'/script)],cwd=root,check=True)
