import '@google/model-viewer';
import '@google/model-viewer-effects';
import {EnvironmentRotationPass} from './environment-pass.js';
import './style.css';

const viewer=document.querySelector('#viewer');
const controls=document.querySelector('#model-controls');
const stage=document.querySelector('.stage');
const status=document.querySelector('#load-status');
const assembly=document.querySelector('#assembly');
const exposure=document.querySelector('#exposure');
const led=document.querySelector('#led');
const transparent=document.querySelector('#transparent');
const rotate=document.querySelector('#rotate');
const environment=document.querySelector('#environment');
const environmentAngle=document.querySelector('#environment-angle');
const background=document.querySelector('#background');
const ssaoEnabled=document.querySelector('#ssao-enabled');
const ssao=document.querySelector('#ssao');
const composer=document.querySelector('#composer');
const environmentPass=new EnvironmentRotationPass();
composer.addPass(environmentPass);
const environmentSources={studio03:'./environments/studio_small_03_1k.hdr',studio02:'./environments/studio_small_02_1k.hdr',neutral:'neutral'};
const viewButtons=[...document.querySelectorAll('[data-view]')];
const viewAngles={hero:[25,65],front:[0,90],right:[90,90],top:[0,.1]};
let ready=false,restTarget,restRadius,emissive=[],caseMaterials=[];
let view='hero';

function frameCurrentView(){
  if(!ready)return;
  const fraction=Number(assembly.value)/100;
  const [theta,phi]=viewAngles[view];
  viewer.cameraOrbit=`${theta}deg ${phi}deg ${restRadius*(1+.45*fraction)}m`;
  viewer.cameraTarget=`${restTarget.x}m ${restTarget.y+.028*fraction}m ${restTarget.z}m`;
}
function setView(name){
  view=name;
  viewButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===view)));
  frameCurrentView();
}
function setAssembly(){
  const fraction=Number(assembly.value)/100;
  document.querySelector('#assembly-value').value=`${assembly.value}%`;
  if(!ready)return;
  viewer.pause();viewer.currentTime=Math.min(viewer.duration-.0001,Math.max(0,viewer.duration*fraction));
  frameCurrentView();
}
function setLights(){
  for(const {material,factor} of emissive)material.setEmissiveFactor(led.checked?factor:[0,0,0]);
}
function setTransparency(){
  for(const {material,color,alpha,doubleSided} of caseMaterials){
    material.setAlphaMode(transparent.checked?'BLEND':alpha);
    material.setDoubleSided(transparent.checked||doubleSided);
    material.pbrMetallicRoughness.setBaseColorFactor([...color.slice(0,3),transparent.checked?.18:color[3]]);
  }
}
function setExposure(){viewer.exposure=Number(exposure.value);document.querySelector('#exposure-value').value=Number(exposure.value).toFixed(1);}
function setRotation(){
  // Start immediately and at a visible speed; on mobile the switch can be below the viewport.
  viewer.autoRotateDelay=0;viewer.rotationPerSecond='20deg';viewer.autoRotate=rotate.checked;
  const rect=viewer.getBoundingClientRect();
  if(rotate.checked&&(rect.bottom<100||rect.top>innerHeight-100)){
    viewer.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  }
}
function setEnvironmentAngle(){
  environmentPass.angle=Number(environmentAngle.value);
  document.querySelector('#environment-angle-value').value=`${environmentAngle.value}°`;
  composer.queueRender();
}
function setBackground(){viewer.skyboxImage=background.checked&&environment.value!=='neutral'?environmentSources[environment.value]:null;}
function setEnvironment(){
  const source=environmentSources[environment.value];
  if(viewer.environmentImage!==source){stage.dataset.environmentLoading='true';status.textContent='HDR環境を読み込み中…';}
  viewer.environmentImage=source;
  background.disabled=environment.value==='neutral';
  if(background.disabled)background.checked=false;
  const credit=document.querySelector('#environment-credit a');
  credit.href=environment.value==='studio02'?'https://polyhaven.com/a/studio_small_02':'https://polyhaven.com/a/studio_small_03';
  document.querySelector('#environment-credit').hidden=environment.value==='neutral';
  setBackground();setEnvironmentAngle();
}
function setSSAO(){ssao.blendMode=ssaoEnabled.checked?'DEFAULT':'SKIP';}
viewer.addEventListener('environment-change',()=>{
  requestAnimationFrame(()=>{
    setEnvironmentAngle();stage.dataset.environmentLoading='false';stage.dataset.environment=environment.value;
    if(ready)status.textContent='ドラッグして操作できます';
  });
});
function reset(){
  assembly.value='0';exposure.value='0.8';led.checked=true;transparent.checked=false;rotate.checked=false;
  environment.value='studio03';environmentAngle.value='90';background.checked=false;ssaoEnabled.checked=true;
  setAssembly();setExposure();setLights();setTransparency();setRotation();setView('hero');
  viewer.resetTurntableRotation(0);setEnvironment();setSSAO();
}

viewer.addEventListener('progress',event=>{document.querySelector('#progress').value=event.detail.totalProgress;});
viewer.addEventListener('load',()=>{
  ready=true;controls.disabled=false;stage.dataset.loaded='true';status.textContent='ドラッグして操作できます';
  document.querySelector('#error-panel').hidden=true;
  restTarget=viewer.getCameraTarget();restRadius=viewer.getCameraOrbit().radius;
  emissive=viewer.model.materials.filter(material=>material.emissiveFactor.some(value=>value>0)).map(material=>({material,factor:[...material.emissiveFactor]}));
  caseMaterials=viewer.model.materials.filter(material=>material.name==='Pearl white PETG').map(material=>({material,color:[...material.pbrMetallicRoughness.baseColorFactor],alpha:material.getAlphaMode(),doubleSided:material.getDoubleSided()}));
  viewer.animationName='Assembly';viewer.pause();viewer.currentTime=0;reset();
});
viewer.addEventListener('error',()=>{
  ready=false;controls.disabled=true;status.textContent='読み込みエラー';document.querySelector('#error-panel').hidden=false;
});
assembly.addEventListener('input',setAssembly);
exposure.addEventListener('input',setExposure);
led.addEventListener('change',setLights);
transparent.addEventListener('change',setTransparency);
rotate.addEventListener('change',setRotation);
environment.addEventListener('change',setEnvironment);
environmentAngle.addEventListener('input',setEnvironmentAngle);
background.addEventListener('change',setBackground);
ssaoEnabled.addEventListener('change',setSSAO);
viewButtons.forEach(button=>button.addEventListener('click',()=>{if(ready)setView(button.dataset.view);}));
document.querySelector('#reset').addEventListener('click',reset);
document.querySelector('#retry').addEventListener('click',()=>window.location.reload());
document.querySelector('#controls').addEventListener('submit',event=>event.preventDefault());
// Keep all initial controls deterministic; motion only starts when the user enables it.
fetch('./project/build.json').then(response=>{if(!response.ok)throw new Error('No build metadata');return response.json();}).then(data=>{document.querySelector('#revision').textContent=`MODEL / ${data.model.slice(0,8).toUpperCase()}`;}).catch(()=>{});
