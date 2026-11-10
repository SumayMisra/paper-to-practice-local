# Attribution and provenance

## Original project

Credit to **Vizuara AI** for [paper-to-notebook-traditional](https://github.com/VizuaraAI/paper-to-notebook-traditional), the traditional PDF-to-Jupyter-notebook demo for the Modern Software Developer 2.0 bootcamp.

The comparison in this repository's README is based on the original tracked source at revision [`e0d94a3a02883ca7335a6373ef555e13168c6aef`](https://github.com/VizuaraAI/paper-to-notebook-traditional/tree/e0d94a3a02883ca7335a6373ef555e13168c6aef). It does not attribute uncommitted local changes in the separate checkout to the original authors.

The original supplies the PDF-upload-to-notebook workflow, a FastAPI conversion endpoint, PyMuPDF extraction with regex heuristics, heuristic code-block extraction, and nbformat assembly/export. Those are existing capabilities, not new contributions claimed here.

## Work in this version

Paper to Practice is a separate local AI implementation developed from that workflow. Additions in this project include the browser interface and preview, model-generated teaching notebooks, audience/focus instructions, Ollama integration and runtime management, pypdf extraction with bounded excerpts and coverage notes, and structured-output/syntax validation with a bounded retry. Earlier iterations of this app used hosted APIs; the current code uses local Ollama only.

This project is not an official Vizuara release and does not claim ownership of Vizuara's original work. It does not package the sibling traditional repository or its Git history.

## Preserved upstream license notice

The inspected [original README](https://github.com/VizuaraAI/paper-to-notebook-traditional/blob/e0d94a3a02883ca7335a6373ef555e13168c6aef/README.md) contains this license statement, preserved verbatim:

> MIT — Part of the Modern Software Developer 2.0 bootcamp by [Vizuara AI](https://vizuara.ai).

There was no standalone `LICENSE` or `COPYING` file in that tracked revision or this app's source directory. No original license file has been removed, changed, or replaced. The statement above records the upstream notice; it is not a newly authored license grant for this implementation. A license for the additions has not been selected as part of this preparation.

Ollama and its bundled libraries, model weights, and installed Python packages have their own license notices. Their locally installed files and notices remain intact and are excluded from this source upload together with their containing runtime/environment directories.
