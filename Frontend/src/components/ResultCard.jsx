import CategoryBadge from "./CategoryBadge.jsx";
import NeonButton from "./NeonButton.jsx";
import SourceBadge from "./SourceBadge.jsx";
import {
  CONFIDENCE_LOCK_THRESHOLD,
  formatConfidence,
  getCategoryTone,
  getRecyclability,
  isHazardous,
} from "../utils/categories";
import { toneColor } from "../utils/tone";

/**
 * Top prediction + the confirm-disposal flow.
 * Saving only happens when the user presses "Confirm disposal".
 */
export default function ResultCard({
  result,
  top,
  canConfirm,
  saving,
  saved,
  award,
  saveError,
  onConfirm,
  onRetryAward,
  onReset,
}) {
  const info = top.category_info;
  const tone = getCategoryTone(top.category);
  const recyclability = getRecyclability(info?.recyclability);
  const isDemo = result.source === "demo";
  const lowConfidence = !isDemo && top.confidence < CONFIDENCE_LOCK_THRESHOLD;

  return (
    <section className="panel panel--flow">
      <div className="row row--between">
        <SourceBadge source={result.source} />
        {result.model_name && <span className="ui-text muted">{result.model_name}</span>}
      </div>

      <h2 className="result-title">{isDemo ? "No prediction" : top.label}</h2>

      <div className="row">
        <CategoryBadge category={top.category} displayName={info?.display_name} />
        <span className={`badge badge--${recyclability.tone}`}>{recyclability.label}</span>
      </div>

      <div>
        <div className="row row--between ui-text">
          <span className="muted">Confidence</span>
          <span>{formatConfidence(top.confidence)}</span>
        </div>
        <div className="meter" style={{ marginTop: 6 }}>
          <div
            className="meter-fill"
            style={{
              "--value": `${Math.round(top.confidence * 100)}%`,
              "--meter-color": toneColor(tone),
            }}
          />
        </div>
      </div>

      {isDemo && (
        <p className="notice notice--info">
          The AI model isn't running, so this is a placeholder, not a real prediction.
          {result.note ? ` ${result.note}` : ""}
        </p>
      )}

      {lowConfidence && (
        <p className="notice notice--info">
          Not confident enough to lock on. Move closer, add light, or turn the item and scan again.
        </p>
      )}

      {!isDemo && !lowConfidence && isHazardous(top.category) && (
        <p className="notice notice--warn">
          Hazardous item. Keep it out of household bins and take it to a proper drop-off point.
        </p>
      )}

      {!isDemo && !lowConfidence && info?.short_advice && <p className="prose">{info.short_advice}</p>}

      {saveError && (
        <div className="inline-alert" role="alert">
          {saveError}
        </div>
      )}

      {saved ? (
        <div className="confirm-ok" role="status">
          <h3>Disposal confirmed</h3>
          {award?.awarded && (
            <p>
              +{award.amount} droplets earned. Balance: {award.balance.droplets}. Tree level{" "}
              {award.balance.tree_level}.
            </p>
          )}
          {award && !award.awarded && (
            <p>{award.note || "Droplets were already awarded for this scan."}</p>
          )}
          {!award && (
            <NeonButton size="sm" onClick={onRetryAward}>
              Award droplets
            </NeonButton>
          )}
          <div className="row">
            <NeonButton solid onClick={onReset}>
              Scan another item
            </NeonButton>
            <NeonButton to="/tree">View my tree</NeonButton>
          </div>
        </div>
      ) : (
        <div className="stack" style={{ gap: 8 }}>
          <NeonButton solid block onClick={onConfirm} disabled={!canConfirm || saving}>
            {saving ? "Saving" : "Confirm disposal"}
          </NeonButton>
          <p className="ui-text muted" style={{ margin: 0 }}>
            {canConfirm
              ? "Saves this scan to your history and earns droplets for your tree."
              : isDemo
                ? "Demo results can't be saved."
                : "Confidence is too low to save. Scan again."}
          </p>
        </div>
      )}
    </section>
  );
}
