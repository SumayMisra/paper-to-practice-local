import asyncio
import io
import json

import httpx
import nbformat
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

import app
import generator
from generator import Cell, Tutorial, GenerationError
from paper import MAX_SOURCE_BYTES, extract_paper

client = TestClient(app.app)


def pdf_bytes(encrypted=False, pages=1, text='A paper about computing the arithmetic mean.'):
    writer = PdfWriter()
    for _ in range(pages):
        page = writer.add_blank_page(width=612, height=792)
        if text:
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                     NameObject('/Subtype'): NameObject('/Type1'),
                                     NameObject('/BaseFont'): NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
            stream = DecodedStreamObject()
            safe_text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            stream.set_data(f'BT /F1 12 Tf 50 750 Td ({safe_text}) Tj ET'.encode())
            page[NameObject('/Contents')] = writer._add_object(stream)
    if encrypted:
        writer.encrypt('password')
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def tutorial():
    return Tutorial(title='A test tutorial', summary='Learn through a tiny experiment.', cells=[
        Cell(cell_type='markdown', source='# Learning objectives'),
        Cell(cell_type='code', source='x = [1, 2, 3]'),
        Cell(cell_type='markdown', source='## Intuition'),
        Cell(cell_type='code', source='mean = sum(x) / len(x)'),
        Cell(cell_type='markdown', source='## Experiment'),
        Cell(cell_type='code', source='assert mean == 2\nprint(mean)'),
        Cell(cell_type='markdown', source='## Interpretation'),
        Cell(cell_type='markdown', source='## Limitations'),
        Cell(cell_type='markdown', source='## Exercises and solutions'),
        Cell(cell_type='markdown', source='## References'),
    ])


def post(data=None, **fields):
    return client.post('/api/generate', files={'file': ('paper.pdf', data if data is not None else pdf_bytes(), 'application/pdf')}, data=fields)


def test_full_conversion_without_api_key(monkeypatch):
    async def fake_generate(text, level, focus, model):
        assert '[PDF page 1]' in text and 'arithmetic mean' in text
        assert model == generator.DEFAULT_MODEL
        return tutorial()
    monkeypatch.setattr(app, 'generate_tutorial', fake_generate)
    response = post()
    assert response.status_code == 200
    result = response.json()
    notebook = nbformat.reads(json.dumps(result['notebook']), as_version=4)
    nbformat.validate(notebook)
    assert result['filename'].endswith('.ipynb')
    assert notebook.metadata.kernelspec.name == 'python3'
    assert notebook.metadata.paper_to_practice.executed is False
    assert notebook.metadata.paper_to_practice.provider == 'ollama'
    assert result['source_notes']
    assert result['source_notes'][0] in notebook.cells[0].source
    assert all(c.execution_count is None and c.outputs == [] for c in notebook.cells if c.cell_type == 'code')
    assert response.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize('data, status', [(b'not a pdf', 400), (b'%PDF-broken', 400), (b'%PDF-' + b'x' * app.MAX_BYTES, 413)])
def test_invalid_upload(data, status):
    assert post(data).status_code == status


def test_encrypted_and_too_many_pages():
    assert post(pdf_bytes(encrypted=True)).status_code == 400
    assert post(pdf_bytes(pages=101)).status_code == 400


def test_scanned_pdf_rejected_before_generation():
    response = post(pdf_bytes(text=''))
    assert response.status_code == 400
    assert 'OCR' in response.json()['detail']


def test_text_extraction_page_labels_and_long_paper_notes():
    paper = extract_paper(pdf_bytes(pages=3))
    assert paper.pages == 3
    assert '[PDF page 3]' in paper.text
    paper = extract_paper(pdf_bytes(pages=3, text='many words ' * 4000))
    assert len(paper.text.encode()) <= MAX_SOURCE_BYTES
    assert '[PDF page 3]' in paper.text
    assert 'omitted' in paper.text
    assert any('excerpts' in note for note in paper.notes)


def test_mixed_scanned_and_text_pages_are_reported():
    from pypdf import PdfReader
    writer = PdfWriter()
    writer.add_page(PdfReader(io.BytesIO(pdf_bytes())).pages[0])
    writer.add_blank_page(width=612, height=792)
    output = io.BytesIO()
    writer.write(output)
    paper = extract_paper(output.getvalue())
    assert paper.pages == 2
    assert any('skipped: 2' in note for note in paper.notes)


@pytest.mark.parametrize('model', ['../other', 'qwen3:4b-cloud', 'https://remote/model'])
def test_bad_or_cloud_model(model):
    assert post(model=model).status_code in (400, 422)


