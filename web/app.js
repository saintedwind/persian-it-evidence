'use strict';
const $ = selector => document.querySelector(selector);
const state = {collection: 'sample', catalogSequence: 0, documents: [], current: null, question: '', controller: null, sequence: 0, draftController: null, draftSequence: 0, ticketContext: null};
function cancelDraft() {
  state.draftSequence++;
  if (state.draftController) state.draftController.abort();
  state.draftController = null;
  $('#draft-button').disabled = false;
  $('#draft-panel').hidden = true;
}
const digits = n => String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
function notify(text) { $('#feedback').textContent = text; }
function renderDocument(doc) {
  cancelDraft();
  if (state.current && state.current.id !== doc.id) $('#ticket').hidden = true;
  state.current = doc;
  $('#document').hidden = false; $('#no-result').hidden = true;
  $('#doc-id').textContent = doc.id; $('#doc-title').textContent = doc.title;
  $('#answer').textContent = doc.text || doc.excerpt; $('#source-path').textContent = doc.source;
  $('#ticket-open').hidden = state.collection === 'reference';
  $('#document-kind').textContent = state.collection === 'reference' ? 'متن عمومی؛ دستورالعمل سازمانی نیست' : 'متن راهنمای نمونه';
  $('#source-hash').textContent = doc.text_sha256 ? 'Text SHA-256: ' + doc.text_sha256 : '';
  const sourceLink = $('#source-link'); sourceLink.hidden = true; sourceLink.removeAttribute('href');
  if (/^https:\/\/fa\.wikipedia\.org\/w\/index\.php\?oldid=\d+$/.test(doc.source)) { sourceLink.href = doc.source; sourceLink.hidden = false; }
  document.querySelectorAll('.catalog-item').forEach(el => el.setAttribute('aria-current', String(el.dataset.id === doc.id)));
  document.querySelectorAll('.candidate').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.id === doc.id)));
}
function resetView() {
  cancelDraft();
  $('#welcome').hidden = true; $('#result').hidden = false;
  $('#document').hidden = true; $('#ticket').hidden = true; $('#no-result').hidden = true;
  $('#candidates').replaceChildren(); state.current = null; notify('');
}
function openGuide(doc) {
  state.sequence++; if (state.controller) state.controller.abort();
  $('#search-button').disabled = false; $('#result').setAttribute('aria-busy', 'false');
  resetView(); state.question = '';
  $('#result-label').textContent = 'از فهرست راهنماها'; $('#status').textContent = 'راهنمای انتخاب‌شده';
  renderDocument(doc); $('#result').scrollIntoView({block: 'start'});
}
async function loadCatalog() {
  const catalogSequence = ++state.catalogSequence; const collection = state.collection;
  $('#retry-catalog').hidden = true;
  try {
    const response = await fetch('/api/documents?collection=' + collection); if (!response.ok) throw new Error();
    const data = await response.json(); if (catalogSequence !== state.catalogSequence) return; state.documents = data.documents;
    $('#doc-count').textContent = digits(data.documents.length); $('#catalog').replaceChildren();
    data.documents.forEach((doc, i) => {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'catalog-item'; button.dataset.id = doc.id;
      const number = document.createElement('span'); number.textContent = digits(i + 1).padStart(2, '۰');
      const title = document.createElement('span'); title.textContent = doc.title;
      button.append(number, title); button.addEventListener('click', () => openGuide(doc)); $('#catalog').append(button);
    });
  } catch { if (catalogSequence !== state.catalogSequence) return; $('#catalog').textContent = 'فهرست دریافت نشد. اتصال به برنامه را بررسی کنید.'; $('#retry-catalog').hidden = false; }
}
async function search(question) {
  question = question.trim(); if (!question) { $('#question').focus(); return; }
  const sequence = ++state.sequence; if (state.controller) state.controller.abort();
  state.controller = new AbortController(); const controller = state.controller;
  const timeout = setTimeout(() => controller.abort(), 10000);
  resetView(); state.question = question; $('#search-button').disabled = true;
  $('#result').setAttribute('aria-busy', 'true'); $('#result-label').textContent = 'جست‌وجو در راهنماها'; $('#status').textContent = 'در حال بررسی…';
  try {
    const response = await fetch('/api/ask', {method:'POST', signal:controller.signal, headers:{'Content-Type':'application/json'}, body:JSON.stringify({question, collection:state.collection})});
    if (!response.ok) throw new Error(); const data = await response.json(); if (sequence !== state.sequence) return;
    if (data.status !== 'evidence_found') { $('#status').textContent = 'راهنمای کافی پیدا نشد'; $('#no-result').hidden = false; return; }
    $('#status').textContent = 'این راهنماها را بررسی کنید'; $('#result-label').textContent = digits(data.retrieved.length) + ' نتیجه مرتبط · انتخاب با شما';
    for (const doc of data.retrieved) {
      const button = document.createElement('button'); button.type = 'button'; button.className = 'candidate'; button.dataset.id = doc.id; button.setAttribute('aria-pressed', 'false');
      const title = document.createElement('strong'); title.textContent = doc.title;
      const id = document.createElement('span'); id.textContent = doc.id;
      button.append(title, id); button.addEventListener('click', () => renderDocument(doc)); $('#candidates').append(button);
    }
    renderDocument(data.citations[0]);
  } catch { if (sequence !== state.sequence) return; $('#status').textContent = 'جست‌وجو انجام نشد'; notify('پاسخی از برنامه دریافت نشد. اتصال را بررسی کنید و دوباره «پیدا کن» را بزنید.'); }
  finally { clearTimeout(timeout); if (sequence === state.sequence) { $('#search-button').disabled = false; $('#result').setAttribute('aria-busy', 'false'); } }
}
function openTicket() {
  const doc = state.current;
  const context = JSON.stringify([state.sequence, state.question, doc && doc.id]);
  if (context !== state.ticketContext) {
    state.ticketContext = context;
    $('#ticket-text').value = `موضوع: ${state.question || (doc && doc.title) || ''}\n\nزمان شروع مشکل: \nدستگاه یا نرم‌افزار: \nمتن دقیق خطا: \nمراحل تکرار مشکل: \nاقدام‌های انجام‌شده: \n${doc ? 'راهنمای بررسی‌شده: ' + doc.id + ' — ' + doc.title + '\n' : ''}\nرمز عبور، کد ورود و اطلاعات شخصی دیگران را در تیکت ننویسید.`;
  }
  $('#ticket').hidden = false; $('#ticket-text').focus();
}
async function copy(text, field) {
  try { await navigator.clipboard.writeText(text); notify('کپی شد.'); }
  catch { if (field) { field.focus(); field.select(); } notify('کپی خودکار در دسترس نیست؛ متن را انتخاب و کپی کنید.'); }
}
$('#ask').addEventListener('submit', event => { event.preventDefault(); search($('#question').value); });
document.querySelectorAll('[data-query]').forEach(button => button.addEventListener('click', () => { $('#question').value = button.dataset.query; search(button.dataset.query); }));
$('#retry-catalog').addEventListener('click', loadCatalog);
$('#ticket-open').addEventListener('click', openTicket); $('#empty-ticket').addEventListener('click', openTicket);
$('#ticket-close').addEventListener('click', () => { $('#ticket').hidden = true; });
$('#copy-ticket').addEventListener('click', () => copy($('#ticket-text').value, $('#ticket-text')));
$('#copy-guide').addEventListener('click', () => { const d=state.current; if(d) copy(`${d.title}\n${d.text || d.excerpt}\nمنبع: ${d.id} | ${d.source}`); });
document.addEventListener('keydown', event => { if(event.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName) && !document.activeElement.isContentEditable) {event.preventDefault(); $('#question').focus();} });
loadCatalog();

