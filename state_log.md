# SmartRP – State Log

## 🔹 Kur esame dabar
- ✅ Backend testai praeina (`15 passed`).
- ✅ Legacy v1/update suderintas su testais.
- ✅ /api/estimate/analyze – veikia skeletas + vieta AI JSON-only kvietimui.
- ✅ Recalc logika – `AIEstimateService.recalculate(...)`.
- ✅ Systemd servisas su `backend.app.main:app`.

## 🔸 Darbai dabar
- [ ] Užpildyti `_call_openai_json_only` realiu OpenAI kvietimu (JSON-only).
- [ ] Frontend modulyje prijungti `recalculate` ir parodyti breakdown (materials_sum, labor_sum, totals).
- [ ] Sukurti paprastą „Runbook“ /docs/runbook.md.

## 🔶 Prioritetiniai sekantys žingsniai
- [ ] Įdėti rate-limit / timeouts AI kvietime.
- [ ] Pridėti kontraktinius testus AI atsakymui (schema-validation).
- [ ] CI skriptas „lint → test → build“.

