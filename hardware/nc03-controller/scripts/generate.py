#!/usr/bin/env python3
"""Generate the editable NC-03 controller schematic and component manifest (MIT).
Requires sexpdata; board generation uses the Python shipped with KiCad 10.
All library geometry is original except the separately attributed XIAO land pattern.
"""
import json,uuid,csv,os,sys,copy
from pathlib import Path
import sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
S=sx.Symbol
def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/GOROman/null-city/nc03-pcb/'+name))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def num(x):return f'{x:.6f}'.rstrip('0').rstrip('.') if isinstance(x,float) else str(x)
parts=[];symbols={}
def add(ref,value,fp,pins,pos,sch,desc='',types=None,names=None):
 p=dict(ref=ref,value=value,footprint=fp,pins={str(k):v for k,v in pins.items()},xy=pos,sch=sch,description=desc,uuid=uid(ref))
 p['types']=types or {};p['names']=names or {};parts.append(p);return p
RFP='Resistor_SMD:R_0805_2012Metric';CFP='Capacitor_SMD:C_0805_2012Metric'
def r(ref,value,a,b,pos,sch):return add(ref,value,RFP,{1:a,2:b},pos,sch)
def c(ref,value,a,b,pos,sch):return add(ref,value,CFP,{1:a,2:b},pos,sch)
def conn(ref,value,nets,pos,sch):
 n=len(nets);return add(ref,value,f'Connector_JST:JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical',dict(enumerate(nets,1)),pos,sch)
