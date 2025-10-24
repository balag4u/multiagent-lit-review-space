---
title: Multiagent Lit Review Space
emoji: 👁
colorFrom: indigo
colorTo: indigo
sdk: streamlit
sdk_version: 1.30.0
app_file: streamlit_app.py
pinned: false
---
# Multi-Agent Literature + Patent Aggregator (HF Space POC)

This Streamlit Space demonstrates a multi-agent pipeline for literature review and patent aggregation, returning summaries with provenance.

## How to run locally
1. `git clone <repo>`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `streamlit run streamlit_app.py`
5. Open `http://localhost:8501`

## Deploy to Hugging Face Spaces
1. Create a new Space on Hugging Face, runtime: `Streamlit`, SDK: `Python`.
2. Push this repository to the new Space (via `git push` following HF instructions).
3. The Space will run in the HF environment. If dependency issues, adjust `requirements.txt`.

## Extensibility
- Replace sample_data retrieval with:
  - PubMed Entrez API (NCBI E-utilities) for live search.
  - PatentsView (or Google Patent Public Datasets / Orbit) API for patents.
- Swap summarizer with larger models or LLM inferencing.
- Add citation formatting (APA / Vancouver) and DOI lookups.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
