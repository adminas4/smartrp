import React from "react";
export default function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto max-w-5xl px-4 py-3 flex items-center gap-3">
        <img src="/logo.png" alt="SmartRP" className="h-7 w-auto" />
        <div className="font-semibold text-slate-900">SmartRP</div>
        <span className="ml-2 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">demo</span>
        <span className="ml-auto inline-flex items-center gap-2 text-xs text-slate-500">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-500" aria-label="API pålogget"></span>
        </span>
      </div>
    </header>
  );
}
