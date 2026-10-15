// Everything the UI needs to decide colours, icons and what is allowed,
// based on the categories and fields defined by the backend schemas.
//
// Backend categories: plastic, paper, fabric, battery, chemical,
// hazardous, biodegradable, other.

// Frame turns RED for these categories.
export const HAZARD_CATEGORIES = new Set(["battery", "chemical", "hazardous"]);

// The camera frame only "locks on" when the top prediction is at least this
// confident. The backend uses a general ImageNet model, so low scores are
// common. Tune this one number if scans feel too strict or too loose.
export const CONFIDENCE_LOCK_THRESHOLD = 0.35;

export const CATEGORY_META = {
  plastic: { label: "Plastic", icon: "🧴" },
  paper: { label: "Paper", icon: "📄" },
  fabric: { label: "Fabric / textile", icon: "👕" },
  battery: { label: "Battery", icon: "🔋" },
  chemical: { label: "Chemical", icon: "⚗️" },
  hazardous: { label: "Hazardous waste", icon: "☣️" },
  biodegradable: { label: "Biodegradable", icon: "🍃" },
  other: { label: "Other / unknown", icon: "❔" },
};

export function getCategoryMeta(category) {
  return CATEGORY_META[category] ?? { label: category ?? "Unknown", icon: "❔" };
}

export function isHazardous(category) {
  return HAZARD_CATEGORIES.has(category);
}

// "red" | "green" | "amber" — matches the .badge--* and .tracking-frame--* classes.
export function getCategoryTone(category) {
  if (isHazardous(category)) return "red";
  if (category === "other" || !category) return "amber";
  return "green";
}

/**
 * Decide the state of the camera tracking frame.
 *   "scanning" -> searching, no lock (also used for offline demo results)
 *   "green"    -> eco-friendly / recyclable category
 *   "red"      -> hazardous category
 *   "amber"    -> locked on, but category is unknown
 */
export function getFrameState(topPrediction, source) {
  if (!topPrediction || source === "demo") return "scanning";
  if (topPrediction.confidence < CONFIDENCE_LOCK_THRESHOLD) return "scanning";
  return getCategoryTone(topPrediction.category);
}

// Only real, confident model results may be saved or rewarded.
// Demo results (model not loaded) must never earn droplets.
export function canConfirmScan(source, topPrediction) {
  return (
    source === "model" &&
    !!topPrediction &&
    topPrediction.confidence >= CONFIDENCE_LOCK_THRESHOLD
  );
}

const RECYCLABILITY = {
  recyclable: { label: "Recyclable", tone: "green" },
  conditional: { label: "Recyclable with care", tone: "amber" },
  not_recyclable: { label: "Not recyclable", tone: "red" },
  unknown: { label: "Unknown", tone: "muted" },
};

export function getRecyclability(value) {
  return RECYCLABILITY[value] ?? RECYCLABILITY.unknown;
}

export function formatConfidence(value) {
  if (typeof value !== "number") return "–";
  return `${Math.round(value * 100)}%`;
}

export function formatDate(iso) {
  if (!iso) return "–";
  return new Date(iso).toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
