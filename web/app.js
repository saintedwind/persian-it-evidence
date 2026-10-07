const form = document.querySelector('#ask');
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  const result = document.querySelector('#result');
  result.hidden = false;
  document.querySelector('#status').textContent = 'در حال جست‌وجو…';
  document.querySelector('#answer').textContent = '';
  document.querySelector('#sources').replaceChildren();
  try {
    const response = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:document.querySelector('#question').value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    document.querySelector('#status').textContent = data.status === 'evidence_found' ? 'متن مرتبط پیدا شد' : 'شواهد کافی نداریم';
    document.querySelector('#answer').textContent = data.answer;
    for (const source of data.citations) {
      const item = document.createElement('p');
      item.className = 'source';
      item.textContent = `${source.id} · ${source.title} · ${source.source}`;
      document.querySelector('#sources').append(item);
    }
  } catch (error) {
    document.querySelector('#status').textContent = 'جست‌وجو انجام نشد';
    document.querySelector('#answer').textContent = error.message;
  } finally { button.disabled = false; }
});