# Exact vendor pad -> label map; D16 is reserved for the module battery ADC.
padnames={str(i+1):f'D{i}' for i in range(11)}
padnames.update({'12':'3V3_OUT','13':'GND','14':'VBUS','15':'D11','16':'D12','17':'D13','18':'D14','19':'D15','20':'D16_BAT_ADC','21':'D17','22':'D18','23':'D19','24':'SWDIO','25':'SWDCLK','26':'RESET','27':'GND','28':'VBAT','29':'GND'})
input_gpio=[('UP','D0','P0.02'),('DOWN','D1','P0.03'),('LEFT','D2','P0.28'),('RIGHT','D3','P0.29'),('B1','D6','P1.11'),('B2','D7','P1.12'),('B3','D8','P1.13'),('B4','D9','P1.14'),('B5','D10','P1.15'),('B6','D11','P0.15'),('1P','D17','P1.03'),('START','D18','P1.05')]
func={d:'IN_'+name for name,d,_ in input_gpio}
func.update(D4='I2C_SDA',D5='I2C_SCL',D12='RGB_DATA_3V3',D13='LED_ENABLE',D14='MODE_PC_N',D15='MODE_SWITCH_N',D19='LINK_USB_N')
modnets={p:func.get(n,{'3V3_OUT':'+3V3','GND':'GND','VBUS':'VBUS','VBAT':'BAT_SW','SWDIO':'SWDIO','SWDCLK':'SWDCLK','RESET':'RESET_N'}.get(n)) for p,n in padnames.items()}
types={p:('power_out' if n in ('3V3_OUT','VBUS') else 'power_in' if n in ('GND','VBAT') else 'bidirectional') for p,n in padnames.items()};types['20']='passive'
add('U1','XIAO nRF52840 Plus','NC03:XIAO_nRF52840_Plus',modnets,[61,91],[54,61],types=types,names=padnames)
conn('J1','LEVER: G U D L R',['GND','SW_UP','SW_DOWN','SW_LEFT','SW_RIGHT'],[73,58],[105,30])
for i,name in enumerate(['B1','B2','B3','B4','B5','B6','1P','START']):
 conn('J'+str(i+2),name+': G SIG',['GND','SW_'+name],[91+(i%4)*17,58+(i//4)*17],[170+(i%4)*37,30+(i//4)*40])
for i,(name,_,_) in enumerate(input_gpio):
 x=78+(i%4)*10;y=87+(i//4)*8
 scx=105+(i%4)*38;scy=115+(i//4)*32
 r('R'+str(i+1),'330','SW_'+name,'IN_'+name,[x,y],[scx,scy])
 r('R'+str(i+21),'10k','+3V3','IN_'+name,[x+3,y+2.5],[scx,scy+9])
 c('C'+str(i+1),'1nF','IN_'+name,'GND',[x+6,y],[scx,scy+18])
# 16 existing 3 mm indicator LEDs: externally wired anode, resistor-limited sinks.
pca={str(i):'GND' for i in [1,2,3,4,5,14,24,25]}
for i in range(16):pca[str(6+i if i<8 else 15+i-8)]='LED_DRV_'+str(i)
pca.update({'23':'GND','26':'I2C_SCL','27':'I2C_SDA','28':'+3V3'})
pnames={p:('A'+str(int(p)-1) if int(p)<=5 else 'VSS' if p=='14' else 'A5' if p=='24' else 'EXTCLK' if p=='25' else 'OE_N' if p=='23' else 'SCL' if p=='26' else 'SDA' if p=='27' else 'VDD' if p=='28' else n) for p,n in pca.items()}
ptypes={p:('power_in' if p in ('14','28') else 'open_collector' if n.startswith('LED_DRV') else 'bidirectional' if p=='27' else 'input') for p,n in pca.items()}
add('U2','PCA9685PW','Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm',pca,[130,108],[300,120],types=ptypes,names=pnames)
for i in range(16):
 r('R'+str(i+41),'1k','LED_K_'+str(i),'LED_DRV_'+str(i),[118 if i<8 else 143,98+(i%8)*3.5],[255 if i<8 else 350,90+(i%8)*13])
conn('J12','DIR LEDs: +5 K0..K7',['+5V_LED']+['LED_K_'+str(i) for i in range(8)],[79,128],[255,55])
conn('J13','BTN LEDs: +5 K8..K15',['+5V_LED']+['LED_K_'+str(i) for i in range(8,16)],[115,128],[350,55])
# Power rail enabled only after USB configuration; RGB is off on battery.
add('F1','350mA PTC','Fuse:Fuse_1206_3216Metric',{1:'VBUS',2:'VBUS_FUSED'},[116,81],[54,205])
add('U3','TPS22918DBVR','Package_TO_SOT_SMD:SOT-23-6',{1:'VBUS_FUSED',2:'GND',3:'LED_ENABLE',4:'LED_CT',5:'+5V_LED',6:'+5V_LED'},[128,85],[106,208],names={'1':'VIN','2':'GND','3':'ON','4':'CT','5':'QOD','6':'VOUT'},types={'1':'power_in','2':'power_in','3':'input','4':'passive','5':'passive','6':'power_out'})
r('R60','100k','LED_ENABLE','GND',[120,86],[150,195])
c('C20','10nF','LED_CT','GND',[128,89],[150,207])
c('C21','1uF','VBUS_FUSED','GND',[124,81],[150,219])
c('C22','47uF 10V','+5V_LED','GND',[136,85],[150,231])
add('U4','SN74LV1T125DBVR','Package_TO_SOT_SMD:SOT-23-5',{1:'GND',2:'RGB_DATA_3V3',3:'GND',4:'RGB_DATA_5V',5:'+5V_LED'},[145,86],[208,208],names={'1':'OE_N','2':'A','3':'GND','4':'Y','5':'VCC'},types={'1':'input','2':'input','3':'power_in','4':'tri_state','5':'power_in'})
r('R61','330','RGB_DATA_5V','RGB_DIN',[149,89],[246,201])
r('R62','100k','RGB_DATA_3V3','GND',[141,90],[246,213])
conn('J14','RGB: +5 DIN GND',['+5V_LED','RGB_DIN','GND'],[150,95],[246,231])
c('C23','100nF','+5V_LED','GND',[148,82],[208,239])
c('C24','100nF','+3V3','GND',[136.5,113],[300,185])
c('C25','1uF','+3V3','GND',[71,103],[54,135])
r('R63','4.7k','+3V3','I2C_SDA',[109,111],[300,201])
r('R64','4.7k','+3V3','I2C_SCL',[109,115],[300,214])
conn('J10','MODE: PC G SW',['MODE_PC_N','GND','MODE_SWITCH_N'],[61,124],[54,165])
conn('J11','LINK: USB=open BLE=short',['LINK_USB_N','GND'],[73,119],[54,185])
r('R65','10k','+3V3','MODE_PC_N',[70,106],[105,165])
r('R66','10k','+3V3','MODE_SWITCH_N',[70,109.5],[145,165])
r('R67','10k','+3V3','LINK_USB_N',[75,113],[185,165])
conn('J15','BATTERY: + GND',['BAT_PLUS','GND'],[58,106],[300,237])
conn('J16','BAT SWITCH: IN OUT',['BAT_PLUS','BAT_SW'],[58,115],[345,237])
conn('J17','AUX: 3V3 SDA SCL G',['+3V3','I2C_SDA','I2C_SCL','GND'],[99,119],[350,205])
conn('J18','SWD: 3V3 IO CLK RST G',['+3V3','SWDIO','SWDCLK','RESET_N','GND'],[82,113],[54,112])
# Datasheets are links, never redistributed under our own license.
urls={'U1':'https://wiki.seeedstudio.com/XIAO_BLE/','U2':'https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf','U3':'https://www.ti.com/lit/ds/symlink/tps22918.pdf','U4':'https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf'}
for p in parts:
 p['datasheet']=urls.get(p['ref'],'')
 p['source_footprint']=p['footprint']
 if not p['footprint'].startswith('NC03:'):p['footprint']='NC03:'+p['footprint'].replace(':','_')
# Custom library symbols: pin names and electrical types retain ERC usefulness.
def symbol(p):
 name=p['ref'];n=len(p['pins']);half=(n+1)//2;h=max(5.08,(half+1)*2.54/2);pins=[];p['pinxy']={}
 if name.startswith(('R','C','F')):
  p['pinxy']={'1':[-5.08,0,0],'2':[5.08,0,180]}
  if name.startswith('C'):
   body='(polyline (pts (xy -0.635 -2) (xy -0.635 2)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.635 -2) (xy 0.635 2)) (stroke (width 0.254) (type default)) (fill (type none)))'
   lead=4.445
  else:
   body='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'
   lead=2.54
  return f'''(symbol "NC03:{name}" (pin_names (offset 0) (hide yes)) (pin_numbers (hide yes)) (in_bom yes) (on_board yes)
   (property "Reference" {q(name[0])} (at 0 3.81 0) (effects (font (size 1.27 1.27))))
   (property "Value" {q(p['value'])} (at 0 -3.81 0) (effects (font (size 1 1))))
   (symbol "{name}_0_1" {body})
   (symbol "{name}_1_1" (pin passive line (at -5.08 0 0) (length {lead}) (name "1" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))
   (pin passive line (at 5.08 0 180) (length {lead}) (name "2" (effects (font (size 1 1)))) (number "2" (effects (font (size 1 1)))))))'''

 for i,(number,net) in enumerate(p['pins'].items()):
  side=0 if i<half else 1;j=i if side==0 else i-half;x=-12.7 if side==0 else 12.7;y=h-2.54-j*2.54;angle=0 if side==0 else 180
  p['pinxy'][number]=[x,-y,angle]
  pins.append(f'(pin {p["types"].get(number,"passive")} line (at {num(x)} {num(y)} {angle}) (length 2.54) (name {q(p["names"].get(number,number))} (effects (font (size 1 1)))) (number {q(number)} (effects (font (size 1 1)))))')
 return f'''(symbol "NC03:{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes)
 (property "Reference" {q(p['ref'][0])} (at 0 {num(h+2.54)} 0) (effects (font (size 1.27 1.27))))
 (property "Value" {q(p['value'])} (at 0 {num(-h-2.54)} 0) (effects (font (size 1.0 1.0))))
 (symbol "{name}_0_1" (rectangle (start -10.16 {num(h)}) (end 10.16 {num(-h)}) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "{name}_1_1" {''.join(pins)}))'''
libs=[symbol(p) for p in parts]
# Five sheets via root + flat child sheet documents. Each page uses global labels.
groups=[('01_controller','Controller and selectors',['U1','J10','J11','J15','J16','J17','J18','R65','R66','R67','C25']),('02_inputs','Direct low-latency inputs',[p['ref'] for p in parts if (p['ref'].startswith('J') and int(p['ref'][1:]) in range(1,10)) or (p['ref'].startswith('R') and int(p['ref'][1:])<=32) or (p['ref'].startswith('C') and int(p['ref'][1:])<=12)]),('03_leds','16 indicator LED sinks',['U2','J12','J13','C24','R63','R64']+['R'+str(i) for i in range(41,57)]),('04_power_rgb','USB LED power and RGB',['F1','U3','U4','R60','R61','R62','J14']+['C'+str(i) for i in range(20,24)])]
rootuuid=uid('root');rootitems=[]
for idx,(fname,title,refs) in enumerate(groups):
 sheetuuid=uid(fname);syms=[];labels=[];nc=[];wires=[]
 # Arrange symbols on an A2 engineering sheet with non-overlapping label gutters.
 group=[next(p for p in parts if p['ref']==ref) for ref in refs]
 for k,p in enumerate(group):
  n=len(p['pins']);long=n>12
  if p['ref']=='U1':x,y=78,91
  elif p['ref']=='U2':x,y=78,91
  else:
   # Fixed generous 67 x 28 mm cells (large parts placed first in their own column).
   ofs=1 if fname in ('01_controller','03_leds') else 0
   kk=k-ofs;x=160+(kk%6)*65 if ofs else 48+(kk%8)*65;y=40+(kk//(6 if ofs else 8))*38
  angle=0
  if fname=='02_inputs':
   ref=p['ref'];number=int(ref[1:])
   if ref.startswith('J'):
    x=45+((number-1)%5)*70;y=30+((number-1)//5)*30
   else:
    ii=number-1 if ref.startswith('C') or number<=12 else number-21
    bx=40+(ii%4)*90;by=105+(ii//4)*63
    if ref.startswith('C'):x,y,angle=bx+15.24,by+12.7,270
    elif number>=21:x,y,angle=bx+15.24,by-12.7,270
    else:x,y=bx,by
  x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
  p['schematic_sheet']=fname;p['schematic_xy']=[x,y]
  attrs=f'''(lib_id "NC03:{p['ref']}") (at {num(x)} {num(y)} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{p['uuid']}")'''
  h=max(5.08,((n+1)//2+1)*2.54/2)
  props=f'''(property "Reference" {q(p['ref'])} (at {num(x)} {num(y-h-3.2)} 0) (effects (font (size 1.27 1.27))))
(property "Value" {q(p['value'])} (at {num(x)} {num(y+h+2.4)} 0) (effects (font (size 1 1))))
(property "Footprint" {q(p['footprint'])} (at {num(x)} {num(y)} 0) (effects (font (size 1 1)) (hide yes)))
(property "Datasheet" {q(p['datasheet'])} (at {num(x)} {num(y)} 0) (effects (font (size 1 1)) (hide yes)))'''
  if angle:
   props=f'''(property "Reference" {q(p['ref'])} (at {num(x-6.35)} {num(y-1.27)} 0) (effects (font (size 1.27 1.27))))
(property "Value" {q(p['value'])} (at {num(x-6.35)} {num(y+2.54)} 0) (effects (font (size 1 1))))
(property "Footprint" {q(p['footprint'])} (at {num(x)} {num(y)} 0) (effects (font (size 1 1)) (hide yes)))
(property "Datasheet" {q(p['datasheet'])} (at {num(x)} {num(y)} 0) (effects (font (size 1 1)) (hide yes)))'''
  syms.append(f'(symbol {attrs} {props} (instances (project "NC03_Controller" (path "/{rootuuid}/{sheetuuid}" (reference {q(p["ref"])}) (unit 1)))))')
  for pin,net in p['pins'].items():
   dx,dy,ang=p['pinxy'][pin]
   if angle==270:dx,dy=-dy,dx
   xx=x+dx;yy=y+dy
   if fname=='02_inputs':
    ref=p['ref'];number=int(ref[1:])
    if (ref.startswith('C') and pin=='1') or (ref.startswith('R') and number>=21 and pin=='2'):continue
    if ref.startswith('R') and number<=12 and pin=='2':xx=x+30.48
   if net is None:nc.append(f'(no_connect (at {num(xx)} {num(yy)}) (uuid "{uid(p["ref"]+pin+"nc")}"))');continue
   # Global labels sit at pin endpoints, facing away from the body.
   labelangle=0 if dx<0 else 180
   if angle:labelangle=90 if dy<0 else 270
   labels.append(f'(global_label {q(net)} (shape passive) (at {num(xx)} {num(yy)} {labelangle}) (effects (font (size 0.9 0.9)) (justify {"right" if dx<0 else "left"})) (uuid "{uid(p["ref"]+pin+"label")}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {num(xx)} {num(yy)} 0) (effects (font (size 1 1)) (hide yes))))')
  # library id unique per component makes all dimensions and pin types explicit.
 if fname=='02_inputs':
  for ii in range(12):
   rp=next(p for p in group if p['ref']=='R'+str(ii+1));x,y=rp['schematic_xy'];xx=x+15.24
   for j,(a,b) in enumerate([((x+5.08,y),(x+30.48,y)),((xx,y-7.62),(xx,y+7.62))]):
    wires.append(f'(wire (pts (xy {num(a[0])} {num(a[1])}) (xy {num(b[0])} {num(b[1])})) (stroke (width 0.254) (type default)) (uuid "{uid(str(ii)+str(j)+"wire")}"))')
   wires.append(f'(junction (at {num(xx)} {num(y)}) (diameter 0.762) (color 0 0 0 0) (uuid "{uid(str(ii)+"junction")}"))')
 paper='A3' if fname=='02_inputs' else 'A2'
 text=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "{sheetuuid}") (paper "{paper}") (title_block (title {q('NC-03 '+title)}) (date "2026-11-16") (rev "A0-PROTOTYPE") (company "GOROman"))
 (lib_symbols {''.join(libs)}) {''.join(syms+labels+nc+wires)} (embedded_fonts no))'''
 (ROOT/(fname+'.kicad_sch')).write_text(text)
 sy=40+idx*38
 rootitems.append(f'''(sheet (at 45 {sy}) (size 100 25) (stroke (width 0) (type default)) (fill (color 0 0 0 0)) (uuid "{sheetuuid}") (property "Sheetname" {q(title)} (at 45 {sy-1} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" {q(fname+'.kicad_sch')} (at 45 {sy+26} 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project "NC03_Controller" (path "/{rootuuid}" (page "{idx+2}")))))''')
flaglib='(symbol "NC03:PWR_FLAG" (pin_names (offset 0)) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 3 0) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at 0 2 0) (effects (font (size 1 1)))) (symbol "PWR_FLAG_0_1" (polyline (pts (xy -1 0) (xy 0 1.27) (xy 1 0)) (stroke (width 0.2) (type default)) (fill (type none)))) (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'
flagitems=[]
for i,net in enumerate(['GND','BAT_SW','VBUS_FUSED']):
 xx=round((180+i*35)/1.27)*1.27;yy=round(150/1.27)*1.27
 flagitems.append(f'(symbol (lib_id "NC03:PWR_FLAG") (at {xx} {yy} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(net+"flag")}") (property "Reference" "#FLG0{i+1}" (at {xx} {yy-3} 0) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at {xx} {yy-6} 0) (effects (font (size 1 1)))) (instances (project "NC03_Controller" (path "/{rootuuid}" (reference "#FLG0{i+1}") (unit 1))))) (global_label "{net}" (shape passive) (at {xx} {yy} 0) (effects (font (size 1 1)) (justify left)) (uuid "{uid(net+"flaglabel")}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {xx} {yy} 0) (effects (font (size 1 1)) (hide yes))))')
root=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "{rootuuid}") (paper "A4") (title_block (title "NULL CITY NC-03 USB/BLE Controller") (date "2026-11-16") (rev "A0-PROTOTYPE") (company "GOROman")) (lib_symbols {flaglib}) {''.join(rootitems+flagitems)} (text "A0: electrical prototype / console protocols and case fit NOT validated.\nUSB data stays on XIAO. No second USB-C receptacle on this carrier.\nPS requires a compatible authenticated external converter (not included).\nLED rail: USB configured only, off during battery/BLE use." (at 158 70 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid "{uid('notes')}")) (sheet_instances (path "/" (page "1"))) (embedded_fonts no))'''
(ROOT/'NC03_Controller.kicad_sch').write_text(sx.dumps(sx.loads(root)))
# Local symbols make the project editable without a global library setup.
libfile='(kicad_symbol_lib (version 20250114) (generator \"kicad_symbol_editor\") '+(''.join(libs)+flaglib).replace('(symbol \"NC03:', '(symbol \"')+')'
(ROOT/'lib/NC03.kicad_sym').write_text(libfile)
(ROOT/'design.json').write_text(json.dumps({'revision':'A0-PROTOTYPE','root_uuid':rootuuid,'parts':parts,'inputs':[{'signal':n,'xiao':d,'nrf':g} for n,d,g in input_gpio],'board':{'origin_mm':[50,50],'size_mm':[110,85],'mounts_mm':[[55,55],[155,55],[55,130],[155,130]],'rf_keepout_mm':[50,85,54,97]}},indent=2)+'\n')
with (ROOT/'BOM.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['Reference','Value','Footprint','Datasheet']);w.writerows((p['ref'],p['value'],p['footprint'],p['datasheet']) for p in parts)
print('Generated',len(parts),'components and 5 schematic sheets')
