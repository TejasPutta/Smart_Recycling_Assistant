// Level, droplet balance and progress to the next level (values come from the backend).
export default function TreeProgress({ level, progressPct, droplets }) {
  const pct = Math.max(0, Math.min(100, Math.round(progressPct)));

  return (
    <div className="stack" style={{ gap: 10 }}>
      <div className="row row--between">
        <h3 style={{ margin: 0 }}>Level {level}</h3>
        <span className="ui-text">{droplets} droplets</span>
      </div>
      <div
        className="meter"
        role="progressbar"
        aria-label="Progress to the next level"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
      >
        <div className="meter-fill" style={{ "--value": `${pct}%`, "--meter-color": "var(--green)" }} />
      </div>
      <p className="ui-text muted" style={{ margin: 0 }}>
        {pct}% of the way to level {level + 1}
      </p>
    </div>
  );
}
