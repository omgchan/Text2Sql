# Agentic Text-to-SQL (Prototype)

This prototype implements an agentic Text-to-SQL pipeline with modular agents:

- Decomposition agent (structured understanding)
- SQL generation agent
- SQL validator
- PostgreSQL executor
- Retry/self-correction agent
- Logging and evaluation

Run the FastAPI app:

```bash
pip install -r project/requirements.txt
cp .env.example .env
# fill .env with your credentials
uvicorn project.app.main:app --reload
```

API:
- POST /agent/sql {"question": "..."}

The project includes prompt templates in `project/prompts` and a small benchmark runner.
