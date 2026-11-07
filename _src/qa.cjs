const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:"msedge"});const page=await browser.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.BASE_URL || 'http://127.0.0.1:8765';
 await page.goto(base+'/tools/food-finder/');await page.locator('.ff-group').first().waitFor();
 await page.selectOption('#ff-diet','vegan');await page.fill('#ff-q','salmon');await page.waitForTimeout(150);assert.equal(await page.locator('.ff-group').count(),0);
 await page.fill('#ff-q','milk');await page.waitForTimeout(150);for(const h of await page.locator('.ff-group h3').allTextContents())assert.match(h,/soy|almond|plant/i);
 await page.selectOption('#ff-diet','all');await page.fill('#ff-q','chana');await page.waitForTimeout(150);assert.ok(await page.locator('.ff-group').count());
 await page.goto(base+'/tools/vitamin-check/');
 async function answer(preg){for(const [name,value] of Object.entries({diet:'vegan',age:'71',preg,sun:'rare',skin:'dark',greens:'daily',fruit:'daily',nuts:'often',dairy:'rare',salt:'yes',periods:'no'}))await page.check(`input[name="${name}"][value="${value}"]`);await page.click('button[type=submit]');}
 await answer('breastfeeding');assert.equal(await page.locator('#vcheck-out .item').count(),3);assert.ok(!(await page.locator('#vcheck-out').innerText()).includes('27 mg'));assert.equal(await page.evaluate(()=>localStorage.getItem('vitapals-check-v2')),null);
 await page.check('[name=remember]');await page.click('button[type=submit]');assert.ok(await page.evaluate(()=>localStorage.getItem('vitapals-check-v2')));await page.click('#forget-check');assert.equal(await page.evaluate(()=>localStorage.getItem('vitapals-check-v2')),null);
 await answer('pregnant');assert.match(await page.locator('#vcheck-out').innerText(),/not validated/);
 await page.goto(base+'/protein/');await page.fill('#pc-w','70');assert.match(await page.locator('#pc-out').innerText(),/84–112/);await page.selectOption('#pc-u','lb');await page.fill('#pc-w','154.3236');assert.match(await page.locator('#pc-out').innerText(),/84–112/);
 for(const route of ['/','/tools/vitamin-check/','/tools/food-finder/','/vitamin-b6/']){await page.setViewportSize({width:375,height:812});await page.goto(base+route);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`overflow ${route}`);}
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS: filters, aliases, reproductive stages, privacy, unit conversion, mobile overflow, browser errors');
})().catch(e=>{console.error(e);process.exit(1)});

