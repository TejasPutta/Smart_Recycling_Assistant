import { getCategoryMeta, getCategoryTone } from "../utils/categories";

export default function CategoryBadge({ category, displayName }) {
  const meta = getCategoryMeta(category);
  const tone = getCategoryTone(category);
  return (
    <span className={`badge badge--${tone}`}>
      <span aria-hidden="true">{meta.icon}</span>
      {displayName || meta.label}
    </span>
  );
}
