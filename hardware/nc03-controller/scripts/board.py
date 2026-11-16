#!/usr/bin/env python3
"""Create placed PCB and Specctra routing input using KiCad 10's bundled Python (MIT)."""
import pcbnew as p,json,os,sys,math
import wx
app=wx.App(False)
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'design.json').read_text());b=p.BOARD()
LIB=Path(os.environ.get('KICAD_FOOTPRINT_DIR',str(Path(p.__file__).parents[4]/'SharedSupport/footprints')))
if not LIB.exists():
 for app in [Path('/Users/null/Applications/KiCad/KiCad.app'),Path('/Applications/KiCad/KiCad.app')]:
  if (app/'Contents/SharedSupport/footprints').exists():LIB=app/'Contents/SharedSupport/footprints';break
mm=p.FromMM
def xy(x,y):return p.VECTOR2I(mm(x),mm(y))
nets={}
for name in sorted({n for c in DATA['parts'] for n in c['pins'].values() if n is not None}):
 n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
# No-connect pad still needs the schematic-assigned net for parity checks.
ncname='unconnected-(U1-D16_BAT_ADC-Pad20)'
n=p.NETINFO_ITEM(b,ncname);b.Add(n);nets[ncname]=n
for c in DATA['parts']:
 lib,fp=c['source_footprint'].split(':');folder=ROOT/'lib/NC03.pretty' if lib=='NC03' else LIB/(lib+'.pretty')
 f=p.FootprintLoad(str(folder),fp)
 if f is None:raise RuntimeError('Missing footprint '+c['footprint'])
 # Project copies keep copper identical and move generic silk drawings to Fab.
 for g in f.GraphicalItems():
  if g.GetLayer()==p.F_SilkS:g.SetLayer(p.F_Fab)
 project_name=c['footprint'].split(':')[1]
 f.SetFPID(p.LIB_ID('NC03',project_name))
 p.FootprintSave(str(ROOT/'lib/NC03.pretty'),f)
 f.SetReference(c['ref']);f.SetValue(c['value']);f.GetField(p.FIELD_T_DATASHEET).SetText(c['datasheet']);f.SetPath(p.KIID_PATH('/'+DATA['root_uuid']+'/'+__import__('uuid').uuid5(__import__('uuid').NAMESPACE_URL,'https://github.com/GOROman/null-city/nc03-pcb/'+c['schematic_sheet']).__str__()+'/'+c['uuid']))
 f.SetFPID(p.LIB_ID('NC03',project_name));f.SetPosition(xy(*c['xy']))
 for pad in f.Pads():
  pn=pad.GetNumber();name=c['pins'].get(pn)
  if pn not in c['pins']:raise RuntimeError(c['ref']+' unknown pad '+pn)
  if name:pad.SetNet(nets[name])
  elif c['ref']=='U1' and pn=='20':pad.SetNet(nets[ncname]);pad.SetPinType('no_connect')
 # Names are legible and avoid tiny component body silk.
 f.Reference().SetTextSize(xy(.8,.8));f.Reference().SetTextThickness(mm(.12));f.Value().SetVisible(False)
 if c['ref'].startswith('R') or c['ref'].startswith('C') or c['ref']=='F1':
  f.Reference().SetLayer(p.F_Fab);f.Reference().SetVisible(True)
 # Reference geometry remains on Fab; purposeful connector legends are added below.
 for g in f.GraphicalItems():
  if g.GetLayer()==p.F_SilkS:g.SetLayer(p.F_Fab)
 f.Reference().SetLayer(p.F_Fab);f.Reference().SetVisible(True)
 b.Add(f)
# Four independent NPTH mounting holes; no case standoff changes are assumed.
for i,pos in enumerate(DATA['board']['mounts_mm']):
 f=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3');f.SetReference('H'+str(i+1));f.SetPosition(xy(*pos));f.Value().SetVisible(False);b.Add(f)
# 110 x 85 mm board; antenna keepout only on carrier, not on the XIAO module.
for a,z in [((50,50),(160,50)),((160,50),(160,135)),((160,135),(50,135)),((50,135),(50,50))]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(xy(*a));s.SetEnd(xy(*z));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
z=p.ZONE(b);z.SetIsRuleArea(True);layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.B_Cu);z.SetLayerSet(layers);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);o=z.Outline();o.NewOutline()
for x,y in [(50,85),(54,85),(54,97),(50,97)]:o.Append(mm(x),mm(y))
b.Add(z)
def text(s,x,y,size=1,layer=p.F_SilkS):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(xy(x,y));t.SetTextSize(xy(size,size));t.SetTextThickness(mm(.14));t.SetLayer(layer);b.Add(t)
text('NULL CITY / NC-03 A0',115,52,1)
text('PROTOTYPE / USB + BLE',112,68,.9)
text('ANTENNA KEEP-OUT',61,76,.8,p.Cmts_User)
# Keep top silk in empty gutters, away from THT mask apertures.
for c in DATA['parts']:
 if c['ref'].startswith('J'):
  x,y=c['xy'];text(c['ref'],x+1.25,y+5.8,.8)
text('RGB +5V / D / G',150,79,.8)
text('PC / PS* / SW',70,132.5,.8)
text('USB=open / BLE=short',85,107,.8)
# For review: critical requirements are not waived by autorouter settings.
ds=b.GetDesignSettings();ds.m_MinClearance=mm(.2);ds.m_TrackMinWidth=mm(.2);ds.m_ViasMinSize=mm(.6);ds.m_MinThroughDrill=mm(.3)
p.SaveBoard(str(ROOT/'NC03_Controller.kicad_pcb'),b)
print('PCB footprints',len(list(b.GetFootprints())),'nets',len(nets),'library',LIB)
if not p.ExportSpecctraDSN(b,str(ROOT/'checks/NC03_Controller.dsn')):raise RuntimeError('DSN export failed')
