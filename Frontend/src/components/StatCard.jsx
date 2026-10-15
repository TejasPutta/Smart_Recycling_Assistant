import "./StatCard.css";

export default function StatCard({ label, value, sub, compact = false }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${compact ? "stat-value--compact" : ""}`}>{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}
