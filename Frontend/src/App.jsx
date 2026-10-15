import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary.jsx";
import Navbar from "./components/Navbar.jsx";
import NeonButton from "./components/NeonButton.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import ScanPage from "./pages/ScanPage.jsx";
import DigitalTwinPage from "./pages/DigitalTwinPage.jsx";
import TreeGamePage from "./pages/TreeGamePage.jsx";

const TITLES = { "/": "Scan", "/twin": "Digital Twin", "/tree": "Tree Game" };

// Sets the browser tab title and handles scrolling:
// menu links like /twin#history scroll to the element with that id.
function PageEffects() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    const title = TITLES[pathname];
    document.title = title ? `${title} | Smart Recycling` : "Smart Recycling Assistant";
  }, [pathname]);

  useEffect(() => {
    if (!hash) {
      window.scrollTo(0, 0);
      return undefined;
    }
    const timer = setTimeout(() => {
      document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
    return () => clearTimeout(timer);
  }, [pathname, hash]);

  return null;
}

function NotFound() {
  return (
    <div className="page">
      <div className="page-head">
        <h1>Page not found</h1>
        <p>That address doesn't exist in this app.</p>
      </div>
      <NeonButton to="/" solid>
        Back to the scanner
      </NeonButton>
    </div>
  );
}

export default function App() {
  const { pathname } = useLocation();

  return (
    <>
      <Navbar />
      <div className="app-shell">
        <StatusBanner />
        <PageEffects />
        {/* keyed by path, so moving to another page clears a crashed screen */}
        <ErrorBoundary key={pathname}>
          <main>
            <Routes>
              <Route path="/" element={<ScanPage />} />
              <Route path="/twin" element={<DigitalTwinPage />} />
              <Route path="/tree" element={<TreeGamePage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </ErrorBoundary>
      </div>
    </>
  );
}
