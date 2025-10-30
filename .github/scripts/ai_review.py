import os, sys, subprocess, json, requests

BASE = os.getenv("GITHUB_BASE_REF") or "master"
subprocess.run(["git","fetch","origin",BASE], check=True)
diff = subprocess.check_output(["git","diff","--unified=0","FETCH_HEAD...HEAD"], text=True, errors="ignore")

if not diff.strip():
    open("ai_review.md","w",encoding="utf-8").write("AI review: no changes detected.")
    sys.exit(0)

prompt = f"""You're a senior reviewer for SmartRP (FastAPI, Pydantic, Alembic, QR Work Time, Estimate Analyze, Risk Advisor).
Review this unified diff and output only Markdown with:
- Security issues
- Breaking API changes vs swagger.yaml if implied
- DB migration needs
- Missing tests
- Style/type issues
- Actionable fixes with file:line

Diff:
{diff[:30000]}
"""

headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}
payload = {"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],"temperature":0.2}
r = requests.post("https://api.openai.com/v1/chat/completions", data=json.dumps(payload), headers=headers, timeout=60)
r.raise_for_status()
out = r.json()["choices"][0]["message"]["content"]
open("ai_review.md","w",encoding="utf-8").write(out)
