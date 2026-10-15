import { useState } from "react";

import AsyncNotice from "../components/AsyncNotice.jsx";
import NeonButton from "../components/NeonButton.jsx";
import Pagination from "../components/Pagination.jsx";
import StatCard from "../components/StatCard.jsx";
import TreeGame from "../components/TreeGame.jsx";
import TreeProgress from "../components/TreeProgress.jsx";
import { getRewardBalance, getRewardHistory } from "../api/client";
import { formatDate } from "../utils/categories";
import { useAsync } from "../utils/useAsync";
import "./DigitalTwinPage.css"; // shared section styles
import "./TreeGamePage.css";

const PAGE_SIZE = 10;

export default function TreeGamePage() {
  const balance = useAsync(() => getRewardBalance(), []);
  const [offset, setOffset] = useState(0);
  const rewards = useAsync(() => getRewardHistory({ limit: PAGE_SIZE, offset }), [offset]);

  const b = balance.data;

  return (
    <div className="page">
      <div className="page-head page-head--row">
        <div>
          <h1>Tree Game</h1>
          <p>Every confirmed disposal waters your tree. Scan, confirm, and watch it grow.</p>
        </div>
        <NeonButton
          size="sm"
          onClick={() => {
            balance.reload();
            rewards.reload();
          }}
        >
          Refresh
        </NeonButton>
      </div>

      <AsyncNotice loading={balance.loading} error={balance.error} onRetry={balance.reload} hasData={!!b} />

      <div className="tree-grid" style={{ marginTop: 16 }}>
        <section className="panel">
          <TreeGame level={b?.tree_level ?? 0} progressPct={b?.tree_progress_pct ?? 0} />
        </section>

        <div className="stack">
          <section className="panel panel--flow">
            <TreeProgress
              level={b?.tree_level ?? 0}
              progressPct={b?.tree_progress_pct ?? 0}
              droplets={b?.droplets ?? 0}
            />
          </section>

          <div className="stat-grid">
            <StatCard label="Droplets" value={b?.droplets ?? "–"} />
            <StatCard label="Tree level" value={b?.tree_level ?? "–"} />
          </div>

          <section className="panel panel--flow">
            <h3>Grow it faster</h3>
            <p className="prose">
              Scan an item, then press Confirm disposal. Each confirmed scan earns droplets, and the
              same scan never pays twice.
            </p>
            <NeonButton to="/" solid>
              Scan an item
            </NeonButton>
          </section>
        </div>
      </div>

      {/* ---------- Droplet history ---------- */}
      <section id="history" className="section">
        <div className="section-head">
          <h2>Droplet history</h2>
        </div>

        <AsyncNotice
          loading={rewards.loading}
          error={rewards.error}
          onRetry={rewards.reload}
          hasData={!!rewards.data}
        />

        {rewards.data &&
          (rewards.data.items.length ? (
            <>
              <ul className="reward-list">
                {rewards.data.items.map((item) => (
                  <li key={item.id} className="reward-row">
                    <span className="reward-amount">
                      {item.amount > 0 ? `+${item.amount}` : item.amount}
                    </span>
                    <span className="reward-reason">{item.reason}</span>
                    {item.scan_id != null && <span className="ui-text muted">Scan #{item.scan_id}</span>}
                    <span className="ui-text muted">{formatDate(item.created_at)}</span>
                  </li>
                ))}
              </ul>
              <Pagination
                total={rewards.data.total}
                limit={PAGE_SIZE}
                offset={offset}
                onChange={setOffset}
              />
            </>
          ) : (
            <section className="panel empty-state">
              <h3>No droplets earned yet</h3>
              <p>Confirm your first disposal on the Scan page to water the tree.</p>
              <NeonButton to="/" solid style={{ marginTop: 14 }}>
                Scan an item
              </NeonButton>
            </section>
          ))}
      </section>
    </div>
  );
}
