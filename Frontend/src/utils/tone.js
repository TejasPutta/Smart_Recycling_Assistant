// Maps a tone name ("green" | "red" | "amber" | "muted") to a CSS colour variable.
export const TONE_COLOR = {
  green: "var(--green)",
  red: "var(--red)",
  amber: "var(--amber)",
  muted: "var(--muted)",
};

export const toneColor = (tone) => TONE_COLOR[tone] ?? TONE_COLOR.muted;
