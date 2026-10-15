import { Component } from "react";
import NeonButton from "./NeonButton.jsx";

// Catches a crash inside a page so the demo never ends on a blank screen.
export default class ErrorBoundary extends Component {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error, info) {
    console.error("This screen crashed:", error, info);
  }

  render() {
    if (!this.state.failed) return this.props.children;

    return (
      <div className="page">
        <section className="panel empty-state">
          <h2>Something broke on this screen</h2>
          <p>Reload the page to carry on. Your saved scans and droplets are safe on the backend.</p>
          <NeonButton solid style={{ marginTop: 14 }} onClick={() => window.location.reload()}>
            Reload page
          </NeonButton>
        </section>
      </div>
    );
  }
}
