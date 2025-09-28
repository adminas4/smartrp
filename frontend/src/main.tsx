import "./fab.css";
import "./shims/suggest-compat.js";
import "./shims/compat.js";
import "./shims/runbomall.js";
import "./index.css";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const el = document.getElementById("root")!;
createRoot(el).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(()=>{}));
}
let deferredPrompt: any = null;
window.addEventListener("beforeinstallprompt", (e: any) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.createElement("button");
  btn.textContent = "Install SmartRP";
  btn.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:9999;padding:10px 14px;border-radius:9999px;background:#0b1220;color:#fff;border:none;box-shadow:0 6px 30px rgba(0,0,0,.2);cursor:pointer";
  document.body.appendChild(btn);
  btn.addEventListener("click", async () => {
    try { await deferredPrompt.prompt?.(); } catch {}
    btn.remove(); deferredPrompt = null;
  });
});
window.addEventListener("appinstalled", () => {
  const el = document.querySelector("button[smart-rp-install]") as HTMLButtonElement | null;
  el?.remove();
});
