import {Pass} from 'postprocessing';

// The documented custom-pass API supplies the scene. No private model-viewer symbols.
export class EnvironmentRotationPass extends Pass {
  constructor(){
    super('Environment rotation');
    this.enabled=false;this.needsSwap=false;this._angle=0;
  }
  set mainScene(scene){this.scene=scene;this.applyRotation();}
  get angle(){return this._angle;}
  set angle(degrees){this._angle=degrees;this.applyRotation();}
  applyRotation(){
    if(!this.scene)return;
    const radians=(this._angle??0)*Math.PI/180;
    this.scene.environmentRotation.set(0,radians,0);
    this.scene.backgroundRotation.set(0,radians,0);
  }
  render(){}
}
