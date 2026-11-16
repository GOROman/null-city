#!/usr/bin/env python3
"""Import a local autorouter session and fill GND planes (KiCad bundled Python)."""
import sys
from pathlib import Path
import wx,pcbnew as p
app=wx.App(False);root=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(root/'NC03_Controller.kicad_pcb'))
if not p.ImportSpecctraSES(b,sys.argv[1]):raise RuntimeError('Session import failed')
for t in b.GetTracks():
 if isinstance(t,p.PCB_TRACK) and not isinstance(t,p.PCB_VIA) and t.GetWidth()<p.FromMM(.2):t.SetWidth(p.FromMM(.2))
for f in b.GetFootprints():
 if f.GetReference().startswith('H'):f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
for layer in [p.B_Cu]:
 z=p.ZONE(b);z.SetNet(b.FindNet('GND'));z.SetLayer(layer);z.SetLocalClearance(p.FromMM(.2));z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetMinThickness(p.FromMM(.2))
 o=z.Outline();o.NewOutline()
 for x,y in [(50.3,50.3),(159.7,50.3),(159.7,134.7),(50.3,134.7)]:o.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(root/'NC03_Controller.kicad_pcb'),b)
print('Imported session and filled ground planes:',len(list(b.GetTracks())),'copper tracks/vias')
