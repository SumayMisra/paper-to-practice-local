# Install Paper to Practice Local from scratch

This app runs on your own computer. Downloading the source does not install Python, Ollama, or its model automatically. You do not need Git, VS Code, Node.js, a paid API account, or an API key. A web browser and a terminal are enough after the steps below.

## 1. Download the project

Use the [direct ZIP download](https://github.com/SumayMisra/paper-to-practice-local/archive/refs/heads/main.zip), or select **Code → Download ZIP** on the [repository page](https://github.com/SumayMisra/paper-to-practice-local). Extract the ZIP completely (on Windows, right-click → **Extract All**). Open the extracted folder containing `run.py`, `requirements.txt`, and `static/`. Do not run files from inside the ZIP or download only `app.py`.

Keep this folder somewhere you can write files, such as Documents. Its default name is `paper-to-practice-local-main`. You may rename or move the folder before setup; if you move it after creating `.venv`, recreate that environment.

## 2. Install Python

Use **Python 3.14** for the setup below. The app recommends Python 3.11 or newer, but use a regular stable Python release rather than a prerelease or free-threaded build.

### macOS

Download the Python 3.14 macOS installer from [python.org](https://www.python.org/downloads/macos/), open the `.pkg`, and follow its installer. Then open **Terminal** and check:

```sh
python3.14 --version
```

It should report `Python 3.14.x`. If HTTPS package installation later reports a certificate error, run **Install Certificates.command** in the installed **Applications → Python 3.14** folder, as described in [Python's macOS guide](https://docs.python.org/3.14/using/mac.html).

### Windows

Install the **Python install manager** from [python.org](https://www.python.org/downloads/). Open a new **PowerShell** window and install/check Python 3.14:

```powershell
py install 3.14
py -3.14 --version
```

If you already installed Python 3.14 with a traditional installer, skip `py install` and run the version check. See [Python's Windows installation guide](https://docs.python.org/3.14/using/windows.html) if `py` is not recognized. Reopen PowerShell after installation.

### Linux (Ubuntu 24.04 or newer / compatible Debian systems)

Use your distribution's supported Python 3.11+ packages, including virtual-environment support. For example:

```sh
sudo apt update
sudo apt install python3 python3-venv python3-pip curl
python3 --version
```

Other distributions use different package managers. If your system Python is older than 3.11, install a supported newer Python through your distribution's instructions rather than replacing system files manually.

## 3. Install Ollama

Ollama runs the AI model locally. Download it from [ollama.com/download](https://ollama.com/download) and select your operating system.

- **macOS:** install and open the Ollama app. Check [Ollama's macOS requirements](https://docs.ollama.com/macos) before downloading.
- **Windows:** run the official Windows installer and open Ollama. Reopen PowerShell so the `ollama` command is available. See [Windows requirements](https://docs.ollama.com/windows).
- **Linux:** follow the [official Linux installation instructions](https://docs.ollama.com/linux). Keep the Ollama service running; if it is not installed as a service, run `ollama serve` in a separate terminal.

In Terminal or PowerShell, run:

```sh
ollama --version
ollama pull qwen3:4b-instruct
ollama list
```

Wait until the download completes. `ollama list` should include `qwen3:4b-instruct`. If the command cannot connect, open Ollama or run `ollama serve` in another terminal and leave it running.

The [default model](https://ollama.com/library/qwen3:4b-instruct) is approximately **2.5 GB** to download, in addition to Ollama and Python dependencies. Runtime RAM usage is higher than download size and depends on context and hardware. This app requests a 32,768-token context. A minimum memory configuration has not been established; low-memory machines may fail or run slowly. The model must be downloaded locally; cloud models are rejected.

You only need to download the model once for the Ollama installation you are using. No account or API key is required by this app.

## 4. Open a terminal in the project folder

The terminal must be in the extracted directory containing `run.py`.

- **macOS/Linux:** type `cd ` (with a space), drag the extracted folder into Terminal, then press Enter. You can also use `cd "path/to/paper-to-practice-local-main"`, replacing the example with your actual path.
- **Windows:** open the extracted folder in File Explorer, right-click an empty space, and choose **Open in Terminal**. Use a PowerShell tab.

Run `ls` (macOS/Linux) or `dir` (Windows) and confirm you see `run.py` and `requirements.txt` before continuing.

## 5. Install the app's dependencies

Run the commands for your operating system one at a time. `.venv` isolates the app's packages; these commands do not require environment activation or a PowerShell execution-policy change.

### macOS

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

### Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Wait for `Uvicorn running on http://127.0.0.1:8001`. Leave this terminal open and visit **http://127.0.0.1:8001** in your browser. The app is on your own computer; the GitHub page itself does not run it.

## 6. Create and open a notebook

1. Click **Check connection** and confirm the model is ready.
2. Upload a PDF with selectable text, no password, at most 12 MiB and 100 pages.
3. Choose the audience. Optionally enter up to 1,000 characters under **Anything to focus on?** For example: “Explain the main equation for beginners, implement a small NumPy example, and add two exercises with solutions.”
4. Click **Create my notebook**. Local generation can take several minutes.
5. Review source-coverage notes and the cell preview, then click **Download notebook**.
6. Open [Google Colab](https://colab.research.google.com/), sign in if prompted, select **File → Upload notebook**, and choose the `.ipynb`. Review its code before running cells in a Python 3 CPU runtime. This sends the notebook to Google; generating it locally does not require Colab.

Colab avoids a separate Jupyter installation. If you prefer local execution, install [JupyterLab](https://jupyter.org/install) separately and install any packages the generated notebook imports. Ollama is needed to generate notebooks, not to run downloaded ones.

The app checks notebook structure and Python syntax; it does not execute the generated code or verify scientific claims. Figures are not read and long papers are excerpted. See the [README limitations](README.md#current-limitations).

## Start again another day

Open Ollama, open a terminal in the same project folder, and run:

- macOS/Linux: `.venv/bin/python run.py`
- Windows: `.\.venv\Scripts\python.exe run.py`

Visit **http://127.0.0.1:8001**. You do not need to reinstall packages or redownload the model each time. Press **Ctrl+C** in the app terminal to stop it. The launcher stops only an Ollama process it started itself.

## Check your installation

With the server running, open **http://127.0.0.1:8001/health**. It should display `{"status":"ok"}`. This checks the web server; the page's **Check connection** checks the model separately.

Run the automated tests in a second terminal in the project folder:

```sh
# macOS/Linux
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
```

```powershell
# Windows
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

Tests simulate model responses and require no model download. Passing tests does not guarantee that a particular model or computer will generate a correct tutorial.

## Common setup problems

| Problem | What to do |
| --- | --- |
| `python`, `py`, or `ollama` not found | Finish the relevant installer, reopen the terminal, and repeat its version check. |
| `requirements.txt` or `run.py` not found | Extract the ZIP, then open the terminal in the folder containing both files. |
| `No module named venv` or `ensurepip` missing | On Ubuntu/Debian, install the matching `python3-venv` package. |
| `ModuleNotFoundError` | Use the `.venv` Python command above to install requirements and launch the app. |
| Cannot connect to Ollama | Open Ollama or start `ollama serve`; wait until ready and click **Check connection**. |
| Model missing | Run `ollama pull qwen3:4b-instruct` against the same running Ollama server. |
| Port 8001 already in use | Stop the previous copy of this app with Ctrl+C, or use its already-open page. |
| Out of memory, timeout, or invalid tutorial | Close memory-heavy apps; try a shorter PDF excerpt and a narrower focus. Another compatible downloaded model can be selected under Advanced settings, but is not guaranteed to work. |
| No readable text in PDF | Perform OCR elsewhere or choose a PDF with selectable text. |

Installation/model downloads need internet. Once installed, generation uses local Ollama; opening Colab or installing packages in a notebook may need internet again. The source contains no model weights, Python environment, or bundled installers.
