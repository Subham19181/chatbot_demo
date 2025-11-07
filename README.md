# NDOC Chatbot — Local MiniLM + FAISS Semantic Retrieval

A lightweight, offline-friendly chatbot that performs **semantic search and Q&A retrieval** using **local embeddings** with [Sentence Transformers (MiniLM)](https://www.sbert.net/) and [FAISS](https://faiss.ai/).  
No cloud embedding APIs required — fast, reliable, and free of quota limits.

---

## Project Structure

project/
├── app.py # FastAPI server (main application)
├── data/
│ ├── qa_data.json # Q&A dataset
│ ├── question_embs.npy # Precomputed embeddings (generated once)
├── scripts/
│ └── precompute_embeddings.py # Script to generate and save question embeddings
├── .env # Optional: environment variables
└── README.md # This file

## Prerequisites

Make sure you have:

1. Python 3.9 or higher (Python 3.10+ recommended)
2. pip installed
3. git (repo link - https://github.com/Subham19181/chatbot_demo.git)

## Run Locally

1. Clone the repo

`git clone <https://github.com/Subham19181/chatbot_demo.git>
cd NDOC-Chatbot`

2. Setup the environment (mac or linux)

`python3 -m venv .venv
source .venv/bin/activate`

2. windows

`python -m venv .venv
.venv\Scripts\activate`

3. Install dependencies

`pip install -r requirements.txt`

4. Start the server

`uvicorn app:app --reload`

5. Check server status

`curl http://127.0.0.1:8000`

6. Ask a Question

`curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"user_input":"How long does shipping take?"}'`

7. Get random suggestions

`curl http://127.0.0.1:8000/suggestions`
