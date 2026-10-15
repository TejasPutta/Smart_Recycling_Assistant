import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";
import NeonButton from "./components/NeonButton.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import ScanPage from "./pages/ScanPage.jsx";
import DigitalTwinPage from "./pages/DigitalTwinPage.jsx";
import TreeGamePage from "./pages/TreeGamePage.jsx";

// Menu links like /twin#history scroll to the element with that id.
function ScrollToHash() {
  const { pathname, hash } = useLocation();

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
  return (
    <>
      <Navbar />
      <div className="app-shell">
        <StatusBanner />
        <ScrollToHash />
        <main>
          <Routes>
            <Route path="/" element={<ScanPage />} />
            <Route path="/twin" element={<DigitalTwinPage />} />
            <Route path="/tree" element={<TreeGamePage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </>
  );
}
