"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";

import { LanguageSwitcher, useLanguage } from "@/components/language-provider";
import type { MessageKey } from "@/lib/translations";

import { MoneyGraph, roleColors } from "@/components/money-graph";
import {
  ApiError,
  moneyGraphApi,
  type ClusterDetail,
  type EgoGraphResponse,
  type NodeDetail,
  type PrioritiesResponse,
  type PriorityItem,
  type Role,
  type SummaryResponse,
} from "@/lib/api";

function RoleBadge({ role }: { role: Role }) {
  const { t } = useLanguage();
  return (
    <span className={`role-badge role-${role}`}>
      <span style={{ backgroundColor: roleColors[role] }} />
      {t(role)}
    </span>
  );
}

function SummaryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SignalBar({ label, value }: { label: string; value: number }) {
  const { percent } = useLanguage();
  return (
    <div className="signal-row">
      <div className="signal-label">
        <span>{label}</span>
        <strong>{percent(value)}</strong>
      </div>
      <div className="signal-track">
        <span style={{ width: `${Math.max(2, value * 100)}%` }} />
      </div>
    </div>
  );
}

function QueueItem({
  item,
  selected,
  onSelect,
}: {
  item: PriorityItem;
  selected: boolean;
  onSelect: (gid: string) => void;
}) {
  const { percent, evidence } = useLanguage();
  return (
    <button
      type="button"
      className={`queue-item ${selected ? "queue-item-selected" : ""}`}
      onClick={() => onSelect(item.gid)}
      aria-pressed={selected}
    >
      <div className="queue-rank">{String(item.rank).padStart(2, "0")}</div>
      <div className="queue-content">
        <div className="queue-title-row">
          <code>{item.gid}</code>
          <strong>{percent(item.priority_score)}</strong>
        </div>
        <RoleBadge role={item.role} />
        <p>{evidence(item.why)}</p>
      </div>
    </button>
  );
}

