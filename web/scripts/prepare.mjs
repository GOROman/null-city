import {readFile, mkdir, copyFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import validator from 'gltf-validator';
const web=fileURLToPath(new URL('../',import.meta.url));
const root=path.resolve(web,'..');
const manifest=JSON.parse(await readFile(path.join(web,'public/model/manifest.json'),'utf8'));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
for(const [name,expected] of Object.entries(manifest.inputs)){
  if(hash(await readFile(path.join(root,name)))!==expected)throw new Error(`Web model is stale: ${name}. Run scripts/export_web_model.py with Blender.`);
}
const glb=await readFile(path.join(web,'public/model/nc03.glb'));
if(hash(glb)!==manifest.glb_sha256)throw new Error('GLB hash differs from its export manifest');
const report=await validator.validateBytes(new Uint8Array(glb),{uri:'nc03.glb',maxIssues:30});
if(report.issues.numErrors)throw new Error(JSON.stringify(report.issues,null,2));
const doc=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString());
if(doc.animations?.[0]?.name!=='Assembly'||!doc.images?.length)throw new Error('Missing assembly animation or deck artwork');
if(!doc.extensionsUsed.includes('KHR_materials_transmission'))throw new Error('Missing PBR glass transmission');
await mkdir(path.join(web,'public/project'),{recursive:true});
for(const [source,target] of [
  ['docs/images/lighting.jpg','poster.jpg'],
  ['fonts/null-font/NULLFont-Italic.woff2','NULLFont-Italic.woff2'],
  ['fonts/null-font/OFL.txt','OFL.txt'],
  ['LICENSES/CC-BY-4.0.txt','CC-BY-4.0.txt'],
  ['LICENSES/MIT.txt','MIT.txt'],
])await copyFile(path.join(root,source),path.join(web,'public/project',target));
await writeFile(path.join(web,'public/project/build.json'),JSON.stringify({model:manifest.glb_sha256,source:manifest.inputs['NULL_CITY_NC03.blend']}));
console.log(`Verified GLB: ${report.issues.numErrors} errors, ${report.issues.numWarnings} warnings; ${(glb.length/1024/1024).toFixed(2)} MiB. Sources match Blender export.`);

const lock=JSON.parse(await readFile(path.join(web,'package-lock.json'),'utf8'));
let notices='NULL CITY Web preview — third-party licenses\n\n';
for(const [location,metadata] of Object.entries(lock.packages)){
  if(!location||metadata.dev)continue;
  const directory=path.join(web,location);
  for(const filename of ['LICENSE','LICENSE.txt','LICENSE.md','license','license.txt']){
    try{
      const text=await readFile(path.join(directory,filename),'utf8');
      notices+=`\n${location.replace('node_modules/','')} ${metadata.version}\n${'='.repeat(60)}\n${text}\n`;
      break;
    }catch(error){if(error.code!=='ENOENT')throw error;}
  }
}
await writeFile(path.join(web,'public/project/THIRD_PARTY_LICENSES.txt'),notices);
