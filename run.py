import uvicorn
from local_runtime import start_ollama, stop_ollama

if __name__ == "__main__":
    process = start_ollama()
    try:
        print("Open http://127.0.0.1:8001 — local AI, no API key needed.", flush=True)
        uvicorn.run("app:app", host="127.0.0.1", port=8001, access_log=False)
    finally:
        stop_ollama(process)
