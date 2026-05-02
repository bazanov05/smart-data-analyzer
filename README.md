# Smart AML Analyzer

A containerized application for detecting financial crimes in transaction data. Upload a CSV, run automated AML analysis, and consult an AI compliance agent — all from an interactive dashboard.

---

## What it does

The system runs four detection algorithms on uploaded transaction data:

- **Structuring detection** — finds senders splitting large amounts into smaller transactions to stay below reporting thresholds, using a rolling time window
- **High velocity transfers** — identifies accounts making an unusually high number of transactions within a short period (layering)
- **Geographic risk** — flags inflows from high-risk jurisdictions (IR, KP, SY, RU, BLR)
- **Unverified originators** — surfaces first-time senders with no transaction history

Results are stored in a database and accessible via an interactive dashboard. An AI agent powered by Claude can answer natural language questions about flagged activity and generate compliance summaries.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite |
| Data processing | Pandas, NumPy |
| AI agent | LangChain, Anthropic Claude |
| Frontend | Streamlit |
| Infrastructure | Docker, Docker Compose |

---

## Requirements

- Docker and Docker Compose installed
- An Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

---

## Getting started

**1. Clone the repository**

```bash
git clone https://github.com/your-username/smart-data-analyzer.git
cd smart-data-analyzer
```

**2. Create a `.env` file in the project root**

```
ANTHROPIC_API_KEY=your_api_key_here
BACKEND_URL=http://backend:8000
```

**3. Build and start the containers**

```bash
docker compose up --build
```

**4. Open the dashboard**

- Frontend: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## CSV format

Your CSV file must contain these exact columns:

| Column | Type | Example |
|---|---|---|
| transaction_id | string | TXN001 |
| sender_id | string | SENDER_A |
| receiver_id | string | RECEIVER_X |
| amount | number | 9500 |
| country | string | PL |
| type | string | wire_transfer |
| timestamp | datetime | 2024-01-15 08:23:00 |

The API will return a `400` error listing any missing columns.

---

## Usage

1. Open http://localhost:8501
2. Upload a CSV file using the sidebar uploader
3. Click **Analyze** — the system runs all four detections and saves results
4. Navigate the sidebar to explore flagged reports
5. Open **AI agent** to ask questions like:
   - *"Give me a full AML summary for today"*
   - *"Which senders should I escalate?"*
   - *"Are there any high-risk geographic patterns?"*

---

## Project structure

```
app/
  api/
    transactions.py     # FastAPI routes
  db/
    models.py           # SQLAlchemy models
    schemas.py          # Pydantic schemas
    repository.py       # Database operations
    database.py         # Engine and session setup
  services/
    analyzer.py         # AML detection algorithms
    ai_agent.py         # LangChain agent
    tools.py            # Agent database tools
  frontend/
    dashboard.py        # Streamlit app entry point
    api.py              # HTTP client for backend
    pages/              # One file per dashboard page
        ai_agent_page.py
        ai_sum_page.py
        geo_inflow_page.py
        high_velocity_page.py
        overview_page.py
        structuring_page.py
        unverified_page.py
Dockerfile.backend
Dockerfile.frontend
docker-compose.yml
requirements.txt
```

---

## Running without Docker

**Backend:**
```bash
uvicorn app.api.transactions:app --reload
```

**Frontend** (in a separate terminal):
```bash
streamlit run -m app/frontend/dashboard.py
```

Make sure `ANTHROPIC_API_KEY` is set in your environment and `BACKEND_URL` is not set (it defaults to `http://localhost:8000`).

---

## Notes

- The SQLite database file (`aml_database.db`) is persisted via a Docker volume — data survives container restarts
- Uploading the same CSV twice is handled gracefully — duplicate transactions are skipped silently
- The AI agent requires a valid Anthropic API key to function — all other features work without one