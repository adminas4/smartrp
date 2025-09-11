import React from "react";
export default function Hero() {
  return (
    <section className="container mt-4">
      <div className="rounded-2xl bg-white shadow-sm ring-1 ring-slate-200 p-6">
        <h1 className="text-2xl font-semibold text-slate-900">Fast estimates. Clear pricing.</h1>
        <p className="mt-1 text-slate-600">
          Paste a project description, get materials and tasks, then calculate a price with your own rates.
        </p>
        <div className="mt-3 flex gap-2">
          <a href="#" className="btn btn-primary rounded-md px-3 py-1.5">Start demo</a>
          <a href="#" className="rounded-md border border-slate-200 px-3 py-1.5 hover:bg-slate-50">View pricing</a>
        </div>
      </div>
    </section>
  );
}
