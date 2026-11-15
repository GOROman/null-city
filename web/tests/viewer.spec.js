import {test,expect} from '@playwright/test';

async function load(page){
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('./');
  await expect(page.locator('.stage')).toHaveAttribute('data-loaded','true',{timeout:45000});
  await expect(page.locator('#error-panel')).toBeHidden();
  await expect(page.locator('.stage')).toHaveAttribute('data-environment','studio03',{timeout:45000});
  expect(errors).toEqual([]);
  return errors;
}

test('PBR model, meter scale, artwork, camera and assembly controls',async({page},testInfo)=>{
  const errors=await load(page);
  const model=await page.locator('#viewer').evaluate(v=>({size:v.getDimensions(),animations:v.availableAnimations,materials:v.model.materials.map(m=>m.name)}));
  expect(model.size.x).toBeCloseTo(.3,3);expect(model.size.z).toBeCloseTo(.19,3);
  expect(model.animations).toEqual(['Assembly']);
  expect(model.materials).toContain('Printed NC-03 graphic');
  await page.getByRole('button',{name:'右側面',exact:true}).click();
  await expect(page.getByRole('button',{name:'右側面',exact:true})).toHaveAttribute('aria-pressed','true');
  await page.locator('#assembly').evaluate(e=>{e.value='100';e.dispatchEvent(new Event('input',{bubbles:true}));});
  await expect(page.locator('#assembly-value')).toHaveText('100%');
  const pose=await page.locator('#viewer').evaluate(v=>({time:v.currentTime,duration:v.duration}));
  expect(pose.time).toBeGreaterThan(.9*pose.duration);
  await page.locator('#led').uncheck({force:true});
  expect(await page.locator('#viewer').evaluate(v=>v.model.materials.every(m=>m.emissiveFactor.every(x=>x===0)))).toBe(true);
  await page.locator('#transparent').check({force:true});
  expect(await page.locator('#viewer').evaluate(v=>v.model.materials.find(m=>m.name==='Pearl white PETG').pbrMetallicRoughness.baseColorFactor[3])).toBeCloseTo(.18,2);
  await page.locator('#exposure').evaluate(e=>{e.value='1.4';e.dispatchEvent(new Event('input',{bubbles:true}));});
  await expect(page.locator('#exposure-value')).toHaveText('1.4');
  await page.locator('#rotate').check({force:true});
  expect(await page.locator('#viewer').evaluate(v=>v.autoRotate)).toBe(true);
  expect(await page.locator('#viewer').evaluate(v=>v.autoRotateDelay)).toBe(0);
  await expect.poll(()=>page.locator('#viewer').evaluate(v=>v.modelIsVisible),{timeout:8000}).toBe(true);
  const initialAngle=await page.locator('#viewer').evaluate(v=>v.turntableRotation);
  if(process.env.CI)console.log('Rotation start',await page.evaluate(()=>({
    dpr:devicePixelRatio,visibility:document.visibilityState,
    modelVisible:document.querySelector('#viewer').modelIsVisible,
    autoRotate:document.querySelector('#viewer').autoRotate,
    renderCount:document.querySelector('#composer').userPasses[0].scene.renderCount,
  })));
  await expect.poll(()=>page.locator('#viewer').evaluate((v,initial)=>Math.abs(v.turntableRotation-initial),initialAngle),{timeout:8000}).toBeGreaterThan(.05);
  await page.locator('#rotate').uncheck({force:true});
  await page.locator('#viewer').scrollIntoViewIfNeeded();
  const stoppedAngle=await page.locator('#viewer').evaluate(v=>v.turntableRotation);
  await page.waitForTimeout(400);
  expect(await page.locator('#viewer').evaluate((v,angle)=>Math.abs(v.turntableRotation-angle),stoppedAngle)).toBeLessThan(.002);
  await page.getByRole('button',{name:'視点と表示設定をリセット'}).click();
  await expect(page.locator('#assembly-value')).toHaveText('0%');
  await page.locator('#environment').selectOption('studio02');
  await expect(page.locator('.stage')).toHaveAttribute('data-environment','studio02',{timeout:45000});
  await expect.poll(()=>page.locator('#composer').evaluate(c=>c.userPasses[0].scene?.environment?.name),{timeout:15000}).toContain('studio_small_02_1k.hdr');
  await page.locator('#environment-angle').evaluate(e=>{e.value='180';e.dispatchEvent(new Event('input',{bubbles:true}));});
  expect(await page.locator('#composer').evaluate(c=>c.userPasses[0].scene.environmentRotation.y)).toBeCloseTo(Math.PI,4);
  await expect(page.locator('#environment-angle-value')).toHaveText('180°');
  await page.locator('#background').check({force:true});
  expect(await page.locator('#viewer').evaluate(v=>v.skyboxImage)).toContain('studio_small_02_1k.hdr');
  await page.locator('#ssao-enabled').uncheck({force:true});
  await expect.poll(()=>page.locator('#ssao').evaluate(e=>e.effects[0].disabled)).toBe(true);
  await page.locator('#ssao-enabled').check({force:true});
  await expect.poll(()=>page.locator('#ssao').evaluate(e=>e.effects[0].disabled)).toBe(false);
  await page.getByRole('button',{name:'視点と表示設定をリセット'}).click();
  await expect(page.locator('.stage')).toHaveAttribute('data-environment','studio03',{timeout:45000});
  await expect(page.locator('#led')).toBeChecked();await expect(page.locator('#rotate')).not.toBeChecked();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await expect(page.locator('.wordmark')).toHaveCSS('font-family',/Null/);
  await page.getByRole('button',{name:'自動回転を切り替える'}).click();
  await expect(page.locator('#rotate')).toBeChecked();
  const overlayAngle=await page.locator('#viewer').evaluate(v=>v.turntableRotation);
  await expect.poll(()=>page.locator('#viewer').evaluate((v,initial)=>Math.abs(v.turntableRotation-initial),overlayAngle),{timeout:8000}).toBeGreaterThan(.05);
  await page.getByRole('button',{name:'自動回転を切り替える'}).click();
  await expect(page.locator('#rotate')).not.toBeChecked();
  await page.waitForTimeout(1200);
  await page.screenshot({path:testInfo.outputPath('viewer.png'),fullPage:true});
  expect(errors).toEqual([]);
});

test('failed model request shows an actionable error instead of an endless loader',async({page})=>{
  await page.route('**/model/nc03.glb',route=>route.abort());
  await page.goto('./');
  await expect(page.locator('#error-panel')).toBeVisible({timeout:30000});
  await expect(page.getByRole('button',{name:'再読み込み',exact:true})).toBeVisible();
  await expect(page.getByRole('link',{name:/GLBをダウンロード/})).toBeVisible();
});
