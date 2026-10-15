import "./TreeGame.css";

// Six growth stages, drawn with plain SVG (no image files needed).
// Canopy blobs are [dx, dy, radius] relative to the top of the trunk.
const STAGES = [
  { trunk: 26, w: 2.5, blobs: [[-13, 4, 9], [13, -2, 9]], fruit: [] },
  { trunk: 70, w: 5, blobs: [[0, -8, 22], [-20, 8, 16], [20, 8, 16]], fruit: [] },
  { trunk: 100, w: 7, blobs: [[0, -18, 34], [-32, 6, 26], [32, 6, 26], [0, 12, 24]], fruit: [] },
  {
    trunk: 125,
    w: 9,
    blobs: [[0, -26, 42], [-40, 0, 32], [40, 0, 32], [-22, 22, 26], [22, 22, 26]],
    fruit: [],
  },
  {
    trunk: 145,
    w: 11,
    blobs: [[0, -34, 48], [-48, -4, 36], [48, -4, 36], [-30, 26, 30], [30, 26, 30], [0, 6, 34]],
    fruit: [[-30, -20], [34, 0]],
    branches: true,
  },
  {
    trunk: 160,
    w: 12,
    blobs: [
      [0, -40, 52], [-54, -8, 40], [54, -8, 40], [-34, 28, 34],
      [34, 28, 34], [0, 8, 38], [-62, 24, 24], [62, 24, 24],
    ],
    fruit: [[-30, -34], [22, -52], [50, -2], [-52, 14], [4, 30]],
    branches: true,
  },
];

export const STAGE_NAMES = ["Seed sprout", "Sapling", "Young tree", "Growing tree", "Mature tree", "Ancient tree"];

const CX = 150;
const BASE_Y = 300;

export default function TreeGame({ level = 0, progressPct = 0 }) {
  const stage = Math.max(0, Math.min(level, STAGES.length - 1));
  const s = STAGES[stage];
  const topY = BASE_Y - s.trunk;

  // Within a level the tree keeps growing a little with the progress bar.
  const progress = Math.max(0, Math.min(100, progressPct));
  const scale = 0.92 + 0.08 * (progress / 100);

  return (
    <figure className="tree-figure">
      <svg
        className="tree-svg"
        viewBox="0 0 300 340"
        role="img"
        aria-label={`${STAGE_NAMES[stage]}, level ${level}`}
      >
        <ellipse cx={CX} cy="306" rx="112" ry="14" className="tree-ground-glow" />
        <path d="M44 304 Q150 292 256 304" className="tree-ground" />

        <g className="tree-grow" key={stage}>
          <g className="tree-sway">
            <g transform={`translate(${CX} ${BASE_Y}) scale(${scale}) translate(${-CX} ${-BASE_Y})`}>
              <path
                className="tree-trunk"
                d={`M${CX - s.w} ${BASE_Y} L${CX - s.w * 0.6} ${topY} L${CX + s.w * 0.6} ${topY} L${CX + s.w} ${BASE_Y} Z`}
              />

              {s.branches && (
                <>
                  <path className="tree-branch" d={`M${CX} ${BASE_Y - s.trunk * 0.45} L${CX - 30} ${BASE_Y - s.trunk * 0.72}`} />
                  <path className="tree-branch" d={`M${CX} ${BASE_Y - s.trunk * 0.55} L${CX + 30} ${BASE_Y - s.trunk * 0.8}`} />
                </>
              )}

              {/* outline pass, then a fill pass that hides the lines inside the canopy */}
              <g className="tree-canopy-outline">
                {s.blobs.map(([dx, dy, r], i) => (
                  <circle key={i} cx={CX + dx} cy={topY + dy} r={r} />
                ))}
              </g>
              <g className="tree-canopy-fill">
                {s.blobs.map(([dx, dy, r], i) => (
                  <circle key={i} cx={CX + dx} cy={topY + dy} r={r - 1} />
                ))}
              </g>

              {s.fruit.map(([dx, dy], i) => (
                <circle
                  key={i}
                  className="tree-fruit"
                  cx={CX + dx}
                  cy={topY + dy}
                  r="5"
                  style={{ animationDelay: `${i * 0.4}s` }}
                />
              ))}
            </g>
          </g>
        </g>
      </svg>
      <figcaption className="tree-caption">{STAGE_NAMES[stage]}</figcaption>
    </figure>
  );
}
