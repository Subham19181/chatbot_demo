# Chatbot Demo - Quick Start Guide

## Setup

### 1. Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# OR: .venv\Scripts\activate  # On Windows
```

### 2. Install dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3. Set environment variables (optional)
Create a `.env` file or export:
```bash
export PARAPHRASE_WITH_GENAI=False  # Set to True if you have a GenAI API key
export GENAI_API_KEY=your_api_key_here  # Only needed if PARAPHRASE_WITH_GENAI=True
```

## Running the Server

### Start the server
```bash
# Activate venv first
source .venv/bin/activate

# Start server
uvicorn app:app --host 127.0.0.1 --port 8000

# OR with auto-reload for development:
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Start in background
```bash
nohup .venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
```

## Testing the API

### Correct curl syntax (single line)
```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"user_input":"How long does shipping take?"}'
```

### Multi-line curl (if needed, escape properly)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input":"How long does shipping take?"}'
```
**Note:** Multi-line curl requires proper backslash escaping at the END of each line (before the newline). In some shells, this can cause issues - single-line is more reliable.

### Test with conversation history
```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"user_input":"What about construction?","history":[{"role":"user","text":"Do you offer estimates?"},{"role":"assistant","text":"Yes, we do!"}]}'
```

### Check server status
```bash
curl http://127.0.0.1:8000/
```

## Common Issues

### Issue: "externally-managed-environment" error
**Solution:** Use a virtual environment (see Setup step 1)

### Issue: curl returns "Internal Server Error" + JSONDecodeError
**Cause:** Malformed curl command (usually from line breaks)
**Solution:** Use single-line curl command OR properly escape backslashes in multi-line

### Issue: GenAI/paraphrase errors in logs
**Solution:** This is expected if `GENAI_API_KEY` is not set. The app will gracefully fall back to returning answers without paraphrasing.

## API Endpoints

### `GET /`
Returns server status and available endpoints.

### `POST /chat`
Main chat endpoint.

**Request body:**
```json
{
  "user_input": "Your question here",
  "history": [
    {"role": "user", "text": "Previous question"},
    {"role": "assistant", "text": "Previous answer"}
  ]
}
```

**Response:**
```json
{
  "reply": "The answer to your question",
  "top_match": "The matched question from knowledge base",
  "suggested_questions": ["Related question 1", "Related question 2"]
}
```
