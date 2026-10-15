import { useCallback, useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

// Menus with dropdowns. Hash links (#bins ...) are scrolled to by App.jsx.
const MENUS = [
  {
    id: "twin",
    label: "Digital Twin",
    match: "/twin",
    items: [
      { to: "/twin#bins", label: "Virtual bins", hint: "fill levels" },
      { to: "/twin#history", label: "Scan history" },
      { to: "/twin#stats", label: "Statistics" },
    ],
  },
  {
    id: "tree",
    label: "Tree Game",
    match: "/tree",
    items: [
      { to: "/tree", label: "My tree", hint: "grow it" },
      { to: "/tree#history", label: "Droplet history" },
    ],
  },
];

const CLOSE_MS = 140; // must match the menu-close animation in index.css

function Caret() {
  return (
    <svg className="menu-caret" viewBox="0 0 10 10" aria-hidden="true">
      <path d="M1 3l4 4 4-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function MenuRows({ items }) {
  return items.map((item) => (
    <Link key={item.to} to={item.to} role="menuitem" className="menu-row">
      <span>{item.label}</span>
      {item.hint && <span className="menu-hint">{item.hint}</span>}
    </Link>
  ));
}

export default function Navbar() {
  const [open, setOpen] = useState(null); // "twin" | "tree" | "mobile" | null
  const [closing, setClosing] = useState(false);
  const barRef = useRef(null);
  const timer = useRef(null);
  const location = useLocation();

  const close = useCallback(() => {
    if (open === null || closing) return;
    setClosing(true);
    timer.current = setTimeout(() => {
      setOpen(null);
      setClosing(false);
    }, CLOSE_MS);
  }, [open, closing]);

  const toggle = (id) => {
    if (open === id && !closing) {
      close();
    } else {
      clearTimeout(timer.current);
      setClosing(false);
      setOpen(id);
    }
  };

  // Like the Mac menu bar: once a menu is open, hovering another one switches to it.
  const hoverSwitch = (id) => {
    if (open !== null && !closing && open !== id && open !== "mobile") {
      setOpen(id);
    }
  };

  // Close on outside click and Esc
  useEffect(() => {
    if (open === null) return undefined;
    const onPointerDown = (e) => {
      if (barRef.current && !barRef.current.contains(e.target)) close();
    };
    const onKey = (e) => {
      if (e.key === "Escape") close();
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, close]);

  // Close after navigating
  useEffect(() => {
    clearTimeout(timer.current);
    setOpen(null);
    setClosing(false);
  }, [location.pathname, location.hash]);

  useEffect(() => () => clearTimeout(timer.current), []);

  const dropdownClass = (extra = "") =>
    `menu-dropdown ${extra} ${closing ? "is-closing" : ""}`.trim();

  return (
    <header className="menubar" ref={barRef}>
      <Link to="/" className="menubar-brand">
        <span aria-hidden="true">{"\u267B\uFE0E"}</span>
        Smart Recycling
      </Link>

      {/* Desktop: full menu bar */}
      <nav className="menu-desktop" aria-label="Main">
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <NavLink
            to="/"
            end
            className={({ isActive }) => `menu-item ${isActive ? "is-active" : ""}`}
          >
            Scan
          </NavLink>

          {MENUS.map((menu) => (
            <div className="menu-wrap" key={menu.id} onMouseEnter={() => hoverSwitch(menu.id)}>
              <button
                type="button"
                className={`menu-item ${location.pathname === menu.match ? "is-active" : ""}`}
                aria-haspopup="menu"
                aria-expanded={open === menu.id && !closing}
                onClick={() => toggle(menu.id)}
              >
                {menu.label}
                <Caret />
              </button>
              {open === menu.id && (
                <div className={dropdownClass()} role="menu">
                  <MenuRows items={menu.items} />
                </div>
              )}
            </div>
          ))}
        </div>
      </nav>

      <div className="menubar-spacer" />

      {/* Phones: one menu button with everything inside */}
      <div className="menu-wrap menu-mobile">
        <button
          type="button"
          className="menu-item"
          aria-haspopup="menu"
          aria-expanded={open === "mobile" && !closing}
          onClick={() => toggle("mobile")}
        >
          Menu
          <Caret />
        </button>
        {open === "mobile" && (
          <div className={dropdownClass("menu-dropdown--right")} role="menu">
            <Link to="/" role="menuitem" className="menu-row">
              <span>Scan</span>
            </Link>
            {MENUS.map((menu) => (
              <div key={menu.id}>
                <hr className="menu-sep" />
                <div className="panel-title" style={{ padding: "4px 12px 2px", margin: 0 }}>
                  {menu.label}
                </div>
                <MenuRows items={menu.items} />
              </div>
            ))}
          </div>
        )}
      </div>
    </header>
  );
}
