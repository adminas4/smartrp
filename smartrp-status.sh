#!/usr/bin/env bash
set -u
section(){ printf "\n==== %s ====\n" "$1"; }
cd /srv/smartrp 2>/dev/null || { echo "/srv/smartrp not found"; exit 1; }

section "GIT"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "-- remote:"; git remote -v
  echo "-- branch:"; git branch -vv
  echo "-- last commits:"; git log --oneline -n 10
  echo "-- status:"; git status -sb
  echo "-- authors:"; git shortlog -sn --all
else
  echo "Ne git repo"
fi

section "KODO DYDIS"
if command -v cloc >/dev/null 2>&1; then
  cloc backend frontend 2>/dev/null || true
else
  echo "(cloc nėra) failų skaičius:"
  find backend frontend -type f \( -name '*.py' -o -name '*.ts' -o -name '*.js' -o -name '*.vue' -o -name '*.html' -o -name '*.css' \) | wc -l
  echo "Python eilučių (apytiksliai):"
  find backend -type f -name '*.py' -print0 | xargs -0 wc -l 2>/dev/null | tail -n1
fi

section "FASTAPI ENDPOINT'AI"
curl -sS http://127.0.0.1:8000/openapi.json | jq -r '.paths|keys[]' 2>/dev/null || echo "openapi.json nepasiekiamas"

section "HEALTH"
echo -n "public:  "; curl -sS https://smartrp.org/health 2>/dev/null; echo
echo -n "local:   ";  curl -sS http://127.0.0.1:8000/health 2>/dev/null; echo

section "PRICING TESTAS"
cat >/tmp/items-no.json <<'JSON'
{"items":[
  {"name":"Gipsplate 12,5 1200x2400"},
  {"name":"Rockwool 100 mm isolasjon"},
  {"name":"Treskrue 5x80"},
  {"name":"ELKO RS16 dobbel stikkontakt"}
]}
JSON
curl -sS http://127.0.0.1:8000/api/pricing/suggest \
  -H 'content-type: application/json' --data @/tmp/items-no.json \
  | jq -c '.results[] | {q:.query, offers:(.offers|length), sample:(.offers[0]//null)}' 2>/dev/null || echo "pricing nepavyko"

section "SYSTEMD"
systemctl --no-pager -l status smartrp-api | sed -n '1,15p'

section "FAIL2BAN"
systemctl is-active --quiet fail2ban && fail2ban-client status nginx-smartapi 2>/dev/null || echo "fail2ban/nginx-smartapi nėra aktyvus"

section "NGINX"
nginx -t
grep -n 'location /api/' /etc/nginx/sites-available/smartrp.org 2>/dev/null || true
