(function(){
  function fmt(n,cur){return new Intl.NumberFormat("nb-NO",{style:"currency",currency:cur||"NOK",maximumFractionDigits:0}).format(n||0);}
  function paint(d){
    if(!d||!d.breakdown) return;
    const cur=d.currency||"NOK";
    const rows={
      "Materialer": d.breakdown.materials ?? d.materials_total ?? 0,
      "Arbeid":     d.breakdown.labor     ?? d.labor_total     ?? 0,
      "Verktøy":    d.breakdown.tools     ?? d.tools_total     ?? 0,
      "Overhead":   d.breakdown.overhead  ?? d.overhead_total  ?? 0,
      "Fortjeneste":d.breakdown.profit    ?? d.profit_total    ?? 0,
      "Total":      d.total ?? d.breakdown.total ?? d.subtotal ?? 0
    };
    const panel=[...document.querySelectorAll("section,div")].find(el=>/Kostnadsoversikt/.test(el.textContent||""));
    if(!panel) return;
    const table=panel.querySelector("table")||panel.querySelector("tbody")?.closest("table");
    if(!table) return;
    Object.entries(rows).forEach(([label,val])=>{
      const tr=[...table.querySelectorAll("tr")].find(tr=>(tr.cells[0]?.textContent||"").trim()===label);
      if(tr && tr.cells[1]) tr.cells[1].textContent=fmt(val,cur);
    });
  }
  window.__uiSum={paint};
})();
