# 💰 FinanceBot Pro — AI-Powered Financial Advisor (MVP)

An AI financial-advisor MVP: a **FastAPI + MongoDB** back-end that serves
personalised financial planning, investment strategies and risk-management
insights, paired with a **React** front-end.

> This is the MVP described in the project brief — a working framework, not a
> regulated financial-advice product.

## Features

- **AI advisory chat** — conversation history persisted in MongoDB
  (`chat_history_test.py` exercises the flow)
- **Pluggable LLM providers** — the repo ships integration tests for
  **NVIDIA Nemotron** (`nemotron_model_test.py`) and **Palmyra**
  (`palmyra_chat_test.py`, `single_palmyra_test.py`), plus a
  **non-AI fallback path** (`backend_non_ai_test.py`)
- **Authentication** — JWT sessions with hashed passwords (`pyjwt`, `passlib`)
- **Financial planning topics** — budgeting, investment strategy, risk profiling

## Stack

| Layer | Technology |
| :--- | :--- |
| Back-end | FastAPI 0.110, Uvicorn, Pydantic v2 |
| Database | MongoDB (`pymongo` + async `motor`) |
| Auth | JWT (`pyjwt`), `passlib`, `email-validator` |
| Integrations | NVIDIA Nemotron / Palmyra LLM endpoints, AWS S3 via `boto3` |
| Front-end | React (CRA), React Router, Axios |
| Testing | `pytest` suite in `tests/` + standalone integration scripts |

## Project layout

```text
.
├── backend/
│   ├── server.py            # FastAPI app (app = FastAPI(title="FinanceBot Pro API"))
│   ├── config.py            # settings / environment loading
│   ├── utils/               # helpers
│   └── requirements.txt
├── frontend/                # React client
├── tests/                   # pytest suite
├── backend_test.py          # API smoke tests
├── backend_non_ai_test.py   # non-AI fallback path
├── chat_history_test.py     # conversation persistence
├── nemotron_model_test.py   # NVIDIA Nemotron integration
├── palmyra_chat_test.py     # NVIDIA Palmyra chat
└── single_palmyra_test.py   # single-turn Palmyra call
```

## Running locally

### Back-end

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    |    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` (or export environment variables) for MongoDB and your LLM
provider — see `backend/config.py` for the exact variable names — then start
the API:

```bash
uvicorn server:app --reload
# or: python server.py
```

### Front-end

```bash
cd frontend
npm install
npm start          # http://localhost:3000
```

## Tests

```bash
pytest tests/
python backend_test.py
```

## Notes

- `.emergent/` and `.gitconfig` are leftovers from the starter template and are
  safe to delete.
- No `.env` or API keys are committed — bring your own MongoDB URI and model
  credentials.
