type Json = Record<string, any>;

async function post<T = any>(url: string, body: Json): Promise<T> {
  const res = await fetch(`${url}?v=${Date.now()}`, {
    method: "POST",
    cache: "no-store",
    headers: {
      "content-type": "application/json",
      "pragma": "no-cache",
      "cache-control": "no-cache",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  analyze: (p: { description: string; locale?: string }) =>
    post("/api/estimate/analyze", {
      description: p.description,
      locale: p.locale || "nb",
    }),
  suggest: (payload: Json) => post("/api/estimate/recalculate", payload),
};
