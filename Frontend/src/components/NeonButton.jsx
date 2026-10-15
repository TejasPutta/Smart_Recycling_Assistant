import { Link } from "react-router-dom";

/**
 * The one button used everywhere, so hover and click animations stay identical.
 *
 * <NeonButton>Scan</NeonButton>
 * <NeonButton solid>Confirm disposal</NeonButton>
 * <NeonButton color="red" size="sm">Retry</NeonButton>
 * <NeonButton to="/tree">Open tree</NeonButton>   (renders a router link)
 */
export default function NeonButton({
  color = "green", // "green" | "red" | "amber"
  solid = false,
  size, // "sm" for a smaller button
  block = false, // full width
  to,
  type = "button",
  className = "",
  children,
  ...rest
}) {
  const classes = [
    "neon-btn",
    color === "red" ? "neon-btn--danger" : "",
    color === "amber" ? "neon-btn--amber" : "",
    solid ? "neon-btn--solid" : "",
    size === "sm" ? "neon-btn--sm" : "",
    block ? "neon-btn--block" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  if (to) {
    return (
      <Link to={to} className={classes} {...rest}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} className={classes} {...rest}>
      {children}
    </button>
  );
}
