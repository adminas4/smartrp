(()=>{ 
  function fix(){
    document.querySelectorAll("table").forEach(t=>{
      t.style.tableLayout="fixed";
      t.style.width="100%";
    });
    document.querySelectorAll("td,th").forEach(c=>{
      c.style.minWidth="0";
      c.style.overflow="hidden";
    });
    document.querySelectorAll("td input,td select,td textarea").forEach(el=>{
      el.style.width="100%";
      el.style.maxWidth="100%";
      el.style.minWidth="0";
      el.style.boxSizing="border-box";
      el.style.overflow="hidden";
    });
  }
  window.__fixCells = fix;         // kad galėtum įvykdyti per konsolę
  fix();
  new MutationObserver(fix).observe(document.body,{subtree:true,childList:true});
})();
