// frontend/src/App.tsx
import Nav from "./components/Nav";
import Hero from "./components/Hero";
import { useState, useEffect } from "react";
import { api } from "./lib/api";
import Totals from "./components/Totals";
import Pricing from "./components/Pricing";
import About from "./components/About";
import StatusBar from "./components/Status";
import Progress from "./components/Progress";
import { exportPdf } from "./lib/pdf";
import type {
  AnalyserResponse,
  RecalcResponse,
  Material,
  WorkflowItem,
  CrewMember,
  Tool,
} from "./types";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const SAMPLES = [
  "garasje 50 m² med plate på mark",
  "lite tre-ramme 3x3 m med OSB-kledning",
  "rehab av bad 6 m², flis + membran",
  "innvendig isolering 100 mm, 40 m² vegg",
  "taktekking 120 m², papp",
];

const empty: AnalyserResponse = { materials: [], workflow: [], crew: [], tools: [] };

type PricingParams = {
  labor_rate: number;
  material_markup: number;
  overhead_pct: number;
  profit_pct: number;
  currency: string;
};

const DEFAULT_PARAMS: PricingParams = {
  labor_rate: 750,
  material_markup: 0.15,
  overhead_pct: 0.10,
  profit_pct: 0.10,
  currency: "NOK",
};

// --- helpers: no-cache fetch + normalizatorius ---
async function fetchAnalyze(description: string): Promise<any> {
  const url = `/api/estimate/analyze?v=${Date.now()}`;
  const res = await fetch(url, {
    method: "POST",
    cache: "no-store",
    headers: {
      "content-type": "application/json",
      pragma: "no-cache",
      "cache-control": "no-cache",
    },
    body: JSON.stringify({ description, locale: "nb" }),
  });
  return res.json();
}

function normalizeAnalyze(r: any): AnalyserResponse {
  const pick = (keys: string[]) => {
    for (const k of keys) {
      const v = r?.[k];
      if (Array.isArray(v)) return v;
    }
    return [];
  };
  return {
    materials: pick(["materials", "m"]),
    workflow: pick(["workflow", "w", "tasks"]),
    crew: pick(["crew", "manpower", "team"]),
    tools: pick(["tools", "equipment", "tooling"]),
  };
}

