import React, { useEffect, useState } from "react";

type ProgressItem = {
  id: string;
  project_id: string;
  percent: number;
  note?: string;
  photo_url?: string;
  task_id?: string;
  timestamp: string;
};

export default function ProgressModule() {
  const [projectId, setProjectId] = useState("proj-123");
  const [percent, setPercent] = useState(10);
  const [note, setNote] = useState("");
  const [items, setItems] = useState<ProgressItem[]>([]);

  const list = async () => {
    const r = await fetch(`/api/_disabled?project_id=${encodeURIComponent(projectId)}`);
    const j = await r.json();
    setItems(j.items || []);
  };

  const create = async () => {
    const r = await fetch("/api/_disabled", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, percent, note }),
    });
    if (r.ok) {
      setNote("");
      list();
    }
  };

  useEffect(() => { list(); }, [projectId]);

  return (
    <div style={{ padding: 16 }}>
      <h2>Progreso sekimas</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <input value={projectId} onChange={e => setProjectId(e.target.value)} placeholder="project_id" />
        <input type="number" value={percent} onChange={e => setPercent(Number(e.target.value))} step={0.5} min={0} max={100} />
        <input value={note} onChange={e => setNote(e.target.value)} placeholder="note" />
        <button onClick={create}>Add</button>
        <button onClick={list}>Refresh</button>
      </div>
      <table border={1} cellPadding={6}>
        <thead>
          <tr><th>Time</th><th>%</th><th>Note</th></tr>
        </thead>
        <tbody>
          {items.map(i => (
            <tr key={i.id}>
              <td>{new Date(i.timestamp).toLocaleString()}</td>
              <td>{i.percent}</td>
              <td>{i.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
