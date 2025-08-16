import React, { useMemo, useState } from "react";

type Material = { name: string; quantity: number };
type Workflow = { task: string; hours: number };
type Pricing = {
  material_unit?: number;
  labor_hour?: number;
  overhead_pct?: number;
  profit_pct?: number;
};

type UpdateResponse = {
  currency: string;
  totals: number;
  materials_sum?: number;
  labor_sum?: number;
  overhead?: number;
  profit?: number;
  grand_total_ex_vat?: number;
  vat_pct?: number;
  vat_amount?: number;
  grand_total?: number;
  warnings?: string[] | null;
  rates_used?: Record<string, number>;
};

const asJson = (s: string) => {
  if (!s.trim()) return undefined;
  try {
    return JSON.parse(s);
  } catch {
    return undefined;
  }
};

const EstimateDemo: React.FC = () => {
  // Analyze
  const [description, setDescription] = useState("Stogas su keramikinėm čerpėm");
  // Update payload fields (kaip JSON tekstas, patogu greitai redaguoti)
  const [materialsText, setMaterialsText] = useState(
    `[{"name":"Concrete C25/30","quantity":12}]`
  );
  const [workflowText, setWorkflowText] = useState(
    `[{"task":"Pouring","hours":8}]`
  );
  const [vatPct, setVatPct] = useState<number>(0.25);
  const [pricingText, setPricingText] = useState(
    `{"material_unit":10,"labor_hour":500,"overhead_pct":0.10,"profit_pct":0.10}`
  );

  const materials = useMemo(() => asJson(materialsText) as Material[] | undefined, [materialsText]);
  const workflow = useMemo(() => asJson(workflowText) as Workflow[] | undefined, [workflowText]);
  const pricing = useMemo(() => asJson(pricingText) as Pricing | undefined, [pricingText]);

  const [resp, setResp] = useState<UpdateResponse | null>(null);
  const [analyzeData, setAnalyzeData] = useState<{ materials: Material[]; workflow: Workflow[] } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleAnalyze = async () => {
    setErr(null);
    setBusy(true);
    try {
      const r = await fetch("/api/v1/estimate/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, currency: "NOK" }),
      });
      if (!r.ok) throw new Error(`Analyze failed: ${r.status}`);
      const data = await r.json();
      // Užpildom formas iš gauto stub’o
      setMaterialsText(JSON.stringify(data.materials, null, 2));
      setWorkflowText(JSON.stringify(data.workflow, null, 2));
      setAnalyzeData({ materials: data.materials, workflow: data.workflow });
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleUpdate = async () => {
    setErr(null);
    setBusy(true);
    try {
      const payload: any = {
        materials: materials ?? [],
        workflow: workflow ?? [],
        vat_pct: vatPct,
      };
      if (pricing && Object.keys(pricing).length > 0) {
        payload.pricing = pricing;
      }
      const r = await fetch("/api/v1/estimate/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`Update failed: ${r.status}`);
      const data: UpdateResponse = await r.json();
      setResp(data);
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>SmartRP — Estimate Demo</h1>

      <section style={{ marginBottom: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
        <h2>1) Analyze (POST /api/v1/estimate/analyze)</h2>
        <label>
          Description:
          <input
            style={{ width: "100%", padding: 8, marginTop: 8 }}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <button disabled={busy} onClick={handleAnalyze} style={{ marginTop: 12 }}>
          {busy ? "Analyzing..." : "Analyze"}
        </button>
        {analyzeData && (
          <div style={{ marginTop: 12, color: "#333" }}>
            <div><strong>Analyzed materials:</strong> {analyzeData.materials.length}</div>
            <div><strong>Analyzed workflow:</strong> {analyzeData.workflow.length}</div>
          </div>
        )}
      </section>

      <section style={{ marginBottom: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
        <h2>2) Update (POST /api/v1/estimate/update)</h2>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <label>materials (JSON array)</label>
            <textarea
              rows={8}
              style={{ width: "100%", marginTop: 6 }}
              value={materialsText}
              onChange={(e) => setMaterialsText(e.target.value)}
            />
            {!materials && <div style={{ color: "crimson" }}>Invalid JSON</div>}
          </div>

          <div>
            <label>workflow (JSON array)</label>
            <textarea
              rows={8}
              style={{ width: "100%", marginTop: 6 }}
              value={workflowText}
              onChange={(e) => setWorkflowText(e.target.value)}
            />
            {!workflow && <div style={{ color: "crimson" }}>Invalid JSON</div>}
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
          <div>
            <label>vat_pct</label>
            <input
              type="number"
              min={0}
              max={1}
              step={0.01}
              value={vatPct}
              onChange={(e) => setVatPct(parseFloat(e.target.value))}
              style={{ width: "100%", marginTop: 6, padding: 8 }}
            />
          </div>
          <div>
            <label>pricing (JSON object)</label>
            <textarea
              rows={6}
              style={{ width: "100%", marginTop: 6 }}
              value={pricingText}
              onChange={(e) => setPricingText(e.target.value)}
            />
            {!pricing && <div style={{ color: "crimson" }}>Invalid JSON</div>}
          </div>
        </div>

        <button disabled={busy || !materials || !workflow} onClick={handleUpdate} style={{ marginTop: 12 }}>
          {busy ? "Calculating..." : "Update"}
        </button>
      </section>

      {err && (
        <div style={{ color: "crimson", marginBottom: 16 }}>
          <strong>Error:</strong> {err}
        </div>
      )}

      {resp && (
        <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
          <h2>Result</h2>
          <div>currency: <strong>{resp.currency}</strong></div>
          <div>materials_sum: <strong>{resp.materials_sum ?? 0}</strong></div>
          <div>labor_sum: <strong>{resp.labor_sum ?? 0}</strong></div>
          <div>overhead: <strong>{resp.overhead ?? 0}</strong></div>
          <div>profit: <strong>{resp.profit ?? 0}</strong></div>
          <div>grand_total_ex_vat: <strong>{resp.grand_total_ex_vat ?? 0}</strong></div>
          <div>vat_pct: <strong>{resp.vat_pct ?? 0}</strong></div>
          <div>vat_amount: <strong>{resp.vat_amount ?? 0}</strong></div>
          <div>grand_total: <strong>{resp.grand_total ?? 0}</strong></div>

          {resp.warnings?.length ? (
            <div style={{ marginTop: 12 }}>
              <strong>Warnings:</strong>
              <ul>
                {resp.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {resp.rates_used && (
            <div style={{ marginTop: 12 }}>
              <strong>Rates used:</strong>
              <pre style={{ background: "#f6f6f6", padding: 12 }}>
                {JSON.stringify(resp.rates_used, null, 2)}
              </pre>
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default EstimateDemo;