export default function App() {
  const [desc, setDesc] = useState("");
  const [sample, setSample] = useState<string>("");
  const [data, setData] = useState<AnalyserResponse>(empty);
  const [totals, setTotals] = useState<RecalcResponse["totals"]>();
  const [loading, setLoading] = useState<"idle" | "analyze" | "recalc" | "export">("idle");
  const [error, setError] = useState<string | null>(null);

  const [params, setParams] = useState<PricingParams>(DEFAULT_PARAMS);
  function setParam<K extends keyof PricingParams>(key: K, val: PricingParams[K]) {
    setParams((p) => ({ ...p, [key]: val }));
  }

  // SAFE ARRAYS
  const mats = Array.isArray(data?.materials) ? data.materials : [];
  const wf   = Array.isArray(data?.workflow)  ? data.workflow  : [];
  const cr   = Array.isArray(data?.crew)      ? data.crew      : [];
  const tl   = Array.isArray(data?.tools)     ? data.tools     : [];

  // DEBUG
  console.log("LEN", { m: mats.length, w: wf.length, c: cr.length, t: tl.length });

  useEffect(() => {}, [mats, wf, cr, tl]);

  // --- ANALYZE ---
  async function doAnalyser() {
    try {
      setError(null);
      setLoading("analyze");

      const d =
        (desc || "").trim() ||
        SAMPLES[1] ||
        SAMPLES[0] ||
        "garasje 50 m² med plate på mark";
      if (!(desc || "").trim()) setDesc(d);

      // 1 kvietimas
      let r = await fetchAnalyze(d);
      let analyzed = normalizeAnalyze(r);

      // jei trūksta crew/tools, 1 kartą bandom dar
      if (analyzed.crew.length === 0 || analyzed.tools.length === 0) {
        const r2 = await fetchAnalyze(d);
        const a2 = normalizeAnalyze(r2);
        if (analyzed.crew.length === 0) analyzed.crew = a2.crew;
        if (analyzed.tools.length === 0) analyzed.tools = a2.tools;
      }

      setData(analyzed);
      console.log("[doAnalyser] setData:", {
        m: analyzed.materials.length,
        w: analyzed.workflow.length,
        c: analyzed.crew.length,
        t: analyzed.tools.length,
      });
      setTotals(undefined);
    } catch {
      setError("Noe gikk galt under analyse.");
    } finally {
      setLoading("idle");
    }
  }

  // --- RECALC (local only) ---
  async function doRecalc() {
    setError(null);
    setLoading("recalc");

    const toFrac = (v: any) => {
      const n = Number(v);
      if (!isFinite(n) || isNaN(n)) return 0;
      return n > 1 ? n / 100 : n;
    };

    // vietiniam skaičiavimui API nereikia
    const labor_hours     = wf.reduce((s, w) => s + Number(w?.hours || 0), 0);
    const labor_total     = labor_hours * Number(params.labor_rate || 0);

    const base_mat        = mats.reduce((s, m) => s + Number(m?.price || 0) * Number(m?.qty || 0), 0);
    const materials_total = base_mat * (1 + toFrac(params.material_markup));

    const tools_total     = 0; // jei reikės, pridėsim
    const subtotal        = labor_total + materials_total + tools_total;

    const overhead_total  = subtotal * toFrac(params.overhead_pct);
    const profit_total    = (subtotal + overhead_total) * toFrac(params.profit_pct);
    const total           = subtotal + overhead_total + profit_total;

    setTotals({
      materials: Number(materials_total.toFixed(2)),
      labor:     Number(labor_total.toFixed(2)),
      tools:     Number(tools_total.toFixed(2)),
      overhead:  Number(overhead_total.toFixed(2)),
      profit:    Number(profit_total.toFixed(2)),
      total:     Number(total.toFixed(2)),
      currency:  params.currency || "NOK",
    } as any);

    setLoading("idle");
  }

  // EDITORS
  function updateMat(i: number, patch: Partial<Material>) {
    const next = structuredClone ? structuredClone(data) : JSON.parse(JSON.stringify(data));
    if (!next.materials[i]) return;
    Object.assign(next.materials[i], patch);
    setData(next);
  }
  function updateWf(i: number, patch: Partial<WorkflowItem>) {
    const next = structuredClone ? structuredClone(data) : JSON.parse(JSON.stringify(data));
    if (!next.workflow[i]) return;
    Object.assign(next.workflow[i], patch);
    setData(next);
  }
  function updateCrew(i: number, patch: Partial<CrewMember>) {
    const next = structuredClone ? structuredClone(data) : JSON.parse(JSON.stringify(data));
    if (!next.crew[i]) return;
    Object.assign(next.crew[i], patch);
    setData(next);
  }
  function updateTool(i: number, patch: Partial<Tool>) {
    const next = structuredClone ? structuredClone(data) : JSON.parse(JSON.stringify(data));
    if (!next.tools[i]) return;
    Object.assign(next.tools[i], patch);
    setData(next);
  }

  // CO₂ demo
  const co2Data = mats.map((m) => ({ name: m.name || "?", kg: Number(m.qty ?? 0) * 1.5 }));
  const co2Total = co2Data.reduce((s, x) => s + x.kg, 0);

  async function runAnalyserWithDesc(d: string) {
    try {
      setError(null);
      setLoading("analyze");

      let description = String(d || "").trim();
      if (!description && typeof document !== "undefined") {
        const t = document.querySelector("textarea") as HTMLTextAreaElement | null;
        if (t?.value) description = String(t.value).trim();
      }
      if (!description) description = "garasje 50 m² med plate på mark";

      // 1 kvietimas
      let r = await fetchAnalyze(description);
      let a = normalizeAnalyze(r);

      // pakartojimas jei trūksta
      if (a.crew.length === 0 || a.tools.length === 0) {
        const r2 = await fetchAnalyze(description);
        const a2 = normalizeAnalyze(r2);
        if (a.crew.length === 0) a.crew = a2.crew;
        if (a.tools.length === 0) a.tools = a2.tools;
      }

      setData(a);
      console.log("[runAnalyserWithDesc] setData:", {
        m: a.materials.length, w: a.workflow.length, c: a.crew.length, t: a.tools.length,
      });
      setTotals(undefined);
      return a;
    } catch {
      setError("Noe gikk galt under analyse.");
      return empty;
    } finally {
      setLoading("idle");
    }
  }

  async function useSample() {
    if (!sample) return;
    setDesc(sample);
    await runAnalyserWithDesc(sample);
    await doRecalc();
  }

  async function onExportPdf() {
    try {
      setLoading("export");
      exportPdf(desc, data, totals);
    } finally {
      setLoading("idle");
    }
  }

  async function runDemoAll() {
    const s = SAMPLES[1] || SAMPLES[0];
    setDesc(s);
    await runAnalyserWithDesc(s);
    await doRecalc();
    await onExportPdf();
  }

  return (
    <div className="container space-y-4">
      <Nav />
      <StatusBar />
      <Hero />

      {/* Priser / påslag */}
      <section className="card">
        <h3 style={{ marginTop: 0 }}>Priser / påslag</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(120px,1fr))", gap: 8 }}>
          <label>
            <div>Timepris (NOK/h)</div>
            <input
              type="number"
              value={params.labor_rate}
              onChange={(e) => setParam("labor_rate", Number(e.target.value || 0))}
              min={0}
              step={50}
              style={{ width: "100%" }}
            />
          </label>
          <label>
            <div>Material-påslag (%)</div>
            <input
              type="number"
              value={Math.round(params.material_markup * 100)}
              onChange={(e) => setParam("material_markup", Math.max(0, Number(e.target.value || 0)) / 100)}
              min={0}
              step={1}
              style={{ width: "100%" }}
            />
          </label>
          <label>
            <div>Overhead (%)</div>
            <input
              type="number"
              value={Math.round(params.overhead_pct * 100)}
              onChange={(e) => setParam("overhead_pct", Math.max(0, Number(e.target.value || 0)) / 100)}
              min={0}
              step={1}
              style={{ width: "100%" }}
            />
          </label>
          <label>
            <div>Fortjeneste (%)</div>
            <input
              type="number"
              value={Math.round(params.profit_pct * 100)}
              onChange={(e) => setParam("profit_pct", Math.max(0, Number(e.target.value || 0)) / 100)}
              min={0}
              step={1}
              style={{ width: "100%" }}
            />
          </label>
          <label>
            <div>Valuta</div>
            <input
              value={params.currency}
              onChange={(e) => setParam("currency", e.target.value || "NOK")}
              style={{ width: "100%" }}
            />
          </label>
        </div>
      </section>

      {/* Aprašymas + veiksmai */}
      <section style={{ marginBottom: 16 }}>
        <textarea
          placeholder="Lim inn prosjektbeskrivelse her"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          rows={5}
          style={{ width: "100%" }}
        />
        <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={runDemoAll} disabled={loading !== "idle"}>Kino demo (60s)</button>
          <select value={sample} onChange={(e) => setSample(e.target.value)} style={{ padding: 6, minWidth: 260 }} disabled={loading !== "idle"}>
            <option value="">Eksempel…</option>
            {SAMPLES.map((s, i) => (<option key={i} value={s}>{s}</option>))}
          </select>
          <button className="btn btn-ghost" onClick={useSample} disabled={loading !== "idle" || !sample}>
            {loading !== "idle" ? "Laster…" : "Bruk eksempel"}
          </button>
          <button className="btn btn-ghost" onClick={doAnalyser} disabled={loading !== "idle"}>
            {loading === "analyze" ? "Laster…" : "Analyser"}
          </button>
          <button className="btn btn-primary" onClick={doRecalc} disabled={loading !== "idle" || (!mats.length && !wf.length)}>
            {loading === "recalc" ? "Laster…" : "Beregn pris"}
          </button>
          <button className="btn btn-primary" disabled={loading !== "idle" || (!mats.length && !wf.length)} onClick={onExportPdf}>
            {loading === "export" ? "Laster…" : "Eksporter PDF"}
          </button>
          {error ? <span style={{ color: "#b00020", marginLeft: 8 }}>{error}</span> : null}
        </div>
      </section>

      {/* Lentelės */}
      <section className="grid gap-4 grid-cols-1 md:grid-cols-2">
        <div>
          <h3>Materialer</h3>
          <table width="100%" border={1} cellPadding={6}>
            <thead><tr><th>Navn</th><th>Mengde</th><th>Enhet</th></tr></thead>
            <tbody>
              {mats.map((m, i) => (
                <tr key={i}>
                  <td><input value={m.name ?? ""} onChange={(e) => updateMat(i, { name: e.target.value })} /></td>
                  <td><input type="number" value={m.qty ?? 0} onChange={(e) => updateMat(i, { qty: Number(e.target.value) })} /></td>
                  <td><input value={m.unit ?? ""} onChange={(e) => updateMat(i, { unit: e.target.value })} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <h3>Arbeidsflyt</h3>
          <table width="100%" border={1} cellPadding={6}>
            <thead><tr><th>Oppgave</th><th>Timer</th></tr></thead>
            <tbody>
              {wf.map((w, i) => (
                <tr key={i}>
                  <td><input value={w.task ?? ""} onChange={(e) => updateWf(i, { task: e.target.value })} /></td>
                  <td><input type="number" value={w.hours ?? 0} onChange={(e) => updateWf(i, { hours: Number(e.target.value) })} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <h3>Mannskap</h3>
          <table width="100%" border={1} cellPadding={6}>
            <thead><tr><th>Rolle</th><th>Antall</th></tr></thead>
            <tbody>
              {cr.map((c, i) => (
                <tr key={i}>
                  <td><input value={c.role ?? ""} onChange={(e) => updateCrew(i, { role: e.target.value })} /></td>
                  <td><input type="number" value={c.count ?? 0} onChange={(e) => updateCrew(i, { count: Number(e.target.value) })} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <h3>Verktøy</h3>
          <table width="100%" border={1} cellPadding={6}>
            <thead><tr><th>Navn</th><th>Dager</th></tr></thead>
            <tbody>
              {tl.map((t, i) => (
                <tr key={i}>
                  <td><input value={t.name ?? ""} onChange={(e) => updateTool(i, { name: e.target.value })} /></td>
                  <td><input type="number" value={t.days ?? 0} onChange={(e) => updateTool(i, { days: Number(e.target.value) })} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Totals */}
      <section className="card mt-4">
        <h3>Kostnadsoversikt</h3>
        <Totals totals={totals} />
      </section>

      {/* ESG */}
      <section className="card mt-6">
        <h3>ESG / CO₂</h3>
        {co2Data.length ? (
          <>
            <p>Totalt: {co2Total.toFixed(1)} kg CO₂ (demo)</p>
            <div style={{ width: "100%", height: 240 }}>
              <ResponsiveContainer>
                <BarChart data={co2Data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" hide={co2Data.length > 6} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="kg" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : <p>Ingen data.</p>}
      </section>

      <Pricing data={{ ...data, materials: mats, workflow: wf, crew: cr, tools: tl }} onTotals={setTotals} />
      <Progress />
      <About />
    </div>
  );
}
