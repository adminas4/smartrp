PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup test run lint fmt api clean

setup:
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest -q

run:
	$(PY) -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

lint:
	.venv/bin/ruff .

fmt:
	.venv/bin/black --check .

api:
	$(PY) - << 'PY'
	from fastapi.testclient import TestClient
	from backend.app.main import app
	c = TestClient(app)
	print(c.get("/openapi.json").status_code)
	PY

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} \;
	EOF
