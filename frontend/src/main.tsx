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
