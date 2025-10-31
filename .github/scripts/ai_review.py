import os`nimport sys`nimport subprocess`nimport json`nimport requests

BASE = os.getenv("GITHUB_BASE_REF") or "master"
subprocess.run(["git","fetch","origin", BASE], check=True)

try:
    diff = subprocess.check_output(["git","diff","--unified=0","FETCH_HEAD...HEAD"], text=True, errors="ignore")
except Exception:
    diff = ""

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

headers = {
    "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY','')}",
    "Content-Type": "application/json"
}
payload = {"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],"temperature":0.2}

try:
    r = requests.post("https://api.openai.com/v1/chat/completions", data=json.dumps(payload), headers=headers, timeout=60)
    if r.status_code >= 400:
        msg = f"OpenAI API error {r.status_code}:\n{r.text}"
        print(msg)
        open("ai_review.md","w",encoding="utf-8").write(msg)
        sys.exit(0)
    out = r.json()["choices"][0]["message"]["content"]
except Exception as e:
    out = f"AI review failed: {e}"

open("ai_review.md","w",encoding="utf-8").write(out)

