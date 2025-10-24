# app.py
import gradio as gr
from utils import load_json
from agents import Orchestrator
import json
import os

# load config and sample data
HERE = os.path.dirname(__file__)
models_cfg = load_json(os.path.join(HERE, "models_config.json"))

pubmed = load_json(os.path.join(HERE, "sample_data", "pubmed_sample.json"))
patents = load_json(os.path.join(HERE, "sample_data", "patents_sample.json"))
docs = pubmed + patents

orchestrator = Orchestrator(docs, {
    "embed_model": models_cfg["embed_model"],
    "summarizer_model": models_cfg["summarizer_model"]
})

def run_pipeline(query, top_k):
    out = orchestrator.run(query, top_k=int(top_k))
    # prepare display
    items_html = ""
    for i, it in enumerate(out['items'], start=1):
        prov = it['provenance']
        items_html += f"<h4>{i}. {it['title']}</h4>"
        items_html += f"<p><b>Summary:</b> {it['summary']}</p>"
        items_html += f"<p><b>Source:</b> {prov['ref'].get('source')} &nbsp; DOI: {prov['ref'].get('doi') or ''} &nbsp; <a href='{prov['ref'].get('url')}' target='_blank'>link</a></p>"
        items_html += f"<hr/>"
    executive = out.get('executive_summary', '')
    json_out = json.dumps(out, indent=2, ensure_ascii=False)
    return executive, items_html, json_out

with gr.Blocks() as demo:
    gr.Markdown("# Multi-Agent Literature + Patent Aggregator (POC)")
    with gr.Row():
        query_input = gr.Textbox(label="Query", placeholder="E.g. neutralizing antibody patents + clinical trials 2019-2024", lines=2)
        top_k = gr.Slider(minimum=1, maximum=10, step=1, value=5, label="Top K documents")
    run_btn = gr.Button("Run pipeline")
    exec_summary = gr.Textbox(label="Executive summary", interactive=False)
    results_html = gr.HTML()
    results_json = gr.Code(label="Raw JSON output")
    run_btn.click(run_pipeline, inputs=[query_input, top_k], outputs=[exec_summary, results_html, results_json])
    gr.Markdown("Download: JSON / CSV (copy from JSON block).")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

# app.py (append this at the bottom)

import threading
import uvicorn
from api import app as fastapi_app

def run_fastapi():
    # Start FastAPI on a different port
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

# Start FastAPI in a background thread
threading.Thread(target=run_fastapi, daemon=True).start()