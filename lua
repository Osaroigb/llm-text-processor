llm-text-processor/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI entrypoint
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # /analyze + /search endpoints
│   │ 
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Settings (DB, API keys, etc.)
│   │   └── db.py              # Database connection (SQLAlchemy/Postgres)
│   │ 
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py     # OpenAI API integration
│   │   └── nlp_utils.py       # Keyword extraction (noun frequency)
│   │ 
│   ├── models/
│   │   ├── __init__.py
│   │   └── analysis.py        # SQLAlchemy model for storing results
│   │ 
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   ├── responses.py
│   │   └── analysis.py        # Pydantic schemas for request/response
│   │ 
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_nlp_utils.py
│       └── test_llm_service.py
│ 
├── migrations/                # Alembic migrations for Postgres
│   └── README
│ 
├── scripts/
│   └── init_db.py             # Helper to initialize DB
│ 
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example               # Env template (DB_URL, OPENAI_KEY, etc.)
├── .gitignore
├── README.md
└── pyproject.toml             # since we are using Poetry instead of pip
