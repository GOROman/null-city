import {Pass} from 'postprocessing';

// The documented custom-pass API supplies the scene. No private model-viewer symbols.
export class EnvironmentRotationPass extends Pass {
  constructor(){
    super('Environment rotation');
    this.enabled=false;this.needsSwap=false;this._angle=0;this._intensity=1;
  }
  set mainScene(scene){this.scene=scene;this.applyRotation();this.applyIntensity();}
  set mainCamera(camera){this.camera=camera;}
  get angle(){return this._angle;}
  set angle(degrees){this._angle=degrees;this.applyRotation();}
  applyRotation(){
    if(!this.scene)return;
    const radians=(this._angle??0)*Math.PI/180;
    this.scene.environmentRotation.set(0,radians,0);
    this.scene.backgroundRotation.set(0,radians,0);
  }
  get intensity(){return this._intensity;}
  set intensity(value){this._intensity=value;this.applyIntensity();}
  applyIntensity(){
    if(!this.scene)return;
    this.scene.environmentIntensity=this._intensity??1;
    this.scene.backgroundIntensity=this._intensity??1;
  }
  render(){}
}
