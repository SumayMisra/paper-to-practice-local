# Paper to Practice Local

[Download ZIP](https://github.com/SumayMisra/paper-to-practice-local/archive/refs/heads/main.zip) · [Installation guide](INSTALL.md)

Turn a research paper PDF into a guided Python tutorial notebook using a model running locally through Ollama. Upload a paper, choose an audience and learning focus, preview the generated cells, and download an `.ipynb` for Google Colab or Jupyter.

**No OpenAI/Gemini API key, paid API credits, or hosted model account is required for generation.** Ollama and its model must be installed separately; they are not included in this repository.

**Starting from scratch? Follow [INSTALL.md](INSTALL.md)** for ZIP download instructions, Python and Ollama installation, model download, and commands for macOS, Windows, and Linux. No Git, IDE, or Node.js installation is required. This is a local app, not a hosted website.

## Credit and project origins

This is a separate implementation inspired by [Vizuara AI's Paper to Notebook — Traditional Version](https://github.com/VizuaraAI/paper-to-notebook-traditional), a demo for its Modern Software Developer 2.0 bootcamp. Credit for the original PDF-to-notebook workflow belongs to Vizuara AI. This repository is not an official Vizuara release.

| Area | Existing Vizuara traditional project | Maintainer additions and changes in this version |
| --- | --- | --- |
| Upload and download | FastAPI PDF upload and `.ipynb` export | Browser form, progress display, source preview, download, and Colab instructions |
| PDF processing | PyMuPDF text extraction, regex section detection, and heuristic code extraction | pypdf extraction with page labels, explicit skipped-page notes, and bounded page excerpts |
| Notebook creation | nbformat assembly of extracted text/code and a fixed setup cell | Local-model generation of teaching explanations, Python examples, experiments, and exercises |
| Customization | No audience/focus controls in the inspected original API | Beginner/intermediate/advanced audience and custom focus instructions |
| Model integration | No AI or LLM dependency | Ollama generation, model readiness checks, local runtime startup, and cloud-model rejection |
| Validation | Original extraction tests and manual-review guidance | Structured response validation, Python syntax checks, one repair attempt, and app/generator tests |

PDF upload, extraction, FastAPI usage, nbformat notebook assembly, and notebook export are **not claimed as new ideas introduced here**. See [ATTRIBUTION.md](ATTRIBUTION.md) for the inspected upstream revision and preserved license notice. The separate Vizuara AI-powered project is not the comparison baseline used above.

## Requirements and dependencies

- **Python 3.11+** is the recommended setup. The current local verification used Python 3.14; a full Python/platform compatibility matrix has not been tested.
- **Ollama**, installed separately and reachable at `http://127.0.0.1:11434`.
- **Default model:** `qwen3:4b-instruct`. Its [Ollama model page](https://ollama.com/library/qwen3:4b-instruct) lists a download of approximately 2.5 GB. Allow additional disk space for Ollama and Python dependencies.
- **Memory:** allow space in RAM for the model, its 32,768-token context, and the app. The 2.5 GB download size is not a RAM requirement. A minimum RAM/GPU configuration has not been established by this review; use `ollama ps` during generation to inspect the loaded model, as described in [Ollama's FAQ](https://docs.ollama.com/faq).
- **Platform:** setup and automated tests were checked on macOS. Consult [Ollama's macOS requirements](https://docs.ollama.com/macos) for supported hardware and OS versions. Windows and Linux have not been verified for this app.
- Internet is needed for installation/model downloads and to use Google Colab. Generation itself uses the local model. Running a downloaded notebook locally does not require Ollama.

Python dependencies are declared in [requirements.txt](requirements.txt):

| Package | Purpose |
| --- | --- |
| FastAPI | Web routes, form handling, and request validation |
| Uvicorn | Local web server |
| python-multipart | PDF upload and form parsing |
| pypdf | PDF validation and text extraction |
| Pydantic 2 | Tutorial/cell schema and generated JSON validation |
| nbformat | Notebook construction, serialization, and validation |
| HTTPX | Requests to the loopback Ollama service |
| pytest | Automated tests; included in the same requirements file |

Version ranges are bounded but not locked to an exact dependency set. There is no Node.js build step and no OpenAI, Gemini, or Ollama Python SDK dependency. NumPy and Matplotlib are preferred in generated notebook code; they are not required to run this web app.

## Setup

Run these commands from the repository root, the directory containing `run.py`. A checkout contains source only: it does not include `.venv`, Ollama binaries, model weights, or generated notebooks.

### 1. Create the Python environment

On macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The launcher does **not** create a virtual environment or install dependencies automatically.

### 2. Install Ollama and download the model

Install [Ollama](https://ollama.com/download), open the Ollama application (or run `ollama serve` in another terminal), then download the model:

```sh
ollama pull qwen3:4b-instruct
ollama list
```

No sign-in is required by this app. Use a downloaded local model, not an Ollama cloud model.

### 3. Start the app

With the virtual environment activated:

```sh
python run.py
```

Open **http://127.0.0.1:8001**. Keep the terminal running. Stop the app with **Ctrl+C**. After changing Python code, restart the server; automatic reload is not enabled.

`run.py` reuses an existing Ollama server. If none is running, it looks for a project-local binary, `/Applications/Ollama.app/Contents/Resources/ollama`, or `ollama` on `PATH`, and tries to start one. It stops only a server that it started itself. The web page can still open when Ollama is missing; use **Check connection** to see what needs setup.

### Existing project-local installations

An existing development setup may contain `.local/ollama/ollama` (or `.local/ollama/bin/ollama`) and `.local/models`. These are optional, ignored local files and are not distributed with the source. When the launcher starts that binary, it uses `.local/models` and logs to `.local/ollama.log`.

If another Ollama server is already running, its model store is used instead. A model in `.local/models` will not automatically appear in that other server. Either download the model into the running installation or stop that instance before launching this app. The app does not download missing models automatically.

When starting a system-installed binary, the launcher removes `OLLAMA_MODELS` from the child process environment, so that server uses Ollama's default model location. If you need a custom model directory, start Ollama yourself with that configuration before running the app. All launcher-started servers write their output to `.local/ollama.log`.

## Usage

1. Confirm the page reports that the local model is ready.
2. Upload a PDF with selectable text, at most **12 MiB (12 × 1024 × 1024 bytes)** and **100 pages**. Password-protected PDFs are rejected.
3. Choose **Beginner**, **Intermediate**, or **Advanced**.
4. Optionally enter custom notebook instructions in **Anything to focus on?**.
5. Click **Create my notebook**. Local generation may take several minutes. The elapsed-time display is not a token stream or a completion estimate.
6. Read the validation and source-coverage notes, inspect the cells, and select **Download notebook**.
7. In [Google Colab](https://colab.research.google.com/), choose **File → Upload notebook**, then select the file. Alternatively, open it in your own Jupyter environment.
8. Review the code, then run cells in order with **Shift+Enter**. Use a Python 3 CPU runtime; install any notebook-specific dependencies as needed.

The app requests a compact teaching notebook with objectives, prerequisites, intuition, equations, a simplified implementation, synthetic-data experiments, visualizations, limitations, exercises with solutions, and references to supplied PDF page labels. These are generation instructions, not guarantees that every requested element is present or correct.

## Custom notebook instructions

Use **Anything to focus on?** for per-request instructions, up to **1,000 characters**. For example:

> Focus on the loss function. Explain every symbol for a beginner, implement a small NumPy example with seeded synthetic data, plot the result, and include two exercises with worked solutions. State how the example differs from the full paper.

Choose the matching audience separately. A narrower request and a short relevant PDF excerpt usually give the model a more manageable task. The focus text is sent to the local model for that request; it is not saved as a preset.

Custom instructions are intended to adjust explanation, focus, and examples. They do not override the prompt's requirements for self-contained CPU examples, no secrets or external datasets, valid Python, and honest limitations. The model may still fail to follow instructions.

There is no custom-template upload, saved-instruction library, chat editing, or notebook editor in this app. For developer-level changes:

- Edit `SYSTEM` in [generator.py](generator.py) to change the default tutorial instructions.
- Update `Cell`, `Tutorial`, `check_tutorial`, and `build_notebook` together if changing the output format or validation rules.
- Restart the app and run the tests after making changes.

## Ollama model settings

**Advanced settings → Local Ollama model** accepts another installed local text-generation model. The backend checks that it advertises `completion` capability and does not identify itself as remote. It also rejects names containing `cloud`. Models must work with [Ollama structured output](https://docs.ollama.com/capabilities/structured-outputs) through the [`/api/generate` endpoint](https://docs.ollama.com/api/generate); alternative models have not been verified. Use an Ollama version supporting these APIs and the chosen model; this project does not pin or test a minimum Ollama version. A ready status confirms model availability and reported capability, not successful generation or sufficient memory.

Current requests use a **32,768-token context**, **6,144-token generation limit**, temperature **0.2**, and a **five-minute keep-alive**. These are set in `generator.py`. Larger models or contexts need more memory and may be slower. Namespaced names containing `/` are currently rejected by the form/backend validation.

The current model field is used for readiness checks and subsequent generation requests; the app does not save it as a preference. To change the default, update both `DEFAULT_MODEL` in `generator.py` and the model input value in `static/index.html`; setup examples should be updated as well. The Ollama address and app port are fixed in code, not configurable through an app settings file or `OPENAI_API_KEY` environment variable.

## Current limitations

- **Text only:** scanned/image-only PDFs need OCR elsewhere before upload. Figures, diagrams, and visual table structure are not interpreted. Columns and mathematical notation may extract poorly.
- **Limited source coverage:** extracted text is capped at **18,000 UTF-8 bytes**, including page labels. Longer papers use the beginning of each readable page; they are not fully summarized in chunks or searched with retrieval. Omitted text and pages are disclosed in the result and notebook. Some important details can be missed.
- **No scientific or execution verification:** the app validates JSON structure, notebook format, at least three code cells, and Python syntax. It does not execute code, verify results, prove safety, check references, or guarantee faithful reproduction of the research. Every line starting exactly with `%pip install ` is omitted from Python compilation; dependency commands are not validated. Syntax checks use the server's Python version, which may differ from Colab's. Prompt restrictions on downloads and unsafe operations are instructions to the model, not an enforced code sandbox.
- **Bounded generation:** the prompt requests 12–18 cells; the schema accepts 10–45 generated cells, plus an introductory cell added by the app. There is at most one retry for invalid output. The read timeout is 15 minutes per generation attempt, not a strict overall deadline.
- **Cancellation:** the browser stops waiting, but local generation may continue.
- **Local demo deployment:** the app binds to loopback and has no authentication, job queue, saved project history, or production multi-user deployment configuration.
- **No arXiv/URL input or direct Colab upload:** PDFs are uploaded manually and notebooks are downloaded manually. The preview shows cell source, not executed outputs or rendered notebook plots.
- **Platform/dependency coverage:** verified locally on macOS, not across all platforms or dependency versions. Dependency ranges are not a lockfile. The test suite currently emits a Starlette/HTTPX deprecation warning.

## Data handling

The app calls only Ollama on `127.0.0.1:11434` for generation and bypasses proxy environment variables for those calls. For servers it starts, it sets `OLLAMA_NO_CLOUD=1` and limits parallel model requests to one. An already-running server keeps its own configuration; model details are checked before generation. See [Ollama's local/cloud settings](https://docs.ollama.com/faq).

The app does not deliberately save uploaded PDFs or generated notebooks on the server. Upload handling may spool files temporarily; uploads are closed after reading. Downloads are created in the browser. The original PDF filename is included in notebook metadata. Model weights and runtime logs persist locally; notebooks saved by the user may contain paper-derived text. There are no API-key fields, browser localStorage, or analytics in the app.

## Project structure

```text
.
├── app.py                 # FastAPI upload, readiness, and generation routes
├── generator.py           # Ollama calls, prompts, validation, notebook assembly
├── paper.py               # PDF extraction, page labels, excerpt/source notes
├── local_runtime.py       # Ollama discovery, startup, and owned-process cleanup
├── run.py                 # Entry point: local web server on port 8001
├── requirements.txt       # Runtime and test dependencies
├── INSTALL.md             # First-time download and installation guide
├── static/                # Plain HTML, CSS, and JavaScript interface
├── tests/test_app.py      # API, extraction, and mocked generation tests
├── ATTRIBUTION.md         # Original project credit and preserved license notice
└── .gitignore             # Local data, models, credentials, and cache exclusions
```

The sibling `paper-to-notebook-traditional` directory is not needed to run this app and is not part of this repository's upload scope.

## Verification

With the Python environment activated:

```sh
python -m pytest -q
```

The 26 current tests simulate Ollama responses and do not require a running model, network access, or an API key. They cover PDF handling, source omissions, the no-key upload/download flow, model checks, remote-model rejection, error handling, structured requests, syntax validation, and bounded retries.

On November 9, 2026, a clean source copy with a newly created Python 3.14.6 environment installed successfully from `requirements.txt`; all 26 tests passed and `python -m pip check` found no broken requirements. One Starlette/HTTPX deprecation warning remains.

A separate macOS smoke test started that clean copy with `python run.py`, checked the homepage, static assets, health route, and model readiness, then submitted a synthetic one-page teaching note to the real local `qwen3:4b-instruct` model. It returned a valid 13-cell notebook with five code cells. After manual code review, all five cells ran in a separate NumPy/Matplotlib environment; two plots rendered and numerical checks passed. This is evidence for one simple example, not a guarantee for other papers, models, hardware, or scientific claims. The app itself still never executes generated code.

After publication, the public GitHub ZIP was downloaded without authentication and all 14 files were compared against the committed source. A second fresh environment installed successfully, passed all 26 tests and dependency checks, and started the downloaded app with `python run.py`. A real local generation request returned a 16-cell notebook; all seven code cells ran and a plot rendered. Review nevertheless found a logical error in one exercise: it assigned a new population mean to an unused variable, while the sampling function kept using the old mean. This confirms that a runnable notebook can still contain incorrect results; syntax validation is not a correctness guarantee.

Automated tests can be run with the command above on another installation. Windows/Linux execution and a full Python-version compatibility matrix have not been verified. Browser interactions and launcher process-management edge cases are not covered by the test suite.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `ModuleNotFoundError` | Activate `.venv`, install `requirements.txt`, and run `python run.py` with that interpreter. |
| Ollama not ready | Open Ollama or run `ollama serve`; then use **Check connection**. |
| Model missing | Run `ollama pull qwen3:4b-instruct` against the same running server the app uses. |
| Port 8001 already in use | Stop the previous app terminal with Ctrl+C before restarting. |
| Old API-key form or mismatched behavior | Stop the older server, run the current `run.py`, and refresh the browser. |
| No readable text | OCR the PDF separately or upload one with selectable text. |
| Invalid output or timeout | Try a shorter relevant excerpt and a narrower focus; inspect Ollama's log for memory errors. |

## GitHub upload scope

Upload this repository's source, tests, documentation, and dependency list. [.gitignore](.gitignore) excludes virtual environments, caches, local Ollama binaries/model weights, logs, credentials, input PDFs, and generated notebooks. Do not upload `.local/` or `.venv/`; users recreate these through setup. Keep the parent folder's papers/notebooks and the separate original repository outside this project's upload.

Git ignore rules do not remove already-tracked files or sanitize credentials inside source files. Review the proposed Git file list before committing. Deliberately shared example notebooks/PDFs require a separate content/rights review and an explicit ignore-rule exception. Preserve any license and attribution notices when including third-party material.

GitHub's browser upload does not apply local Git ignore rules: select only the source files, never drag in the whole working folder. The repository is intended to contain source, tests, and documentation only. Local models, runtimes, logs, input papers, and generated notebooks are not part of the distribution.

## License

The original Vizuara README declares MIT; its existing notice is preserved in [ATTRIBUTION.md](ATTRIBUTION.md). No standalone `LICENSE` file was found in this app or the inspected original checkout. This preparation does not assign a new license to the added implementation or replace an existing license. No separate license grant for the additions is currently provided. Ollama, model weights, and Python dependencies retain their respective licenses and are not redistributed in this source-only repository.
