# app.py
import os
import json
from pathlib import Path
import numpy as np
import faiss
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# Optional: only if you want to use cloud text-generation for paraphrase
USE_GENAI = os.getenv("PARAPHRASE_WITH_GENAI", "True").lower() in ("1","true","yes")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")  # required only if USE_GENAI True

if USE_GENAI:
    from google import genai
    client = genai.Client(api_key=GENAI_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Data paths
QA_PATH = Path("data/qa_data.json")
EMB_PATH = Path("data/question_embs.npy")

if not QA_PATH.exists():
    raise FileNotFoundError("Please create data/qa_data.json (list of {question,answer})")

if not EMB_PATH.exists():
    raise FileNotFoundError("Please run scripts/precompute_embeddings.py to create question_embs.npy")

# Load QA and embeddings
with open(QA_PATH, "r", encoding="utf-8") as f:
    qa_data = json.load(f)

question_embeddings = np.load(EMB_PATH)  # shape: (N, dim)
if question_embeddings.dtype != np.float32:
    question_embeddings = question_embeddings.astype(np.float32)

# Build FAISS index once
dim = question_embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(question_embeddings)
logger.info("FAISS index loaded with %d vectors (dim=%d)", index.ntotal, dim)

# Local sentence-transformers model (for user embeddings)
LOCAL_MODEL_NAME = os.getenv("LOCAL_SBERT_MODEL", "all-MiniLM-L6-v2")
local_encoder = SentenceTransformer(LOCAL_MODEL_NAME)

@app.get("/")
async def root():
    return {"status": "running", "endpoints": ["/chat (POST)", "/suggestions (GET)"]}

def embed_local(text: str):
    vec = local_encoder.encode(text)
    return np.array(vec, dtype=np.float32)

def get_top_matches(query_vec, k=4):
    query_vec = query_vec.reshape(1, -1).astype(np.float32)
    D, I = index.search(query_vec, k=min(k, index.ntotal))
    return D[0], I[0].tolist()

async def paraphrase_with_genai(text: str, conversation_history=None):
    """Optional single-call paraphrase step using cloud generation (one API call per request).
       Only executed if USE_GENAI is True.
    """
    if not USE_GENAI:
        return text

    # Minimal prompt: include optional sequential history so paraphrase respects last context
    history_str = ""
    if conversation_history:
        for turn in conversation_history[-4:]:  # last 4 turns
            role = turn.get("role", "user")
            t = turn.get("text", "")
            history_str += f"\n{role.upper()}: {t}"
    prompt = f"""
You are a helpful assistant. Paraphrase the answer below to be friendly and concise. Keep meaning intact.

Conversation context: {history_str}

Answer to paraphrase:
{text}

Paraphrased answer:
"""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # Try robust extraction
    if hasattr(resp, "text"):
        return resp.text.strip()
    # fallback
    return str(resp).strip()

@app.post("/chat")
async def chat(req: Request):
    """
    Body JSON:
    {
      "user_input": "Hello, how long is shipping?",
      "history": [{"role":"user","text":"..."}]   # optional (simple sequential context)
    }
    """
    body = await req.json()
    user_input = (body.get("user_input") or "").strip()
    history = body.get("history", None)  # optional

    if not user_input:
        return {"error": "No user_input provided"}

    # quick local greeting handling (optional)
    if user_input.lower().strip() in ("hi","hello","hey","hello!"):
        return {"reply": "Hi! How can I help?", "suggested_questions": []}

    try:
        qvec = embed_local(user_input)
        D, I = get_top_matches(qvec, k=4)

        top_idx = int(I[0]) if len(I) > 0 else None
        if top_idx is None:
            return {"reply": "Sorry, I don't have an answer for that right now.", "suggested_questions": []}

        top_item = qa_data[top_idx]
        top_answer = top_item.get("answer", "")

        # OPTIONAL: paraphrase with a single generate_content call if enabled
        if USE_GENAI:
            try:
                paraphrased = await paraphrase_with_genai(top_answer, conversation_history=history)
                reply = paraphrased or top_answer
            except Exception as e:
                logger.error("GenAI paraphrase failed: %s", e, exc_info=True)
                reply = top_answer
        else:
            reply = top_answer

        # provide a few suggested questions (exclude top)
        suggested = []
        for idx in I:
            if int(idx) != top_idx and len(suggested) < 3:
                suggested.append(qa_data[int(idx)]["question"])

        return {
            "reply": reply,
            "top_match": top_item["question"],
            "suggested_questions": suggested
        }
    except Exception as e:
        logger.exception("Unexpected error in /chat")
        return {"error": "Internal error", "details": str(e)}
