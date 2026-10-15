import ReactMarkdown from "react-markdown";
import NeonButton from "./NeonButton.jsx";
import SourceBadge from "./SourceBadge.jsx";

/**
 * Recycling steps from POST /guidance (markdown).
 * status: "idle" | "loading" | "ready" | "error"
 * A "fallback" source is clearly labelled, never presented as Gemini.
 */
export default function GuidancePanel({ status, data, error, onRetry }) {
  if (status === "idle") return null;

  return (
    <section className="panel panel--flow" aria-live="polite">
      <div className="row row--between">
        <h3 style={{ margin: 0 }}>How to recycle it</h3>
        {status === "ready" && <SourceBadge source={data.source} />}
      </div>

      {status === "loading" && (
        <p className="muted">
          <span className="loader" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>{" "}
          Getting recycling steps
        </p>
      )}

      {status === "error" && (
        <>
          <div className="inline-alert" role="alert">
            {error}
          </div>
          <NeonButton size="sm" onClick={onRetry}>
            Try again
          </NeonButton>
        </>
      )}

      {status === "ready" && (
        <>
          {data.source === "fallback" && (
            <p className="notice notice--info">
              Gemini wasn't used{data.note ? `: ${data.note}` : "."} These are the built-in steps.
            </p>
          )}
          <div className="markdown">
            <ReactMarkdown>{data.guidance}</ReactMarkdown>
          </div>
        </>
      )}
    </section>
  );
}
