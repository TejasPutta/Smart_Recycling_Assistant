import { useState } from "react";

import AsyncNotice from "../components/AsyncNotice.jsx";
import BinCard from "../components/BinCard.jsx";
import CategoryBadge from "../components/CategoryBadge.jsx";
import NeonButton from "../components/NeonButton.jsx";
import Pagination from "../components/Pagination.jsx";
import PredictionList from "../components/PredictionList.jsx";
import SourceBadge from "../components/SourceBadge.jsx";
import StatCard from "../components/StatCard.jsx";
import { getBins, getHistory, getScanDetail, getStatistics } from "../api/client";
import {
  CATEGORY_META,
  formatConfidence,
  formatDate,
  getCategoryMeta,
  getCategoryTone,
} from "../utils/categories";
import { toneColor } from "../utils/tone";
import { useAsync } from "../utils/useAsync";
import "./DigitalTwinPage.css";

const PAGE_SIZE = 10;

export default function DigitalTwinPage() {
  const bins = useAsync(getBins, []);
  const stats = useAsync(getStatistics, []);

  const [category, setCategory] = useState("");
  const [offset, setOffset] = useState(0);
  const history = useAsync(() => getHistory({ limit: PAGE_SIZE, offset, category }), [category, offset]);

  // Expanded history rows load the full scan (GET /history/{id}) on demand.
  const [openId, setOpenId] = useState(null);
  const [details, setDetails] = useState({});

  const toggleRow = async (id) => {
    if (openId === id) {
      setOpenId(null);
      return;
    }
    setOpenId(id);
    if (details[id]?.status === "ready") return;
    setDetails((d) => ({ ...d, [id]: { status: "loading" } }));
    try {
      const data = await getScanDetail(id);
      setDetails((d) => ({ ...d, [id]: { status: "ready", data } }));
    } catch (err) {
      setDetails((d) => ({ ...d, [id]: { status: "error", error: err.message } }));
    }
  };

  const refreshAll = () => {
    bins.reload();
    stats.reload();
    history.reload();
  };

  const changeCategory = (value) => {
    setCategory(value);
    setOffset(0);
    setOpenId(null);
  };

  const s = stats.data;
  const categories = s ? [...s.categories].sort((a, b) => b.count - a.count) : [];
  const topCategory = categories[0];

  return (
    <div className="page">
      <div className="page-head page-head--row">
        <div>
          <h1>Digital Twin</h1>
          <p>A virtual copy of your recycling. Bins fill up from the scans you confirm.</p>
        </div>
        <NeonButton size="sm" onClick={refreshAll}>
          Refresh
        </NeonButton>
      </div>

      {/* ---------- Virtual bins ---------- */}
      <section id="bins" className="section">
        <div className="section-head">
          <h2>Virtual bins</h2>
          {bins.data && <span className="ui-text muted">{bins.data.total_items} items in total</span>}
        </div>

        {bins.data && (
          <p className="virtual-note">
            <span className="badge badge--muted">Virtual</span>
            {bins.data.note}
          </p>
        )}

        <AsyncNotice loading={bins.loading} error={bins.error} onRetry={bins.reload} hasData={!!bins.data} />

        {bins.data &&
          (bins.data.bins.length ? (
            <div className="bin-grid">
              {bins.data.bins.map((bin) => (
                <BinCard key={bin.category} bin={bin} />
              ))}
            </div>
          ) : (
            <section className="panel empty-state">
              <h3>The bins are empty</h3>
              <p>Confirm a disposal on the Scan page and the matching bin starts to fill.</p>
              <NeonButton to="/" solid style={{ marginTop: 14 }}>
                Scan an item
              </NeonButton>
            </section>
          ))}
      </section>

      {/* ---------- Statistics ---------- */}
      <section id="stats" className="section">
        <div className="section-head">
          <h2>Statistics</h2>
        </div>

        <AsyncNotice loading={stats.loading} error={stats.error} onRetry={stats.reload} hasData={!!s} />

        {s && (
          <div className="stack" style={{ gap: 18 }}>
            <div className="stat-grid">
              <StatCard label="Total scans" value={s.total_scans} />
              <StatCard
                label="Top category"
                value={topCategory ? getCategoryMeta(topCategory.category).label : "–"}
                sub={topCategory ? `${topCategory.count} scans` : "No scans yet"}
                compact
              />
              <StatCard label="First scan" value={formatDate(s.first_scan_at)} compact />
              <StatCard label="Last scan" value={formatDate(s.last_scan_at)} compact />
            </div>

            {categories.length > 0 && (
              <div className="panel">
                <div className="panel-title">Scans by category</div>
                <div className="breakdown">
                  {categories.map((c) => (
                    <div className="breakdown-row" key={c.category}>
                      <div className="row row--between">
                        <CategoryBadge category={c.category} />
                        <span className="ui-text">
                          {c.count} ({Math.round(c.percentage)}%)
                        </span>
                      </div>
                      <div className="meter">
                        <div
                          className="meter-fill"
                          style={{
                            "--value": `${c.percentage}%`,
                            "--meter-color": toneColor(getCategoryTone(c.category)),
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* ---------- Scan history ---------- */}
      <section id="history" className="section">
        <div className="section-head">
          <h2>Scan history</h2>
          <div className="filter-row">
            <label className="ui-text muted" htmlFor="history-category">
              Category
            </label>
            <select
              id="history-category"
              className="neon-select"
              value={category}
              onChange={(e) => changeCategory(e.target.value)}
            >
              <option value="">All</option>
              {Object.entries(CATEGORY_META).map(([key, meta]) => (
                <option key={key} value={key}>
                  {meta.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <AsyncNotice
          loading={history.loading}
          error={history.error}
          onRetry={history.reload}
          hasData={!!history.data}
        />

        {history.data &&
          (history.data.items.length ? (
            <>
              <ul className="history-list">
                {history.data.items.map((item) => {
                  const isOpen = openId === item.id;
                  const detail = details[item.id];
                  return (
                    <li key={item.id} className="history-item">
                      <button
                        type="button"
                        className="history-row"
                        aria-expanded={isOpen}
                        onClick={() => toggleRow(item.id)}
                      >
                        <span className="history-label">{item.label}</span>
                        <CategoryBadge category={item.category} />
                        <span className="ui-text">{formatConfidence(item.confidence)}</span>
                        <SourceBadge source={item.source} />
                        <span className="ui-text muted">{formatDate(item.created_at)}</span>
                      </button>

                      {isOpen && (
                        <div className="history-detail">
                          {detail?.status === "loading" && <p className="muted">Loading scan details</p>}
                          {detail?.status === "error" && (
                            <div className="inline-alert" role="alert">
                              {detail.error}
                            </div>
                          )}
                          {detail?.status === "ready" &&
                            (detail.data.predictions.length ? (
                              <PredictionList predictions={detail.data.predictions} />
                            ) : (
                              <p className="muted">No predictions were saved with this scan.</p>
                            ))}
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
              <Pagination
                total={history.data.total}
                limit={PAGE_SIZE}
                offset={offset}
                onChange={(next) => {
                  setOffset(next);
                  setOpenId(null);
                }}
              />
            </>
          ) : (
            <section className="panel empty-state">
              <h3>{category ? "No scans in this category" : "No scans saved yet"}</h3>
              <p>
                {category
                  ? "Pick another category, or scan an item to add one."
                  : "Scans appear here after you confirm a disposal."}
              </p>
              <NeonButton to="/" solid style={{ marginTop: 14 }}>
                Scan an item
              </NeonButton>
            </section>
          ))}
      </section>
    </div>
  );
}
