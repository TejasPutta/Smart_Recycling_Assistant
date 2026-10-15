import NeonButton from "./NeonButton.jsx";

// Previous / Next for paginated lists (limit + offset, as the backend uses).
export default function Pagination({ total, limit, offset, onChange }) {
  if (!total || total <= limit) return null;
  const from = offset + 1;
  const to = Math.min(offset + limit, total);

  return (
    <div className="row row--between" style={{ marginTop: 14 }}>
      <span className="ui-text muted">
        Showing {from} to {to} of {total}
      </span>
      <div className="row">
        <NeonButton size="sm" disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>
          Previous
        </NeonButton>
        <NeonButton size="sm" disabled={to >= total} onClick={() => onChange(offset + limit)}>
          Next
        </NeonButton>
      </div>
    </div>
  );
}
