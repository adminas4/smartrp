(function(){
  var IMG="/assets/logo-custom.png";
  function paint(a){
    if(!a) return;
    a.style.display='inline-block';
    a.style.width='220px';
    a.style.height='52px';
    a.style.background='url("'+IMG+'") no-repeat left center / contain';
    a.style.color='transparent';
    a.style.fontSize='0';
    a.style.textIndent='-9999px';
    a.style.overflow='hidden';
    a.querySelectorAll('img,svg,span').forEach(function(n){ n.style.display='none'; });
  }
  function findAndPaint(){
    // imk pirmą nuorodą header'yje – nesvarbu, koks href/text
    var header=document.querySelector('header');
    var a=header && header.querySelector('a');
    if(a) paint(a);
  }
  // pirmas bandymas po kraunimosi
  (document.readyState==='loading' ? document.addEventListener('DOMContentLoaded', findAndPaint) : findAndPaint());
  // reaguok į SPA perpiešimus
  new MutationObserver(findAndPaint).observe(document.documentElement,{subtree:true,childList:true});
})();
