// frontend/src/components/Totals.tsx
type TotalsT = {
  materials: number;
  labor: number;
  tools: number;
  overhead: number;
  profit: number;
  total: number;
  currency?: string;
};

export default function Totals({ totals }: { totals?: TotalsT }) {
  if (!totals) return <p>Ingen data.</p>;
  const cur = totals.currency || "NOK";
  const fmt = (v: number) =>
    new Intl.NumberFormat("nb-NO", { style: "currency", currency: cur }).format(v);

  return (
    <div className="overflow-x-auto">
      <table>
        <tbody>
          <tr><th>Materialer</th><td>{fmt(totals.materials)}</td></tr>
          <tr><th>Arbeid</th><td>{fmt(totals.labor)}</td></tr>
          <tr><th>Verktøy</th><td>{fmt(totals.tools)}</td></tr>
          <tr><th>Overhead</th><td>{fmt(totals.overhead)}</td></tr>
          <tr><th>Fortjeneste</th><td>{fmt(totals.profit)}</td></tr>
          <tr><th>Total</th><td><strong>{fmt(totals.total)}</strong></td></tr>
        </tbody>
      </table>
    </div>
  );
}
