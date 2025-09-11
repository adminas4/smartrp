import React, { useEffect, useState } from "react";

type Item = { time: string; status: "ok" | "fail" };

export default function Progress() {
  const [items, setItems] = useState<Item[]>([]);

  async function ping() {
    try {
      const r = await fetch("/api/progress/health", { method: "GET" });
      const ok = r.status === 204;
      setItems((prev) => [
        { time: new Date().toLocaleString(), status: ok ? "ok" : "fail" },
        ...prev,
      ].slice(0, 10));
    } catch {
      setItems((prev) => [
        { time: new Date().toLocaleString(), status: "fail" },
        ...prev,
      ].slice(0, 10));
    }
  }

  useEffect(() => {
    ping();
    const id = setInterval(ping, 60000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ marginTop: 16, padding: 12, border: "1px solid #e5e7eb", borderRadius: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Status</h3>
        <button onClick={ping}>Oppdater</button>
      </div>
      {items.length === 0 ? (
        <p style={{ marginTop: 8 }}>Nėra įrašų.</p>
      ) : (
        <ul style={{ marginTop: 8 }}>
          {items.map((it, i) => (
            <li key={i}>
              {it.time} — {it.status === "ok" ? "OK" : "NEVEIKIA"}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
