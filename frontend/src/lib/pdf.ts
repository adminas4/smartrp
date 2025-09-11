// frontend/src/lib/pdf.ts
import type { AnalyserResponse, RecalcResponse } from "../types";

const fmtMoney = (v:number, cur:string="NOK") =>
  new Intl.NumberFormat("nb-NO",{style:"currency",currency:cur}).format(v||0);

export function exportPdf(
  desc: string,
  data: AnalyserResponse,
  totals?: RecalcResponse["totals"]
) {
  const cur = totals?.currency || "NOK";
  const today = new Date().toLocaleString("nb-NO");

  const rows = {
    materials: (data.materials||[]).map(m=>`<tr><td>${m.name||""}</td><td>${m.qty||0}</td><td>${m.unit||""}</td></tr>`).join(""),
    workflow: (data.workflow||[]).map(w=>`<tr><td>${w.task||""}</td><td>${w.hours||0}</td></tr>`).join(""),
    crew: (data.crew||[]).map(c=>`<tr><td>${c.role||""}</td><td>${c.count||0}</td></tr>`).join(""),
    tools: (data.tools||[]).map(t=>`<tr><td>${t.name||""}</td><td>${t.days||0}</td></tr>`).join(""),
  };

  const tot = totals ? `
    <table class="kv">
      <tbody>
        <tr><th>Materialer</th><td>${fmtMoney(totals.materials,cur)}</td></tr>
        <tr><th>Arbeid</th><td>${fmtMoney(totals.labor,cur)}</td></tr>
        <tr><th>Verktøy</th><td>${fmtMoney(totals.tools,cur)}</td></tr>
        <tr><th>Overhead</th><td>${fmtMoney(totals.overhead,cur)}</td></tr>
        <tr><th>Fortjeneste</th><td>${fmtMoney(totals.profit,cur)}</td></tr>
        <tr><th>Total</th><td><strong>${fmtMoney(totals.total,cur)}</strong></td></tr>
      </tbody>
    </table>` : `<p>Ingen totals.</p>`;

  const html = `<!doctype html><html lang="nb">
  <head>
    <meta charset="utf-8"/>
    <title>SmartRP estimat</title>
    <style>
      *{box-sizing:border-box} body{font:12pt/1.45 ui-sans-serif,system-ui,Segoe UI,Roboto; color:#0f172a; margin:24px}
      header{display:flex; align-items:center; justify-content:space-between; margin-bottom:12px}
      .brand{display:flex; gap:12px; align-items:center}
      .brand img{height:28px}
      h1{font-size:18pt; margin:0}
      h2{font-size:12pt; margin:18px 0 8px}
      .grid{display:grid; grid-template-columns:1fr 1fr; gap:16px}
      table{width:100%; border-collapse:collapse; font-size:10.5pt}
      th,td{border:1px solid #e2e8f0; padding:6px}
      th{background:#f8fafc; text-align:left}
      .kv th{width:45%}
      .muted{color:#64748b}
      .desc{white-space:pre-wrap; border:1px solid #e2e8f0; padding:8px; border-radius:8px}
      footer{margin-top:16px; color:#64748b; font-size:10pt}
      @media print { .no-print{display:none} }
    </style>
  </head>
  <body>
    <header>
      <div class="brand">
        <img src="/logo.png" alt="SmartRP"/>
        <div>
          <div style="font-weight:600">SmartRP demo</div>
          <div class="muted">Automatisk estimat og prisberegning</div>
        </div>
      </div>
      <div class="muted">${today}</div>
    </header>

    <h1>Estimat</h1>
    <h2>Beskrivelse</h2>
    <div class="desc">${desc ? desc.replace(/[<>&]/g, s=>({ '<':'&lt;','>':'&gt;','&':'&amp;' } as any)[s]) : "-"}</div>

    <h2>Kostnadsoversikt</h2>
    ${tot}

    <div class="grid">
      <div>
        <h2>Materialer</h2>
        <table><thead><tr><th>Navn</th><th>Mengde</th><th>Enhet</th></tr></thead><tbody>${rows.materials||""}</tbody></table>
      </div>
      <div>
        <h2>Arbeidsflyt</h2>
        <table><thead><tr><th>Oppgave</th><th>Timer</th></tr></thead><tbody>${rows.workflow||""}</tbody></table>
      </div>
      <div>
        <h2>Mannskap</h2>
        <table><thead><tr><th>Rolle</th><th>Antall</th></tr></thead><tbody>${rows.crew||""}</tbody></table>
      </div>
      <div>
        <h2>Verktøy</h2>
        <table><thead><tr><th>Navn</th><th>Dager</th></tr></thead><tbody>${rows.tools||""}</tbody></table>
      </div>
    </div>

    <footer>
      Generert av SmartRP • Valuta: ${cur}
    </footer>

    <div class="no-print" style="margin-top:12px">
      <button onclick="window.print()">Skriv ut / Lagre som PDF</button>
    </div>
  </body></html>`;

  const w = window.open("", "_blank");
  if (!w) return;
  w.document.open();
  w.document.write(html);
  w.document.close();
  setTimeout(() => { try { w.focus(); w.print(); } catch {} }, 400);
}
