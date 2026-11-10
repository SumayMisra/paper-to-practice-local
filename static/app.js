const $ = (id) => document.getElementById(id);
const form = $('form');
let downloadUrl = null;
let controller = null;
let timer = null;

function error(message) { $('error').textContent = message; $('error').hidden = !message; }
function showState(state) {
  for (const name of ['empty', 'loading', 'result']) $(name + '-state').hidden = state !== name;
}
function showFile() {
  const file = $('pdf').files[0];
  $('file-title').textContent = file ? file.name : 'Drop your paper here';
  $('file-help').textContent = file ? `${(file.size / 1024 / 1024).toFixed(2)} MB · Click to choose another PDF` : 'or click to browse · PDF up to 12 MB, 100 pages';
  error('');
}
$('pdf').addEventListener('change', showFile);
for (const event of ['dragenter', 'dragover']) $('dropzone').addEventListener(event, () => $('dropzone').classList.add('dragging'));
for (const event of ['dragleave', 'drop']) $('dropzone').addEventListener(event, () => $('dropzone').classList.remove('dragging'));
async function checkLocal() {
  $('check-local').disabled = true;
  $('local-status').textContent = 'Checking your local model…';
  try {
    const response = await fetch('/api/local-status?model=' + encodeURIComponent($('model').value));
    const result = await response.json();
    $('local-status').textContent = response.ok ? result.message : (result.detail || 'Check your model name.');
  } catch {
    $('local-status').textContent = 'Cannot reach the app. Start python run.py and refresh.';
  } finally {
    $('check-local').disabled = false;
  }
}
$('check-local').addEventListener('click', checkLocal);
$('model').addEventListener('change', checkLocal);
checkLocal();
$('cancel').addEventListener('click', () => controller?.abort());

function renderResult(result) {
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = URL.createObjectURL(new Blob([JSON.stringify(result.notebook, null, 2)], {type: 'application/x-ipynb+json'}));
  $('download').href = downloadUrl;
  $('download').download = result.filename;
  $('result-title').textContent = result.title;
  $('result-summary').textContent = result.summary;
  $('validation').textContent = result.validation + ' Review code and scientific claims before running.';
  $('source-notes').textContent = (result.source_notes || []).join(' ');
  const cells = result.notebook.cells;
  $('stats').replaceChildren(...[`${result.pages} source pages`, `${cells.length} cells`, `${cells.filter(c => c.cell_type === 'code').length} code cells`, 'Python · CPU'].map(text => {
    const span = document.createElement('span'); span.textContent = text; return span;
  }));
  $('preview').replaceChildren(...cells.map((cell, i) => {
    const source = Array.isArray(cell.source) ? cell.source.join('') : cell.source;
    const details = document.createElement('details'); details.className = 'cell ' + cell.cell_type;
    const summary = document.createElement('summary');
    const type = document.createElement('span'); type.className = 'cell-type'; type.textContent = cell.cell_type === 'code' ? '[ ]' : 'md';
    const title = document.createElement('span'); title.textContent = `${i + 1}. ${source.split('\n').find(l => l.trim())?.replace(/^#+\s*/, '').slice(0, 90) || 'Cell'}`;
    summary.append(type, title);
    const pre = document.createElement('pre'); pre.textContent = source;
    details.append(summary, pre); return details;
  }));
  showState('result');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (controller) return;
  error('');
  const file = $('pdf').files[0];
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) return error('Please choose a PDF research paper.');
  if (file.size > 12 * 1024 * 1024) return error('Please choose a PDF under 12 MB.');
  const data = new FormData(form);
  controller = new AbortController();
  $('generate').disabled = true;
  $('generate').textContent = 'Creating your notebook…';
  showState('loading');
  const started = Date.now();
  $('progress-text').textContent = 'Reading your paper locally…';
  timer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - started) / 1000);
    $('progress-text').textContent = `Your local model is writing your tutorial · ${elapsed}s`;
  }, 1000);
  try {
    const response = await fetch('/api/generate', {method: 'POST', body: data, signal: controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Please check your input fields and try again.');
    renderResult(result);
  } catch (err) {
    showState('empty');
    error(err.name === 'AbortError' ? 'Request cancelled. You can start again when ready.' : (err.message === 'Failed to fetch' ? 'Cannot reach the local server. Make sure the app is running and try again.' : err.message));
  } finally {
    clearInterval(timer); controller = null;
    $('generate').disabled = false;
    $('generate').textContent = 'Create my notebook ↗';
  }
});
