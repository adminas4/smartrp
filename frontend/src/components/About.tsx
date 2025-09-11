import React from "react";
export default function About() {
  return (
    <section className="card mt-6">
      <h3>Om</h3>
      <p>
        Denne demoen viser enkel analyse av beskrivelse, prisberegning og PDF-eksport.
        API-ruter: <code>/api/estimate/analyze</code>, <code>/api/pricing/suggest</code>, <code>/api/agent/ask</code>.
      </p>
    </section>
  );
}
