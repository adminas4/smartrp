# SmartRP backend

- Servisas startuoja su `uvicorn app.main:app`.
- OpenAI raktas laikomas **/etc/smartrp.env** (ne repo).
- Testas: `curl -fsS http://127.0.0.1:8000/healthz`.

## .env example (nelaikyti tikro rakto)
OPENAI_MODEL_ANALYZE=gpt-4o
# OPENAI_API_KEY= (naudojamas /etc/smartrp.env)
