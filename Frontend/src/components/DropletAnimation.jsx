import { useEffect, useMemo, useState } from "react";
import "./DropletAnimation.css";

/**
 * Droplets fall and a "+N droplets" message pops up.
 * Trigger it by passing a new object: burst={{ id: Date.now(), amount: 5 }}
 */
export default function DropletAnimation({ burst }) {
  const [active, setActive] = useState(null);

  useEffect(() => {
    if (!burst) return undefined;
    setActive(burst);
    const timer = setTimeout(() => setActive(null), 2800);
    return () => clearTimeout(timer);
  }, [burst]);

  const drops = useMemo(() => {
    if (!active) return [];
    const count = Math.min(Math.max(active.amount * 2, 6), 16);
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      x: 12 + Math.random() * 76, // % from the left
      dx: (Math.random() - 0.5) * 90, // sideways drift in px
      delay: Math.random() * 0.7,
      size: 16 + Math.random() * 16,
    }));
  }, [active]);

  if (!active) return null;

  return (
    <div className="droplet-layer" aria-hidden="true">
      {drops.map((d) => (
        <svg
          key={`${active.id}-${d.id}`}
          className="droplet"
          viewBox="0 0 24 32"
          width={d.size}
          height={d.size * 1.33}
          style={{ left: `${d.x}%`, "--dx": `${d.dx}px`, animationDelay: `${d.delay}s` }}
        >
          <path d="M12 1C12 1 2 14 2 21a10 10 0 0 0 20 0C22 14 12 1 12 1z" />
          <ellipse cx="8.5" cy="20" rx="2" ry="3.4" className="droplet-shine" />
        </svg>
      ))}
      <div className="droplet-toast">+{active.amount} droplets</div>
    </div>
  );
}
