import {test,expect} from '@playwright/test';

async function load(page){
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('./');
  await expect(page.locator('.stage')).toHaveAttribute('data-loaded','true',{timeout:45000});
  await expect(page.locator('#error-panel')).toBeHidden();
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
  await page.getByRole('button',{name:'視点と表示設定をリセット'}).click();
  await expect(page.locator('#assembly-value')).toHaveText('0%');
  await expect(page.locator('#led')).toBeChecked();await expect(page.locator('#rotate')).not.toBeChecked();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await expect(page.locator('.wordmark')).toHaveCSS('font-family',/Null/);
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
