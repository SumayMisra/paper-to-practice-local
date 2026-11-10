"""Start a project-local or installed Ollama runtime when needed."""
import os
from pathlib import Path
import shutil
import subprocess
import time

import httpx

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".local"


def ollama_environment():
    env = os.environ.copy()
    env.update(OLLAMA_HOST="127.0.0.1:11434", OLLAMA_NO_CLOUD="1",
               OLLAMA_MODELS=str(LOCAL / "models"), OLLAMA_NUM_PARALLEL="1")
    return env


def running():
    try:
        with httpx.Client(timeout=1, trust_env=False) as client:
            return client.get("http://127.0.0.1:11434/api/version").is_success
    except httpx.HTTPError:
        return False


def start_ollama():
    """Return only a process we started; callers must not stop an existing server."""
    if running():
        return None
    candidates = [LOCAL / "ollama" / "bin" / "ollama", LOCAL / "ollama" / "ollama",
                  Path("/Applications/Ollama.app/Contents/Resources/ollama")]
    binary = next((str(path) for path in candidates if path.is_file()), None) or shutil.which("ollama")
    if not binary:
        print("Install Ollama from https://ollama.com/download, open it, and run: ollama pull qwen3:4b-instruct (see INSTALL.md)", flush=True)
        return None
    LOCAL.mkdir(exist_ok=True)
    env = ollama_environment()
    if not Path(binary).is_relative_to(LOCAL):
        # A normal installation keeps its existing model location.
        env.pop("OLLAMA_MODELS", None)
    with (LOCAL / "ollama.log").open("a") as log:
        process = subprocess.Popen([binary, "serve"], env=env, stdout=log, stderr=log)
    for _ in range(60):
        if running():
            print("Local Ollama server ready.", flush=True)
            return process
        if process.poll() is not None:
            break
        time.sleep(0.25)
    print(f"Ollama did not start. Check {LOCAL / 'ollama.log'}", flush=True)
    stop_ollama(process)
    return None


def stop_ollama(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
