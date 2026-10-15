import CategoryBadge from "./CategoryBadge.jsx";
import { formatConfidence, getCategoryTone } from "../utils/categories";
import { toneColor } from "../utils/tone";

// All top predictions from /classify, each with its confidence.
export default function PredictionList({ predictions }) {
  if (!predictions?.length) return null;

  return (
    <section className="panel panel--tight">
      <div className="panel-title">All predictions</div>
      <ul className="prediction-list">
        {predictions.map((p, i) => (
          <li key={`${p.label}-${i}`} className={i === 0 ? "is-top" : ""}>
            <div className="row row--between">
              <span>{p.label}</span>
              <span className="ui-text">{formatConfidence(p.confidence)}</span>
            </div>
            <CategoryBadge category={p.category} displayName={p.category_info?.display_name} />
            <div className="meter">
              <div
                className="meter-fill"
                style={{
                  "--value": `${Math.round(p.confidence * 100)}%`,
                  "--meter-color": toneColor(getCategoryTone(p.category)),
                }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
