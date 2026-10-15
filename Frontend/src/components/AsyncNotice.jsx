import NeonButton from "./NeonButton.jsx";

// Loading dots or an error with a retry button. Renders nothing when all is fine.
export default function AsyncNotice({ loading, error, onRetry, hasData }) {
  if (error) {
    return (
      <div className="inline-alert row row--between" role="alert">
        <span>{error}</span>
        <NeonButton color="red" size="sm" onClick={onRetry}>
          Try again
        </NeonButton>
      </div>
    );
  }
  if (loading && !hasData) {
    return (
      <p className="muted">
        <span className="loader" aria-hidden="true">
          <span />
          <span />
          <span />
        </span>{" "}
        Loading
      </p>
    );
  }
  return null;
}