export function InvestigationWorkspace() {
  const { t, numberLocale, compactKzt, percent, count, evidence } = useLanguage();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [priorities, setPriorities] = useState<PrioritiesResponse | null>(null);
  const [node, setNode] = useState<NodeDetail | null>(null);
  const [graph, setGraph] = useState<EgoGraphResponse | null>(null);
  const [cluster, setCluster] = useState<ClusterDetail | null>(null);
  const [selectedGid, setSelectedGid] = useState<string | null>(null);
  const [searchGid, setSearchGid] = useState("");
  const [initialLoading, setInitialLoading] = useState(true);
  const [selectionLoading, setSelectionLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [initialError, setInitialError] = useState<MessageKey | null>(null);
  const [selectionError, setSelectionError] = useState<MessageKey | null>(null);
  const [searchError, setSearchError] = useState<MessageKey | null>(null);
  const selectionAbort = useRef<AbortController | null>(null);

  const selectNode = useCallback(async (gid: string, source: "queue" | "graph" | "search") => {
    selectionAbort.current?.abort();
    const controller = new AbortController();
    selectionAbort.current = controller;
    setSelectionLoading(true);
    setSelectionError(null);
    if (source === "search") {
      setSearchLoading(true);
      setSearchError(null);
    }
    try {
      const [nextNode, nextGraph] = await Promise.all([
        moneyGraphApi.node(gid, controller.signal),
        moneyGraphApi.nodeGraph(gid, controller.signal),
      ]);
      const nextCluster = await moneyGraphApi.cluster(nextNode.cluster_id, controller.signal);
      setNode(nextNode);
      setGraph(nextGraph);
      setCluster(nextCluster);
      setSelectedGid(nextNode.gid);
      if (source === "search") setSearchGid(nextNode.gid);
    } catch (error) {
      if (controller.signal.aborted) return;
      const message = "Unable to load this investigation.";
      if (source === "search" && error instanceof ApiError && error.status === 404) {
        setSearchError("Node not found");
      } else {
        setSelectionError(message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setSelectionLoading(false);
        setSearchLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function bootstrap() {
      try {
        const [nextSummary, nextPriorities] = await Promise.all([
          moneyGraphApi.summary(controller.signal),
          moneyGraphApi.priorities(controller.signal),
        ]);
        setSummary(nextSummary);
        setPriorities(nextPriorities);
        if (nextPriorities.items.length) {
          void selectNode(nextPriorities.items[0].gid, "queue");
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setInitialError("Unable to load MoneyGraph.");
        }
      } finally {
        if (!controller.signal.aborted) setInitialLoading(false);
      }
    }
    void bootstrap();
    return () => {
      controller.abort();
      selectionAbort.current?.abort();
    };
  }, [selectNode]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const gid = searchGid.trim();
    setSearchError(null);
    if (!/^\d+$/.test(gid)) {
      setSearchError("Enter the exact numeric GID.");
      return;
    }
    void selectNode(gid, "search");
  }

  const apiUnavailable = initialError !== null;

  return (
    <main className="workspace-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <h1>MoneyGraph</h1>
            <p>{t("Investigation workspace")}</p>
          </div>
        </div>
        <div className="summary-strip" aria-label={t("Dataset summary")}>
          <SummaryMetric label={t("Nodes")} value={summary ? summary.total_nodes.toLocaleString(numberLocale) : "—"} />
          <SummaryMetric label={t("Observed flow")} value={summary ? compactKzt(summary.total_observed_kzt) : "—"} />
          <SummaryMetric label={t("Seeds")} value={summary ? String(summary.seed_count) : "—"} />
          <SummaryMetric label={t("Clusters")} value={summary ? String(summary.cluster_count) : "—"} />
          <SummaryMetric label={t("Depth-4 boundary")} value={summary ? String(summary.depth_4_boundary_count) : "—"} />
        </div>
        <div className="topbar-actions">
          <LanguageSwitcher />
        <div className="snapshot-status">
          <span className={apiUnavailable ? "status-dot status-dot-error" : "status-dot"} />
          {t(apiUnavailable ? "API unavailable" : "Deterministic snapshot")}
        </div>
        </div>
      </header>

      <div className="workspace-grid">
        <aside className="queue-panel panel-column">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">{t("Investigation queue")}</span>
              <h2>{t("Priority nodes")}</h2>
            </div>
            <span className="count-pill">{priorities?.count ?? 0}</span>
          </div>
          <form className="gid-search" onSubmit={submitSearch}>
            <label htmlFor="gid-search">{t("Exact GID search")}</label>
            <div className="search-control">
              <input
                id="gid-search"
                inputMode="numeric"
                placeholder="10000000…"
                value={searchGid}
                onChange={(event) => setSearchGid(event.target.value)}
                aria-invalid={Boolean(searchError)}
              />
              <button type="submit" disabled={searchLoading} aria-label={t("Search GID")}>
                {searchLoading ? <span className="spinner spinner-small" /> : "→"}
              </button>
            </div>
            {searchError ? <p className="field-error" role="alert">{t(searchError)}</p> : null}
          </form>
          <div className="queue-divider">
            <span>{t("Ranked by explainable priority")}</span>
          </div>
          <div className="queue-list">
            {initialLoading
              ? Array.from({ length: 7 }, (_, index) => <div className="queue-skeleton" key={index} />)
              : null}
            {initialError ? (
              <div className="inline-state inline-state-error">
                <strong>{t("Could not load queue")}</strong>
                <p>{t(initialError)}</p>
              </div>
            ) : null}
            {priorities?.items.map((item) => (
              <QueueItem
                key={item.gid}
                item={item}
                selected={selectedGid === item.gid}
                onSelect={(gid) => void selectNode(gid, "queue")}
              />
            ))}
          </div>
        </aside>

        <section className="graph-panel panel-column">
          <div className="graph-header">
            <div>
              <span className="eyebrow">{t("Observed movement")}</span>
              <h2>{t("Money graph")}</h2>
            </div>
            <div className="role-legend" aria-label={t("Graph role legend")}>
              {(["coordinator", "consolidator", "distributor", "transit", "terminal", "peripheral"] as Role[]).map((role) => (
                <span key={role}><i style={{ backgroundColor: roleColors[role] }} />{t(role)}</span>
              ))}
            </div>
          </div>
          <MoneyGraph
            graph={graph}
            loading={selectionLoading || initialLoading}
            error={selectionError ? t(selectionError) : null}
            onNodeSelect={(gid) => void selectNode(gid, "graph")}
          />
        </section>

        <aside className={`detail-panel panel-column ${selectionLoading ? "panel-updating" : ""}`}>
          <div className="panel-heading detail-heading">
            <div>
              <span className="eyebrow">{t("Selected entity")}</span>
              <h2>{t("Investigation")}</h2>
            </div>
            {node ? <span className="depth-pill">{t("Depth")} {node.depth}</span> : null}
          </div>
          {!node && !selectionLoading ? (
            <div className="inline-state">
              <strong>{t("No node selected")}</strong>
              <p>{t("Select a queue row or search an exact GID.")}</p>
            </div>
          ) : null}
          {node ? (
            <div className="detail-scroll">
              <section className="entity-card">
                <div className="entity-topline">
                  <RoleBadge role={node.role} />
                  <span className="seed-label">{t(node.is_seed ? "Seed node" : "Non-seed")}</span>
                </div>
                <code className="entity-gid">{node.gid}</code>
                <div className="score-pair">
                  <div><span>{t("Priority")}</span><strong>{percent(node.priority_score, 1)}</strong></div>
                  <div><span>{t("Role confidence")}</span><strong>{percent(node.role_score, 1)}</strong></div>
                </div>
              </section>

              {node.observability.warning ? (
                <section className="warning-card" role="note">
                  <span>!</span>
                  <div><strong>{t("Observability limitation")}</strong><p>{evidence(node.observability.warning)}</p></div>
                </section>
              ) : null}

              <section className="detail-section">
                <div className="section-title"><span>{t("Investigation hypothesis")}</span></div>
                <p className="evidence-text">{evidence(node.evidence)}</p>
              </section>

              <section className="detail-section">
                <div className="section-title"><span>{t("Observed flow")}</span></div>
                <div className="metric-grid">
                  <div><span>{t("Incoming")}</span><strong>{compactKzt(node.metrics.incoming_kzt)}</strong><small>{count(node.metrics.incoming_transaction_count, "transactions")}</small></div>
                  <div><span>{t("Outgoing")}</span><strong>{compactKzt(node.metrics.outgoing_kzt)}</strong><small>{count(node.metrics.outgoing_transaction_count, "transactions")}</small></div>
                  <div><span>{t("Unique senders")}</span><strong>{node.metrics.unique_senders}</strong><small>{t("observed counterparties")}</small></div>
                  <div><span>{t("Unique recipients")}</span><strong>{node.metrics.unique_recipients}</strong><small>{t("observed counterparties")}</small></div>
                </div>
                <div className="secondary-metrics">
                  <span>{t("Pass-through")} <strong>{percent(node.metrics.pass_through_ratio)}</strong></span>
                  <span>{t("Near-time flow")} <strong>{percent(node.metrics.fast_forward_ratio)}</strong></span>
                  <span>{t("Seed paths")} <strong>{node.metrics.seed_ancestor_count}</strong></span>
                </div>
              </section>

              <section className="detail-section">
                <div className="section-title"><span>{t("Priority signals")}</span></div>
                <div className="signals">
                  <SignalBar label={t("Role strength")} value={node.priority_components.role_strength} />
                  <SignalBar label={t("Money significance")} value={node.priority_components.money_significance} />
                  <SignalBar label={t("Structural importance")} value={node.priority_components.structural_importance} />
                  <SignalBar label={t("Seed connectivity")} value={node.priority_components.seed_connectivity} />
                  <SignalBar label={t("Anomaly evidence")} value={node.priority_components.anomaly_evidence} />
                </div>
                <div className="technical-signals">
                  <span>PageRank <strong>{node.metrics.pagerank.toExponential(2)}</strong></span>
                  <span>{t("Betweenness")} <strong>{node.metrics.betweenness.toExponential(2)}</strong></span>
                </div>
              </section>

              {cluster ? (
                <section className="cluster-card">
                  <div className="cluster-title">
                    <div><span>{t("Cluster context")}</span><strong>{t("Cluster")} {cluster.cluster_id}</strong></div>
                    <span className="cluster-size">{count(cluster.n_nodes, "nodes")}</span>
                  </div>
                  <div className="cluster-stats">
                    <div><span>{t("Internal flow")}</span><strong>{compactKzt(cluster.sum_kzt_internal)}</strong></div>
                    <div><span>{t("Seed nodes")}</span><strong>{cluster.n_seed}</strong></div>
                  </div>
                  <p>{evidence(cluster.hypothesis)}</p>
                  <span className="top-gids-label">{t("Important GIDs")}</span>
                  <div className="gid-chips">
                    {cluster.top_gids.map((gid) => (
                      <button type="button" key={gid} onClick={() => void selectNode(gid, "graph")}>{gid}</button>
                    ))}
                  </div>
                </section>
              ) : null}
            </div>
          ) : null}
        </aside>
      </div>
    </main>
  );
}