fetch('/health').then(r => r.json()).then(data => { $('#draft-button').hidden = !data.local_draft; }).catch(() => {});
$('#draft-button').addEventListener('click', async () => {
  const question = $('#question').value.trim();
  if (!question || question.length > 400) { notify('برای پاسخ کوتاه، پرسش را در ۱ تا ۴۰۰ نویسه بنویسید.'); $('#question').focus(); return; }
  const sequence = state.sequence;
  cancelDraft(); const draftSequence = state.draftSequence;
  const button = $('#draft-button'); button.disabled = true;
  $('#draft-panel').hidden = false; $('#draft-output').textContent = 'در حال آماده‌سازی؛ ممکن است تا ۹۰ ثانیه طول بکشد…'; $('#draft-source').textContent = '';
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 95000);
  state.draftController = controller;
  try {
    const response = await fetch('/api/draft', {method:'POST', signal:controller.signal, headers:{'Content-Type':'application/json'}, body:JSON.stringify({question, collection:state.collection})});
    if (!response.ok) throw new Error(); const data = await response.json();
    if (sequence !== state.sequence || draftSequence !== state.draftSequence || question !== $('#question').value.trim()) return;
    $('#draft-output').textContent = data.status === 'draft_ready' ? data.draft : data.status === 'busy' ? 'درخواست قبلی هنوز در حال پردازش است.' : 'پاسخ قابل استفاده آماده نشد. متن اصلی راهنما را بررسی کنید.';
    if (data.status === 'draft_ready') $('#draft-source').textContent = 'منبع: ' + data.citations.map(d => d.id + ' — ' + d.title).join('، ');
  } catch { if (sequence === state.sequence && draftSequence === state.draftSequence) $('#draft-output').textContent = 'پاسخ دریافت نشد؛ راهنمای اصلی همچنان در دسترس است.'; }
  finally { clearTimeout(timer); if (draftSequence === state.draftSequence) {button.disabled = false; state.draftController = null;} }
});
$('#question').addEventListener('input', cancelDraft);

