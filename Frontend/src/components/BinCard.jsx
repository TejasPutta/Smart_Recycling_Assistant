import CategoryBadge from "./CategoryBadge.jsx";
import { getCategoryMeta } from "../utils/categories";
import { toneColor } from "../utils/tone";
import "./BinCard.css";

const STATUS = {
  empty: { tone: "muted", text: "Empty" },
  normal: { tone: "green", text: "Normal" },
  filling: { tone: "amber", text: "Filling" },
  full: { tone: "red", text: "Full" },
};

// One virtual bin. The fill colour follows the bin's status (empty, normal, filling, full).
export default function BinCard({ bin }) {
  const meta = getCategoryMeta(bin.category);
  const status = STATUS[bin.status] ?? { tone: "muted", text: bin.status };
  const pct = Math.max(0, Math.min(100, bin.fill_percentage));
  const items = bin.estimated_items;

  return (
    <article className="bin-card">
      <div className="bin-visual" role="img" aria-label={`${meta.label} bin, ${Math.round(pct)} percent full`}>
        <div className="bin-lid" />
        <div className="bin-body">
          <div className="bin-fill" style={{ "--fill": `${pct}%`, "--bin-color": toneColor(status.tone) }} />
          <span className="bin-icon" aria-hidden="true">
            {meta.icon}
          </span>
        </div>
      </div>

      <div className="bin-info">
        <CategoryBadge category={bin.category} />
        <div className="bin-pct">{Math.round(pct)}%</div>
        <div className="ui-text muted">
          {items} {items === 1 ? "item" : "items"}
        </div>
        <span className={`badge badge--${status.tone}`}>{status.text}</span>
      </div>
    </article>
  );
}