def test_cross_origin():
    assert client.post('/api/generate', headers={'Origin': 'https://evil.example'}).status_code == 403


def test_frontend_assets():
    html = client.get('/').text
    assert 'Create a tutorial' in html
    assert 'No API key or credits needed' in html
    assert 'name="api_key"' not in html
    assert f'value="{generator.DEFAULT_MODEL}"' in html
    assert 'OpenAI' not in html and 'Gemini' not in html
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200


def test_syntax_check_and_magic():
    data = tutorial()
    data.cells[1].source = 'return 3'
    with pytest.raises(SyntaxError):
        generator.check_tutorial(data)
    data.cells[1].source = '%pip install numpy\nimport numpy as np'
    generator.check_tutorial(data)


def mocked_ollama(monkeypatch, handler, show=None):
    original = httpx.AsyncClient
    def route(request):
        assert request.url.host == '127.0.0.1'
        assert request.url.port == 11434
        assert 'authorization' not in request.headers
        if request.url.path == '/api/show':
            return show if show is not None else httpx.Response(200, json={'capabilities': ['completion']})
        return handler(request)
    monkeypatch.setattr(generator.httpx, 'AsyncClient', lambda **kwargs: original(transport=httpx.MockTransport(route), **kwargs))


def ollama_result(text, reason='stop'):
    return httpx.Response(200, json={'done': True, 'done_reason': reason, 'response': text})


def generate():
    return asyncio.run(generator.generate_tutorial('[PDF page 1]\nPaper text', 'beginner', '', generator.DEFAULT_MODEL))


def test_local_contract_and_repair(monkeypatch):
    calls = []
    def handler(request):
        body = json.loads(request.content)
        assert request.url.path == '/api/generate'
        assert body['model'] == generator.DEFAULT_MODEL
        assert body['stream'] is False
        assert '[PDF page 1]' in body['prompt']
        assert body['format']['additionalProperties'] is False
        assert body['options']['num_ctx'] == 32768
        calls.append(body)
        if len(calls) == 2:
            assert 'previous attempt failed' in body['prompt']
        return ollama_result('incomplete JSON' if len(calls) == 1 else tutorial().model_dump_json())
    mocked_ollama(monkeypatch, handler)
    assert generate().title == 'A test tutorial'
    assert len(calls) == 2


@pytest.mark.parametrize('status, match', [(404, 'missing'), (500, 'memory')])
def test_local_errors(monkeypatch, status, match):
    mocked_ollama(monkeypatch, lambda request: httpx.Response(status, text='internal diagnostics'))
    with pytest.raises(GenerationError, match=match):
        generate()


@pytest.mark.parametrize('error_type, status', [(httpx.ReadTimeout, 504), (httpx.ConnectError, 503)])
def test_connection_errors(monkeypatch, error_type, status):
    def handler(request):
        raise error_type('diagnostics', request=request)
    mocked_ollama(monkeypatch, handler)
    with pytest.raises(GenerationError) as caught:
        generate()
    assert caught.value.status == status


@pytest.mark.parametrize('text, reason', [('{}', 'stop'), ('{}', 'length')])
def test_repeated_invalid_generation_stops(monkeypatch, text, reason):
    calls = []
    def handler(request):
        calls.append(1)
        return ollama_result(text, reason)
    mocked_ollama(monkeypatch, handler)
    with pytest.raises(GenerationError, match='twice'):
        generate()
    assert len(calls) == 2


@pytest.mark.parametrize('show, message', [
    (httpx.Response(404, json={'error': 'missing'}), 'ollama pull'),
    (httpx.Response(200, json={'remote_model': 'model', 'capabilities': ['completion']}), 'Cloud'),
    (httpx.Response(200, json={'capabilities': ['embedding']}), 'text-generation'),
])
def test_not_ready_models_are_not_used(monkeypatch, show, message):
    def unexpected(request):
        pytest.fail('Generation must not run for unavailable or remote models')
    mocked_ollama(monkeypatch, unexpected, show)
    with pytest.raises(GenerationError, match=message):
        generate()
    status = client.get('/api/local-status').json()
    assert status['ready'] is False


def test_local_status_ready(monkeypatch):
    mocked_ollama(monkeypatch, lambda request: pytest.fail('No generation expected'))
    assert client.get('/api/local-status').json()['ready'] is True


def test_ollama_not_running(monkeypatch):
    original = httpx.AsyncClient
    def handler(request):
        raise httpx.ConnectError('offline', request=request)
    monkeypatch.setattr(generator.httpx, 'AsyncClient', lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
    assert client.get('/api/local-status').json()['ready'] is False
    with pytest.raises(GenerationError, match='Start Ollama'):
        generate()
