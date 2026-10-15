// Always shows where an answer came from, so the demo never looks fake.
//   classify: "model" | "demo"      guidance: "gemini" | "fallback"
const SOURCES = {
  model: { tone: "green", text: "Live AI model" },
  demo: { tone: "amber", text: "Demo result" },
  gemini: { tone: "green", text: "Gemini guidance" },
  fallback: { tone: "amber", text: "Built-in fallback guidance" },
};

export default function SourceBadge({ source }) {
  const info = SOURCES[source] ?? { tone: "muted", text: source ?? "Unknown source" };
  return <span className={`badge badge--${info.tone}`}>{info.text}</span>;
}
