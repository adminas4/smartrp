import type { AnalyserResponse } from "../types";

type Props = {
  data: AnalyserResponse;
  onTotals?: (v: any) => void; // palikta suderinamumui su App, nenaudojama čia
};

export default function Pricing({ data }: Props) {
  const counts = {
    materials: data.materials.length,
    workflow: data.workflow.length,
    crew: data.crew.length,
    tools: data.tools.length,
  };

  return (
    <section style={{ marginTop: 24, padding: 12, border: "1px solid #e5e7eb", borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>Prisgrunnlag</h3>
      <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.8 }}>
        <li>Materialer: <b>{counts.materials}</b></li>
        <li>Arbeidsoppgaver: <b>{counts.workflow}</b></li>
        <li>Mannskap: <b>{counts.crew}</b></li>
        <li>Verktøy: <b>{counts.tools}</b></li>
      </ul>
      <p style={{ color: "#6b7280", marginTop: 8 }}>
        Bruk knappen «Beregn pris» øverst for å få summer med valgte satser.
      </p>
    </section>
  );
}
