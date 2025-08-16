import React from "react";
import { createRoot } from "react-dom/client";
import EstimateDemo from "./modules/estimate/EstimateDemo";

const el = document.getElementById("root")!;
createRoot(el).render(
  <React.StrictMode>
    <EstimateDemo />
  </React.StrictMode>
);
