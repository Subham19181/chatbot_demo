# scripts/precompute_embeddings.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_PATH = Path("data/qa_data.json")
OUT_EMB = Path("data/question_embs.npy")

def main():
    model = SentenceTransformer(MODEL_NAME)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        qa = json.load(f)

    questions = [item["question"] for item in qa] 
    # encode in a batch
    embeddings = model.encode(questions, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    np.save(OUT_EMB, embeddings)
    print(f"Saved {embeddings.shape} embeddings to {OUT_EMB}")

if __name__ == "__main__":
    main()
