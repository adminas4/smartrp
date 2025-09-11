(function(){
  const fmt=(n,cur="NOK")=>new Intl.NumberFormat("nb-NO",{style:"currency",currency:cur,maximumFractionDigits:0}).format(n||0);

  function ensureTable(panel){
    let table=panel.querySelector("table");
    if(!table){
      table=document.createElement("table");
      const tbody=document.createElement("tbody");
      ["Materialer","Arbeid","Verktøy","Overhead","Fortjeneste","Total"].forEach(lbl=>{
        const tr=document.createElement("tr");
        const th=document.createElement("th"); th.textContent=lbl;
        const td=document.createElement("td"); td.textContent="0 kr";
        tr.appendChild(th); tr.appendChild(td); tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      panel.appendChild(table);
    }
    return table;
  }

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
    const table=ensureTable(panel);
    Object.entries(rows).forEach(([label,val])=>{
      const tr=[...table.querySelectorAll("tr")].find(tr=>(tr.cells[0]?.textContent||"").trim()===label);
      if(tr && tr.cells[1]) tr.cells[1].textContent=fmt(val,cur);
    });
  }

  const _fetch=window.fetch.bind(window);
  window.fetch=async (input,init)=>{
    const url=typeof input==="string"?input:(input&&input.url);
    const resp=await _fetch(input,init);
    if(url && /\/api\/pricing\/suggest$/.test(url)){
      try{ paint(await resp.clone().json()); }catch(_){}
    }
    return resp;
  };
})();
