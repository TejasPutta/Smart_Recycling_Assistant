import { useCallback, useEffect, useState } from "react";
import { getClassifierStatus } from "../api/client";
import NeonButton from "./NeonButton";

const POLL_MS = 30000;

/**
 * Shows a banner only when something is wrong:
 *  - the backend cannot be reached (red, with a Retry button)
 *  - the AI model is not loaded, so scans are demo-only (amber)
 * Nothing is shown while everything is healthy.
 */
export default function StatusBanner() {
  const [status, setStatus] = useState({ kind: "checking" });

  const check = useCallback(async () => {
    try {
      const result = await getClassifierStatus();
      setStatus({ kind: result.model_available ? "ok" : "offline" });
    } catch (err) {
      setStatus({ kind: "unreachable", message: err.message });
    }
  }, []);

  useEffect(() => {
    check();
    const id = setInterval(check, POLL_MS);
    return () => clearInterval(id);
  }, [check]);

  if (status.kind === "ok" || status.kind === "checking") return null;

  if (status.kind === "offline") {
    return (
      <div className="status-banner" role="status">
        <span>AI model offline. Demo mode: scans return a placeholder and can't be saved.</span>
      </div>
    );
  }

  return (
    <div className="status-banner status-banner--error" role="alert">
      <span>{status.message}</span>
      <NeonButton color="red" size="sm" onClick={check}>
        Retry
      </NeonButton>
    </div>
  );
}
