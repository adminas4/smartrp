(function(){
  function inject(){
    var h=document.querySelector('header'); if(!h) return;
    if(!document.getElementById('logo-overlay')){
      var a=document.createElement('a'); a.id='logo-overlay'; a.href='/'; h.prepend(a);
    }
  }
  (document.readyState==='loading'?document.addEventListener('DOMContentLoaded',inject):inject());
  new MutationObserver(inject).observe(document.documentElement,{subtree:true,childList:true});
})();
