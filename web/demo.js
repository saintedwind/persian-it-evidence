'use strict';
const $ = s => document.querySelector(s);
const number = n => new Intl.NumberFormat('fa-IR', {maximumFractionDigits: 2}).format(n);
let sequence = 0, catalogSequence = 0, controller = null, selected = null;
let documents = [];
let modelEnabled = false, modelController = null, modelSequence = 0, answeredQuestion = '', answeredCollection = '';
const collection = () => $('#collection').value;
const safeSource = value => /^https:\/\/fa\.wikipedia\.org\/w\/index\.php\?oldid=\d+$/.test(value);
function steps(done = [], working = '') {
  for (const key of ['query','search','evidence','source']) {
    const node = $('#step-' + key);
    node.classList.toggle('done', done.includes(key));
    node.classList.toggle('working', key === working);
  }
}
function invalidate() {
  modelSequence++; if(modelController) modelController.abort();
  $('#model-panel').hidden = true; $('#generate').disabled = false;
  $('#model-answer').textContent = ''; $('#model-quote').hidden = true; $('#model-meta').textContent = '';
  sequence++;
  if (controller) controller.abort();
  controller = null;
  selected = null;
  $('#submit').disabled = false;
  $('#results').setAttribute('aria-busy', 'false');
  $('#results').hidden = true;
  $('#empty').hidden = false;
  $('#notice').textContent = '';
  steps();
  if ($('#source-dialog').open) $('#source-dialog').close();
}
async function jsonFetch(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error('HTTP ' + response.status);
  return response.json();
}
function showSource(doc) {
  $('#source-title').textContent = doc.title;
  $('#source-text').textContent = doc.text || doc.excerpt;
  const meta = $('#source-meta'); meta.replaceChildren();
  meta.append(document.createTextNode(doc.id + ' · '));
  if (safeSource(doc.source)) {
    const a = document.createElement('a'); a.href = doc.source; a.target = '_blank'; a.rel = 'noopener noreferrer';
    a.textContent = 'مشاهده نسخه اصلی در ویکی‌پدیای فارسی'; meta.append(a);
    meta.append(document.createTextNode(' · مشارکت‌کنندگان ویکی‌پدیای فارسی · CC BY-SA 4.0'));
  } else meta.append(document.createTextNode(doc.source));
  if (!$('#source-dialog').open) $('#source-dialog').showModal();
}
function receipt(data, source) {
  const rows = [['روش اجرا', data.mode || 'document lookup'], ['مجموعه', data.dataset || collection()], ['شناسه سند', source ? source.id : '—'], ['SHA-256 مجموعه', data.corpus_sha256 || '—']];
  if (source) rows.push(['SHA-256 متن', source.text_sha256 || '—'], ['منبع', source.source]);
  if (source && source.category) rows.push(['موضوع', source.category]);
  if (source && source.license) rows.push(['مجوز', source.license]);
  if (source && source.retrieved_at) rows.push(['تاریخ دریافت', source.retrieved_at]);
  const dl = $('#receipt'); dl.replaceChildren();
  for (const [key, value] of rows) {
    const dt = document.createElement('dt'); dt.textContent = key;
    const dd = document.createElement('dd');
    if (key === 'منبع' && safeSource(value)) {
      const a = document.createElement('a'); a.href = value; a.textContent = value; a.target = '_blank'; a.rel = 'noopener noreferrer'; dd.append(a);
    } else dd.textContent = value;
    dl.append(dt, dd);
  }
}
function render(data, duration) {
  const accepted = data.status === 'evidence_found';
  selected = accepted ? data.citations[0] : null;
  $('#empty').hidden = true; $('#results').hidden = false;
  $('#elapsed').textContent = number(duration) + ' میلی‌ثانیه · زمان درخواست';
  $('#result-title').textContent = accepted ? 'شواهد مرتبط پیدا شد' : 'شواهد کافی پیدا نشد';
  $('#answer-label').textContent = accepted ? 'نقل عین متن از منبع' : 'خودداری از پاسخ';
  $('#answer-title').textContent = accepted ? selected.title : 'به‌جای حدس، به منبع بیشتری نیاز داریم.';
  $('#answer').textContent = data.answer;
  $('#copy').hidden = !accepted;
  $('#answer-note').textContent = !accepted ? 'هیچ منبعی به‌عنوان پاسخ تأیید نشد. پرسش را دقیق‌تر کنید یا مجموعه مناسب‌تری انتخاب کنید.' : collection() === 'reference'
    ? 'این متن از مقدمه نسخه مشخص ویکی‌پدیای فارسی است؛ ممکن است قدیمی باشد. مشارکت‌کنندگان ویکی‌پدیا · CC BY-SA 4.0. برای تصمیم عملی، منبع را بررسی کنید.'
    : 'این دستورالعمل ساختگیِ نمونه است؛ راهنمای مصوب هیچ سازمانی نیست.';
  $('#hits').replaceChildren();
  $('#hit-count').textContent = number(data.retrieved.length) + ' سند';
  for (const [i, doc] of data.retrieved.entries()) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'source-hit';
    if (selected && doc.id === selected.id) button.classList.add('selected');
    button.setAttribute('aria-label', 'مشاهده منبع: ' + doc.title);
    const title = document.createElement('strong'); title.textContent = number(i + 1) + '. ' + doc.title;
    const meta = document.createElement('small');
    const id = document.createElement('span'); id.textContent = doc.id; id.dir = 'ltr';
    const score = document.createElement('span'); score.textContent = 'امتیاز ' + number(doc.score);
    meta.append(id, score); button.append(title, meta);
    button.addEventListener('click', () => showSource(doc)); $('#hits').append(button);
  }
  receipt(data, selected);
  steps(['query','search','evidence', ...(accepted ? ['source'] : [])]);
}
async function ask(question) {
  if (!question.trim()) { $('#question').focus(); return; }
  invalidate(); const run = sequence, corpus = collection();
  controller = new AbortController(); const active = controller;
  const timeout = setTimeout(() => active.abort(), 10000);
  $('#submit').disabled = true; $('#results').setAttribute('aria-busy', 'true');
  $('#notice').textContent = 'در حال جست‌وجو در اسناد…'; steps(['query'], 'search');
  const started = performance.now();
  try {
    const data = await jsonFetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'}, signal:active.signal, body:JSON.stringify({question, collection:corpus})});
    if (run !== sequence) return;
    render(data, performance.now() - started); $('#notice').textContent = '';
    answeredQuestion = question; answeredCollection = corpus;
    $('#model-panel').hidden = !(modelEnabled && data.status === 'evidence_found');
    $('#model-status').textContent = 'متن منبع پایین صفحه می‌ماند. برای ساخت پاسخ کوتاه، دکمه را بزنید.';
  } catch (error) {
    if (run !== sequence) return;
    steps(['query']); $('#notice').textContent = 'ارتباط با برنامه برقرار نشد یا مهلت درخواست تمام شد. دوباره تلاش کنید.';
  } finally {
    clearTimeout(timeout);
    if (run === sequence) { $('#submit').disabled = false; $('#results').setAttribute('aria-busy', 'false'); }
  }
}
async function catalog() {
  const run = ++catalogSequence, corpus = collection();
  $('#retry').hidden = true; $('#catalog').textContent = 'در حال دریافت فهرست…'; $('#count').textContent = '—';
  try {
    const data = await jsonFetch('/api/documents?collection=' + corpus);
    if (run !== catalogSequence) return;
    documents = data.documents;
    $('#catalog-filter').value = '';
    renderCatalog();
  } catch {
    if (run !== catalogSequence) return;
    $('#catalog').textContent = 'فهرست اسناد دریافت نشد.'; $('#retry').hidden = false;
  }
}
function renderCatalog() {
    const normalize = text => text.normalize('NFKC').replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/\u200c/g,' ').toLowerCase();
    const query = normalize($('#catalog-filter').value.trim());
    const visible = documents.filter(doc => normalize(doc.title+' '+(doc.category || '')).includes(query));
    $('#count').textContent = number(visible.length) + ' / ' + number(documents.length);
    $('#catalog').replaceChildren();
    for (const doc of visible) {
      const button = document.createElement('button'); button.type = 'button';
      const icon = document.createElement('span'); icon.className = 'doc-square'; icon.textContent = '▤';
      const title = document.createElement('span'); title.textContent = doc.title;
      if (doc.category) { const category = document.createElement('small'); category.textContent = doc.category; title.append(category); }
      button.append(icon, title); button.addEventListener('click', () => showSource(doc)); $('#catalog').append(button);
    }
    if (!visible.length) $('#catalog').textContent = 'سندی با این عنوان یا موضوع نیست.';
}
$('#catalog-filter').addEventListener('input', renderCatalog);
$('#ask').addEventListener('submit', event => { event.preventDefault(); ask($('#question').value); });
for (const button of document.querySelectorAll('[data-query]')) button.addEventListener('click', () => { $('#question').value = button.dataset.query; ask(button.dataset.query); });
$('#collection').addEventListener('change', () => {
  invalidate(); $('#question').value = '';
  const real = collection() === 'reference';
  const examples = real ? ['فیشینگ چیست؟','سامانه نام دامنه چیست؟','احراز هویت چندعاملی چیست؟'] : ['رمز عبور را فراموش کردم','صف چاپ پرینتر متوقف شده','صدای تلفن VoIP یک طرفه است'];
  document.querySelectorAll('[data-query]').forEach((b,i) => { b.dataset.query = examples[i]; b.textContent = examples[i]; });
  $('#collection-note').textContent = real ? 'متن‌های واقعی از ویکی‌پدیای فارسی با نسخه مشخص و مجوز CC BY-SA 4.0.' : 'راهنماهای ساختگی برای نمایش گردش کار؛ دستورالعمل سازمانی نیستند.';
  catalog();
});
$('#retry').addEventListener('click', catalog);
$('#close-source').addEventListener('click', () => $('#source-dialog').close());
$('#copy').addEventListener('click', async () => {
  if (!selected) return;
  const text = selected.title + '\n' + selected.excerpt + '\nمنبع: ' + selected.id + '\n' + selected.source;
  try { await navigator.clipboard.writeText(text); $('#notice').textContent = 'متن و نشانی منبع کپی شد.'; }
  catch { $('#notice').textContent = 'کپی خودکار در دسترس نیست؛ متن پاسخ را انتخاب و کپی کنید.'; }
});
catalog();
$('#generate').addEventListener('click', async () => {
  if(!answeredQuestion || answeredQuestion.length > 400) { $('#model-status').textContent = 'برای پاسخ مدل، پرسش باید حداکثر ۴۰۰ نویسه باشد.'; return; }
  const run=++modelSequence; modelController=new AbortController(); const active=modelController;
  const timeout=setTimeout(()=>active.abort(),95000);
  $('#generate').disabled=true; $('#model-answer').textContent=''; $('#model-quote').hidden=true;
  $('#model-meta').textContent=''; $('#model-status').textContent='مدل محلی در حال آماده‌کردن پاسخ است؛ ممکن است تا ۹۰ ثانیه طول بکشد…';
  const messages={insufficient_evidence:'مدل شواهد کافی تشخیص نداد؛ متن اصلی را بررسی کنید.',invalid_output:'خروجی مدل با قرارداد منبع و نقل‌قول تطبیق نداشت و نمایش داده نشد.',incomplete:'پاسخ مدل ناتمام بود و نمایش داده نشد.',busy:'مدل مشغول درخواست دیگری است؛ کمی بعد دوباره تلاش کنید.',source_too_long:'این منبع برای پردازش فعلی طولانی است.',unavailable:'مدل در دسترس نیست؛ بازیابی منابع همچنان کار می‌کند.'};
  try {
    const data=await jsonFetch('/api/answer',{method:'POST',signal:active.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({question:answeredQuestion,collection:answeredCollection})});
    if(run!==modelSequence)return;
    if(data.status!=='answer_ready'){ $('#model-status').textContent=messages[data.status] || 'پاسخ قابل نمایش دریافت نشد.'; return; }
    $('#model-status').textContent='پیش‌نویس مدل؛ انطباق معنایی پاسخ را با منبع بررسی کنید.';
    $('#model-answer').textContent=data.answer; $('#model-quote').textContent='نقل‌قول از منبع: «'+data.quote+'»'; $('#model-quote').hidden=false;
    $('#model-meta').textContent=data.model+' · '+data.source_id+' · '+number(data.generation_ms/1000)+' ثانیه · نقل‌قول با متن منبع تطبیق دارد؛ صحت همه ادعاها تضمین نمی‌شود.';
  }catch{if(run===modelSequence)$('#model-status').textContent='ارتباط با مدل قطع شد یا مهلت پاسخ پایان یافت.';}
  finally{clearTimeout(timeout);if(run===modelSequence)$('#generate').disabled=false;}
});
jsonFetch('/health').then(data => { modelEnabled=Boolean(data.local_answer); $('#connection').textContent = data.status === 'ok' ? (modelEnabled ? '● بازیابی + مدل محلی' : '● متصل به موتور واقعی') : 'برنامه در دسترس نیست'; }).catch(() => { $('#connection').textContent = 'ارتباط برقرار نشد'; });
