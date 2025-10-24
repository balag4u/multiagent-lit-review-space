# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Orchestrator
from utils import load_json
import os

# Initialize FastAPI app
app = FastAPI()

# Load config and docs
HERE = os.path.dirname(__file__)
models_cfg = load_json(os.path.join(HERE, "models_config.json"))
pubmed = load_json(os.path.join(HERE, "sample_data", "pubmed_sample.json"))
patents = load_json(os.path.join(HERE, "sample_data", "patents_sample.json"))
docs = pubmed + patents

# Initialize orchestrator once
orch = Orchestrator(docs, {
    "embed_model": models_cfg["embed_model"],
    "summarizer_model": models_cfg["summarizer_model"]
})

# Define request schema
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/api/query")
async def query_endpoint(body: QueryRequest):
    """
    Programmatic endpoint for integrations.
    Example POST body:
    {
      "query": "neutralizing antibody patents + clinical trials 2019-2024",
      "top_k": 5
    }
    """
    result = orch.run(body.query, top_k=body.top_k)
    return result