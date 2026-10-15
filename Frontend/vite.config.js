import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The backend already allows http://localhost:5173 through CORS,
// so no dev proxy is needed. API address lives in .env (VITE_API_URL).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "localhost",
  },
});