$('#collection').addEventListener('change', () => {
  state.collection = $('#collection').value;
  const reference = state.collection === 'reference';
  $('#main-title').textContent = reference ? 'دنبال چه مطلبی هستید؟' : 'کارتان کجا گیر کرده؟';
  $('#main-lead').textContent = reference ? 'در متن‌های عمومی فارسی جست‌وجو کنید و نتیجه را با نسخه اصلی منبع تطبیق دهید.' : 'راهنمای مربوط را پیدا کنید، مراحلش را بخوانید و اگر لازم شد، مسئله را به پشتیبانی بسپارید.';
  $('#intro-note').textContent = reference ? '۶ متن واقعی فارسی · منبع و نسخه مشخص · بدون ادعای تأیید محتوای دانشنامه' : '۱۲ راهنمای نمونه پشتیبانی؛ دستورالعمل سازمانی نیست.';
  $('#catalog-title').textContent = reference ? 'فهرست متن‌ها' : 'فهرست راهنماها';
  const examples = reference ? ['فیشینگ چیست','سامانه نام دامنه چه می کند','احراز هویت چندعاملی چیست'] : ['رمز عبور را فراموش کردم','صف چاپ پرینتر متوقف شده','صدای تلفن VoIP یک طرفه است'];
  const labels = reference ? ['فیشینگ','نام دامنه','احراز هویت'] : ['رمز ورود','صف چاپ','صدای تماس'];
  document.querySelectorAll('[data-query]').forEach((button,i) => {button.dataset.query = examples[i]; button.textContent = labels[i];});
  state.sequence++; if (state.controller) state.controller.abort();
  resetView(); $('#question').value = ''; $('#search-button').disabled = false;
  $('#result').setAttribute('aria-busy','false'); $('#result').hidden = true; $('#welcome').hidden = reference;
  $('#catalog').replaceChildren();
  $('#dataset-note').textContent = state.collection === 'reference'
    ? 'مقدمه‌های واقعی از ویکی‌پدیای فارسی با نسخه و مجوز CC BY-SA 4.0؛ متن دانشنامه‌ای است، ممکن است قدیمی باشد و راهنمای مصوب پشتیبانی نیست.'
    : 'محتوای این نسخه، راهنمای نمونه است؛ دستورالعمل هیچ سازمانی نیست.';
  loadCatalog();
});
