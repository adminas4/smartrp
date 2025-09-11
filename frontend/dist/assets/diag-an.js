(function(){
  const _f=window.fetch.bind(window);
  window.fetch=async (input,init)=>{
    const url= typeof input==='string' ? input : (input && input.url);
    const bodyTxt = init && typeof init.body==='string' ? init.body : null;
    if(url && /\/api\/pricing\/suggest$/.test(url) && bodyTxt){
      try{ window.__lastPricingReq = JSON.parse(bodyTxt); console.log('[diag] pricing req:', window.__lastPricingReq); }catch(_){}
    }
    const resp= await _f(input,init);
    try{
      if(url && /\/api\/estimate\/analyze$/.test(url)){
        const data=await resp.clone().json();
        window.__lastAnalyze=data;
        console.log('[diag] analyze resp:', {m:(data.materials||[]).length,w:(data.workflow||[]).length,c:(data.crew||[]).length,t:(data.tools||[]).length, sample:data});
      }
      if(url && /\/api\/pricing\/suggest$/.test(url)){
        const data=await resp.clone().json();
        window.__lastPricing=data;
        console.log('[diag] pricing resp:', data);
      }
    }catch(_){}
    return resp;
  };
})();
