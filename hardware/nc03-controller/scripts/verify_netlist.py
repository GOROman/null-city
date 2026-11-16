#!/usr/bin/env python3
"""Check electrical design invariants against KiCad's independently exported netlist (MIT)."""
import csv,json,os,shutil,subprocess,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cli=os.environ.get('KICAD_CLI') or shutil.which('kicad-cli')
if not cli:
 for a in [Path.home()/'Applications/KiCad/KiCad.app',Path('/Applications/KiCad/KiCad.app')]:
  p=a/'Contents/MacOS/kicad-cli'
  if p.exists():cli=str(p);break
if not cli:raise SystemExit('Set KICAD_CLI or install KiCad 10')
with tempfile.TemporaryDirectory(prefix='nc03-netlist-') as tmp:
 path=Path(tmp)/'netlist.xml'
 subprocess.run([cli,'sch','export','netlist',str(ROOT/'NC03_Controller.kicad_sch'),'--format','kicadxml','-o',str(path)],check=True,capture_output=True)
 tree=ET.parse(path)
 pin={}
 for net in tree.findall('./nets/net'):
  for node in net.findall('node'):
   key=(node.attrib['ref'],node.attrib['pin']);assert key not in pin,key
   pin[key]=net.attrib['name']
 checks=[]
 def expect(ref,pad,net):
  actual=pin.get((ref,str(pad)));assert actual==net,f'{ref}.{pad}: {actual} != {net}'
 def checked(name):checks.append(name)
 # Fixed physical pad numbers checked independently of generated component metadata.
 direct=[('UP',1),('DOWN',2),('LEFT',3),('RIGHT',4),('B1',7),('B2',8),('B3',9),('B4',10),('B5',11),('B6',15),('1P',21),('START',22)]
 for i,(name,pad) in enumerate(direct,1):
  expect('U1',pad,'IN_'+name);expect('R'+str(i),1,'SW_'+name);expect('R'+str(i),2,'IN_'+name)
  expect('R'+str(i+20),1,'+3V3');expect('R'+str(i+20),2,'IN_'+name)
  expect('C'+str(i),1,'IN_'+name);expect('C'+str(i),2,'GND')
  connector='J1' if i<=4 else 'J'+str(i-3);cp=i+1 if i<=4 else 2
  expect(connector,cp,'SW_'+name);expect(connector,1,'GND')
 checked('12 unique direct GPIOs, RC filters, pullups and physical switch headers')
 for pad,net in [(5,'I2C_SDA'),(6,'I2C_SCL'),(16,'RGB_DATA_3V3'),(17,'LED_ENABLE'),(18,'MODE_PC_N'),(19,'MODE_SWITCH_N'),(23,'LINK_USB_N')]:expect('U1',pad,net)
 expect('U1',20,'unconnected-(U1-D16_BAT_ADC-Pad20)')
 checked('Plus pad map, NFC/GPIO selector pins, reserved battery ADC')
 for pad,net in [(1,'MODE_PC_N'),(2,'GND'),(3,'MODE_SWITCH_N')]:expect('J10',pad,net)
 expect('J11',1,'LINK_USB_N');expect('J11',2,'GND')
 for r,net in [('R65','MODE_PC_N'),('R66','MODE_SWITCH_N'),('R67','LINK_USB_N')]:expect(r,1,'+3V3');expect(r,2,net)
 checked('fail-detecting profile selector and separate USB/BLE selector')
 expect('U1',28,'BAT_SW');expect('J15',1,'BAT_PLUS');expect('J15',2,'GND');expect('J16',1,'BAT_PLUS');expect('J16',2,'BAT_SW')
 expect('U1',14,'VBUS');expect('F1',1,'VBUS');expect('F1',2,'VBUS_FUSED')
 for pad,net in [(1,'VBUS_FUSED'),(2,'GND'),(3,'LED_ENABLE'),(4,'LED_CT'),(5,'+5V_LED'),(6,'+5V_LED')]:expect('U3',pad,net)
 expect('R60',1,'LED_ENABLE');expect('R60',2,'GND')
 checked('battery switch, USB-only fused LED supply, default-off enable and load-switch pinout')
 for i in range(16):
  pad=i+6 if i<8 else i+7
  expect('U2',pad,'LED_DRV_'+str(i));expect('R'+str(41+i),2,'LED_DRV_'+str(i));expect('R'+str(41+i),1,'LED_K_'+str(i))
  expect('J12' if i<8 else 'J13',2+i%8,'LED_K_'+str(i))
 for ref in ['J12','J13']:expect(ref,1,'+5V_LED')
 for pad in [1,2,3,4,5,14,23,24,25]:expect('U2',pad,'GND')
 for pad,net in [(26,'I2C_SCL'),(27,'I2C_SDA'),(28,'+3V3')]:expect('U2',pad,net)
 checked('all 16 individually resistor-limited LED sinks and I2C address 0x40')
 for pad,net in [(1,'GND'),(2,'RGB_DATA_3V3'),(3,'GND'),(4,'RGB_DATA_5V'),(5,'+5V_LED')]:expect('U4',pad,net)
 for pad,net in [(1,'+5V_LED'),(2,'RGB_DIN'),(3,'GND')]:expect('J14',pad,net)
 expect('R61',1,'RGB_DATA_5V');expect('R61',2,'RGB_DIN')
 checked('RGB translator supply, pinout, series termination and header polarity')
 components=tree.findall('./components/comp');assert len(components)==89,len(components)
 values={c.attrib['ref']:c.findtext('value') for c in components}
 assert all(values['R'+str(i)]=='1k' for i in range(41,57))
 report={'result':'pass','components':len(components),'direct_inputs':12,'pins_checked':len(pin),'checks':checks,'limits':'Static electrical invariants only; not firmware, USB/console/RF/ESD or physical validation.'}
 (ROOT/'checks/netlist-invariants.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
