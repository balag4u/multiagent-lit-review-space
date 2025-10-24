# agents.py  -- transformers-only embedding (no sentence-transformers)
from typing import List, Dict
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
from datetime import datetime
import hashlib
import numpy as np
from data_providers import search_pubmed, search_patents

class SimpleEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: int = None):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        if device is None:
            self.device = 0 if torch.cuda.is_available() else -1
        else:
            self.device = device
        if self.device >= 0:
            self.model = self.model.to(self.device)

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def encode(self, texts: List[str], show_progress_bar: bool = False):
        all_embs = []
        batch_size = 8
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            encoded_input = self.tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
            if self.device >= 0:
                encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}
            with torch.no_grad():
                model_output = self.model(**encoded_input)
            emb = self._mean_pooling(model_output, encoded_input['attention_mask'])
            emb = emb.cpu().numpy()
            norms = np.linalg.norm(emb, axis=1, keepdims=True)
            norms[norms == 0] = 1
            emb = emb / norms
            all_embs.append(emb)
        return np.vstack(all_embs)

class ExtractorAgent:
    def __init__(self):
        pass

    def extract(self, doc: Dict, query: str, max_sentences=3):
        text = doc.get('text') or doc.get('abstract') or ""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        keywords = [w.lower() for w in query.split() if len(w)>3]
        selected = []
        for s in sentences:
            sl = s.lower()
            if any(k in sl for k in keywords):
                selected.append(s)
            if len(selected) >= max_sentences:
                break
        if not selected:
            selected = sentences[:max_sentences]
        return " . ".join(selected)

class SummarizerAgent:
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        self.summarizer = pipeline("summarization", model=model_name, truncation=True)

    def summarize(self, text: str, max_len=120):
        try:
            out = self.summarizer(text, max_length=max_len, min_length=30, do_sample=False)
            return out[0]['summary_text']
        except Exception:
            return (text[:max_len*2] + "...") if len(text)>max_len*2 else text

class CitationAgent:
    def format_reference(self, doc: Dict):
        ref = {
            "title": doc.get("title"),
            "authors": doc.get("authors", []),
            "doi": doc.get("doi"),
            "source": doc.get("source"),
            "url": doc.get("url")
        }
        provenance = {
            "ref": ref,
            "retrieved_at": doc.get("_retrieved_at"),
            "score": doc.get("_score")
        }
        id_s = (doc.get("doi") or doc.get("url") or doc.get("title") or "") + str(provenance["retrieved_at"])
        provenance['id'] = hashlib.sha256(id_s.encode('utf-8')).hexdigest()
        return provenance

class Orchestrator:
    def __init__(self, models_config):
        embed_model = models_config.get('embed_model', "sentence-transformers/all-MiniLM-L6-v2")
        summarizer_model = models_config.get('summarizer_model', "sshleifer/distilbart-cnn-12-6")
        self.embedder = SimpleEmbedder(embed_model)
        self.extractor = ExtractorAgent()
        self.summarizer = SummarizerAgent(summarizer_model)
        self.citation = CitationAgent()

    def run(self, query: str, top_k: int = 5, enterprise_docs: List[Dict] = []):
        """
        Runs the multi-agent retrieval, extraction, summarization, and hierarchical executive summary pipeline.
        """
        # ---- Document-level processing ----
        pubmed_articles = search_pubmed(query, max_results=top_k)
        patents = search_patents(query, max_results=top_k)

        all_docs = pubmed_articles + patents + enterprise_docs

        texts = [d.get("text", d.get("abstract", "")) for d in all_docs]
        doc_embeddings = self.embedder.encode(texts)
        q_emb = self.embedder.encode([query])[0]
        sims = np.dot(doc_embeddings, q_emb)
        top_idx = sims.argsort()[::-1][:top_k]
        retrieved = []
        for idx in top_idx:
            doc = all_docs[int(idx)].copy()
            doc['_score'] = float(sims[int(idx)])
            doc['_retrieved_at'] = datetime.utcnow().isoformat() + "Z"
            retrieved.append(doc)

        results = []
        for doc in retrieved:
            passage = self.extractor.extract(doc, query)
            summary = self.summarizer.summarize(passage)
            prov = self.citation.format_reference(doc)
            results.append({
                "id": prov['id'],
                "title": doc.get("title"),
                "summary": summary,
                "provenance": prov
            })

        # ---- Hierarchical executive summarization ----
        all_summaries = [r["summary"] for r in results if r.get("summary")]
        full_text = " ".join(all_summaries)
        words = full_text.split()
        chunk_size = 700  # adjust as needed
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        layer1_summaries = []
        for chunk in chunks:
            layer1_summaries.append(self.summarizer.summarize(chunk, max_len=200))

        combined_text = " ".join(layer1_summaries)
        exec_summary = self.summarizer.summarize(combined_text, max_len=180) \
                        if len(combined_text.split()) > 30 else combined_text

        # ---- Return structured output ----
        return {
            "query": query,
            "executive_summary": exec_summary,
            "items": results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }