// Browser acceptance checks. Model responses are controlled here; real CPU
// inference is recorded separately in reports/lifecycle-v04.json.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const fs = require('node:fs');
const assert = require('node:assert/strict');

(async () => {
  fs.mkdirSync('reports/ui', {recursive:true});
  const server = spawn(process.env.PYTHON || 'python', ['server.py'], {windowsHide:true});
  let browser;
  const checks = [], errors = [];
  try {
    for (let n=0; n<50; n++) {
      try {if ((await fetch('http://127.0.0.1:8765/health')).ok) break;} catch {}
      if (n===49) throw Error('Local server did not become ready');
      await new Promise(resolve => setTimeout(resolve,100));
    }
    browser = await chromium.launch({headless:true});
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/health', route => route.fulfill({json:{status:'ok',local_draft:true}}));
    await page.goto('http://127.0.0.1:8765');
    await page.locator('.catalog-item').nth(11).waitFor();
    assert.equal(await page.locator('.catalog-item').count(),12);
    checks.push('12 public guides load');
    await page.getByRole('button',{name:'صف چاپ',exact:true}).click();
    await page.locator('#doc-id').filter({hasText:'IT-004'}).waitFor();
    checks.push('printer query selects expected source');
    await page.locator('#ticket-open').click();
    await page.locator('#ticket-text').fill('Edited ticket - keep this text');
    await page.locator('#ticket-close').click();
    await page.locator('#ticket-open').click();
    assert.equal(await page.locator('#ticket-text').inputValue(),'Edited ticket - keep this text');
    checks.push('close/reopen preserves edited ticket');

    let release, received;
    const requested = new Promise(resolve => {received=resolve;});
    const delayed = new Promise(resolve => {release=resolve;});
    await page.route('**/api/draft', async route => {
      received(); await delayed;
      try {await route.fulfill({json:{status:'draft_ready',draft:'OLD RESPONSE',citations:[]}});} catch {}
    });
    await page.locator('#draft-button').click();
    await requested;
    await page.locator('.catalog-item').nth(0).click();
    release();
    await page.waitForTimeout(250);
    assert.equal(await page.locator('#draft-panel').isVisible(),false);
    assert.equal(await page.locator('#draft-button').isEnabled(),true);
    assert.equal(await page.locator('#ticket').isVisible(),false);
    checks.push('source change discards late draft and hides prior ticket');
    await page.unroute('**/api/draft');
    await page.route('**/api/draft', route => route.fulfill({json:{status:'busy',citations:[]}}));
    await page.locator('#question').fill('VPN');
    await page.locator('#draft-button').click();
    await page.getByText('درخواست قبلی هنوز در حال پردازش است.',{exact:true}).waitFor();
    await page.locator('#question').fill('Changed question');
    assert.equal(await page.locator('#draft-panel').isVisible(),false);
    checks.push('busy feedback and question edit reset draft');
    await page.locator('#question').fill('quasar astronomy');
    await page.locator('#search-button').click();
    await page.locator('#no-result').waitFor();
    await page.locator('#empty-ticket').click();
    assert.match(await page.locator('#ticket-text').inputValue(),/quasar astronomy/);
    checks.push('unsupported query offers editable escalation');
    await page.locator('.catalog-item').nth(3).click();
    await page.locator('#ticket-open').click();
    await page.screenshot({path:'reports/ui/desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.reload();
    await page.locator('.catalog-item').nth(11).waitFor();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),false);
    await page.screenshot({path:'reports/ui/mobile.png',fullPage:true});
    checks.push('390px layout has no horizontal overflow');
    assert.deepEqual(errors,[]);
    checks.push('no uncaught browser errors');
    fs.writeFileSync('reports/ui/results.json',JSON.stringify({checks,model:'mocked',browser:'Chromium',errors},null,2));
    console.log('PASS:',checks.join('; '));
  } finally {
    if (browser) await browser.close();
    server.kill();
    if (server.exitCode===null) await once(server,'exit');
  }
})().catch(error => {console.error(error);process.exitCode=1;});
