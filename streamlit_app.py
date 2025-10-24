# streamlit_app.py
import streamlit as st
from agents import Orchestrator
from utils import load_json
import os
import json
import document_parsers

st.set_page_config(layout="wide")

st.title("Multi-Agent Literature + Patent Aggregator")

# Load config
HERE = os.path.dirname(__file__)
models_cfg = load_json(os.path.join(HERE, "models_config.json"))

# Cache the orchestrator instance
@st.cache_resource
def get_orchestrator():
    return Orchestrator({
        "embed_model": models_cfg["embed_model"],
        "summarizer_model": models_cfg["summarizer_model"]
    })

orchestrator = get_orchestrator()

query = st.text_area("Enter your query here", "neutralizing antibody patents + clinical trials 2019-2024")
top_k = st.slider("Top K documents", min_value=1, max_value=20, value=5)

uploaded_files = st.file_uploader("Upload enterprise documents", accept_multiple_files=True, type=['pdf', 'docx', 'xlsx', 'pptx'])

def parse_uploaded_files(uploaded_files):
    documents = []
    for file in uploaded_files:
        if file.type == "application/pdf":
            text = document_parsers.parse_pdf(file)
            documents.append({"text": text, "source": file.name})
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = document_parsers.parse_docx(file)
            documents.append({"text": text, "source": file.name})
        elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            text = document_parsers.parse_xlsx(file)
            documents.append({"text": text, "source": file.name})
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            text = document_parsers.parse_pptx(file)
            documents.append({"text": text, "source": file.name})
    return documents

if st.button("Run pipeline"):
    with st.spinner("Running pipeline..."):
        enterprise_docs = parse_uploaded_files(uploaded_files)
        out = orchestrator.run(query, top_k=top_k, enterprise_docs=enterprise_docs)

        st.subheader("Executive Summary")
        st.write(out.get('executive_summary', ''))

        st.subheader("Results")
        for i, item in enumerate(out['items'], start=1):
            st.markdown(f"**{i}. {item['title']}**")
            st.markdown(f"**Summary:** {item['summary']}")
            prov = item['provenance']
            st.markdown(f"**Source:** {prov['ref'].get('source')} | **DOI:** {prov['ref'].get('doi') or ''} | [Link]({prov['ref'].get('url')})")
            st.markdown("---")

        with st.expander("Raw JSON Output"):
            st.json(out)
