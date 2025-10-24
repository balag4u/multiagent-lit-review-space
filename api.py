# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Orchestrator
from utils import load_json
import os

# Initialize FastAPI app
app = FastAPI()

# Load config
HERE = os.path.dirname(__file__)
models_cfg = load_json(os.path.join(HERE, "models_config.json"))

# Initialize orchestrator once
orch = Orchestrator({
    "embed_model": models_cfg["embed_model"],
    "summarizer_model": models_cfg["summarizer_model"]
})

# Define request schema
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    enterprise_docs: list = []

@app.post("/api/query")
async def query_endpoint(body: QueryRequest):
    """
    Programmatic endpoint for integrations.
    Example POST body:
    {
      "query": "neutralizing antibody patents + clinical trials 2019-2024",
      "top_k": 5,
      "enterprise_docs": [
            {"text": "This is a sample document.", "source": "sample.txt"}
      ]
    }
    """
    result = orch.run(body.query, top_k=body.top_k, enterprise_docs=body.enterprise_docs)
    return result