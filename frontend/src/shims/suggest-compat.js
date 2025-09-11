(() => {
  const _fetch = window.fetch;
  window.fetch = async (...args) => {
    const res = await _fetch(...args);
    try {
      const url = (args[0] && args[0].toString()) || "";
      if (url.includes("/api/pricing/suggest")) {
        const clone = res.clone();
        const ct = (clone.headers.get("content-type") || "").toLowerCase();
        if (ct.includes("application/json")) {
          const data = await clone.json();
          const b = data.breakdown || {};
          const patched = {
            ...data,
            materials_total: data.materials_total ?? b.materials ?? 0,
            labor_total:     data.labor_total     ?? b.labor     ?? 0,
            tools_total:     data.tools_total     ?? b.tools     ?? 0,
            overhead_total:  data.overhead_total  ?? b.overhead  ?? 0,
            profit_total:    data.profit_total    ?? b.profit    ?? 0,
            subtotal:        data.subtotal        ?? b.subtotal  ?? ((b.materials||0)+(b.labor||0)+(b.tools||0)),
          };
          return new Response(
            JSON.stringify(patched),
            { status: res.status, statusText: res.statusText, headers: { "Content-Type": "application/json" } }
          );
        }
      }
    } catch { /* ignore */ }
    return res;
  };
})();
