# FinLex AI

> AI-powered assistant for Indian Accounting & Law professionals.

FinLex AI helps Chartered Accountants, Lawyers, Tax Consultants, and Company Secretaries with:
- **Tax Calculations** — Income Tax (Old & New Regime), GST, TDS/TCS, Advance Tax
- **Legal Document Drafting** — NDAs, Legal Notices, Board Resolutions, Engagement Letters
- **Knowledge Q&A** — Indian Tax Law (FY 2025-26), GST 2.0, Companies Act, Contract Law
- **Financial Analysis** — Financial Ratios, Depreciation (SLM/WDV)
- **Document Intelligence** — Upload PDFs/DOCX for RAG-powered Q&A

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Python 3.12, SQLAlchemy (async), PostgreSQL |
| **AI/LLM** | LangChain, OpenAI GPT-4o / Ollama Llama3, ChromaDB |
| **Frontend** | Next.js 15, React 19, TailwindCSS, TypeScript |
| **Auth** | Clerk |
| **Payments** | Razorpay |
| **Infrastructure** | Docker, Redis |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (or Ollama for local LLM)
- Clerk account (for auth)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd finlex-ai
cp .env.example .env
# Edit .env with your API keys
cp frontend/.env.local.example frontend/.env.local
# Edit frontend/.env.local with Clerk keys
```

### 2. Start with Docker

```bash
docker-compose up -d
```

This starts:
- **Backend** at http://localhost:8000
- **Frontend** at http://localhost:3000
- **PostgreSQL** at localhost:5432
- **Redis** at localhost:6379

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
finlex-ai/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agent.py          # LangChain agent with tools
│   │   │   ├── embeddings.py     # Embedding model factory
│   │   │   ├── rag.py            # RAG pipeline (ChromaDB)
│   │   │   ├── prompts/          # System prompts
│   │   │   │   ├── accounting.py # Indian accounting/tax prompt
│   │   │   │   └── legal.py      # Indian law prompt
│   │   │   └── tools/            # LangChain tools
│   │   │       ├── tax_calculator.py
│   │   │       ├── gst_calculator.py
│   │   │       ├── document_drafter.py
│   │   │       └── financial_tools.py
│   │   ├── api/                  # FastAPI route handlers
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── calculator.py
│   │   │   └── admin.py
│   │   ├── core/                 # Security, middleware
│   │   ├── knowledge_base/       # Indian tax/law data (JSON)
│   │   │   ├── tax/
│   │   │   └── legal/
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   └── services/             # Business logic layer
│   ├── alembic/                  # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js App Router pages
│   │   ├── components/           # React components
│   │   └── lib/                  # API client
│   └── package.json
├── docker-compose.yml
└── .env
```

## Knowledge Base

The AI is pre-loaded with verified Indian tax and law data:

| Data | Coverage |
|------|----------|
| Income Tax Slabs | FY 2025-26 (Old & New Regime) |
| GST Rates | Post GST 2.0 (Sep 2025) |
| TDS/TCS Rates | 30+ sections with thresholds |
| Tax Deductions | 80C, 80D, 80CCD, HRA, LTA, etc. |
| Compliance Calendar | IT, GST, Companies Act deadlines |
| Contract Templates | 7 common Indian contract types |

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Plans & Pricing

| Feature | Free | Professional | Firm | Enterprise |
|---------|------|-------------|------|------------|
| Queries/month | 50 | 500 | 2000 | Unlimited |
| Documents | 5 | 50 | 200 | Unlimited |
| Users | 1 | 3 | 20 | Unlimited |

## License

Proprietary — All rights reserved.

## Disclaimer

FinLex AI provides AI-generated information for educational purposes. Always verify with a qualified Chartered Accountant or Lawyer before acting on any information. This tool does not constitute professional advice.
