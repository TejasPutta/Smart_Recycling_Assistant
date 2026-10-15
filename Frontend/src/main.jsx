import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

// Fonts are bundled with the app (works without internet at the venue).
// VT323 = headings + main text, Orbitron = buttons, labels, numbers, small text.
import "@fontsource/vt323";
import "@fontsource/orbitron/400.css";
import "@fontsource/orbitron/700.css";

import "./index.css";
import App from "./App.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
