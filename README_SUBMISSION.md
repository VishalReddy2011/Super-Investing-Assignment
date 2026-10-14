# Super Investing · AI Research Agent

A lightweight AI research agent that reads company documents and writes a clear 1-page research brief for retail stock investors.

Built with **Google Agent Development Kit (ADK)** and **Gemini 3.1 Flash Lite**.

---

## What the Agent Does

1. **Checks the Right Company:** Ignores documents about different companies with similar names (e.g. discards news about a local cable TV operator in Nagpur).
2. **Prioritizes Recent Data:** Uses current 2026 exchange filings over outdated 2024 news articles.
3. **Catches Conflicting Numbers:** Spots when media reports contradict official company filings (e.g. ₹1,428 cr in news vs ₹1,248 cr in the official press release) and flags them in *Open Questions*.
4. **Ignores Fake Tips:** Bypasses unverified stock-tip blogs and ignores hidden prompt-injection attempts.
5. **Bonus Live Tools (NSE Data + News Search):** Combines real-time NSE market metrics with live financial news search to research real Indian companies (e.g. `POLYCAB`, `RELIANCE`).

---

## Model Choice

* **Model:** `gemini-3.1-flash-lite`
* **Why:** Fast response times (~3 seconds), reliable on the free-tier API, and follows structured instructions accurately.

---

## Setup & How to Run

### 1. Setup (using `uv`)
```powershell
uv venv .venv
uv pip install --python .venv google-adk yfinance python-dotenv
```

### 2. Configure API Key
Create or edit `.env`:
```env
GEMINI_API_KEY="your-api-key-here"
MODEL_NAME="gemini-3.1-flash-lite"
```

### 3. Run the Agent
```powershell
.venv\Scripts\python.exe agent.py
```
* Generates the brief and saves it to `briefs/brief_SRVCABLE.md`.

### 4. Run on a Live NSE Stock (Bonus)
Pass any real NSE ticker directly:
```powershell
.venv\Scripts\python.exe agent.py INFY
```

* Automatically fetches live market data from NSE and saves to `briefs/brief_<ticker>.md`.

---

## Repository Files

* `agent.py`: Agent code built on Google ADK with dynamic tool calling.
* `system_prompt.txt`: System prompt with instructions and rules.
* `research_pack/`: 8 test documents for Sarvottam Cables Ltd.
* `briefs/`: Directory containing all generated research briefs.
* `.env`: API key configuration (kept private).

---

## Test Log

### Run 1: Gemma Models -> Gemini Flash Lite
* **What went wrong:** Tried open-source Gemma models (`gemma-4-26b` / `31b`), but they threw 404/500 API errors when given system prompts and agent sessions.
* **What changed:** Switched to `gemini-3.1-flash-lite`, which worked instantly with fast (~3s) responses and native tool support.

### Run 2: First Full Run on SRVCABLE
* **What went wrong:** Windows terminal crashed with an encoding error when trying to print the Rupee (`₹`) symbol. Also, relative dates in the prompt were hardcoded to 2025.
* **What changed:** Added UTF-8 stdout reconfiguration, saved the brief directly to disk, and updated dates to dynamic handling.

### Run 3: Live NSE Tool & Prompt Cleanup
* **What went wrong:** Python was pre-fetching live data instead of letting the agent call the tool itself for debugging reasons.
* **What changed:** Let the agent dynamically call `fetch_live_data` when given an NSE ticker (tested on `INFY` and `POLYCAB`).
