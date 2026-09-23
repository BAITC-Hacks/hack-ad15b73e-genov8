"use client";

import cytoscape, { type Core, type ElementDefinition, type StylesheetJson } from "cytoscape";
import { useEffect, useMemo, useRef, useState } from "react";

import { useLanguage } from "@/components/language-provider";

import type { EgoGraphResponse, Role } from "@/lib/api";

interface MoneyGraphProps {
  graph: EgoGraphResponse | null;
  loading: boolean;
  error: string | null;
  onNodeSelect: (gid: string) => void;
}

interface EdgeTooltip {
  x: number;
  y: number;
  sumKzt: number;
  transactionCount: number;
}

const roleColors: Record<Role, string> = {
  coordinator: "#c2412d",
  distributor: "#d47a18",
  consolidator: "#6d56a5",
  transit: "#1f7a78",
  terminal: "#3a6f9f",
  peripheral: "#8a969a",
};

const stylesheet: StylesheetJson = [
  {
    selector: "node",
    style: {
      "background-color": "data(color)",
      "border-color": "#ffffff",
      "border-width": 2,
      color: "#233238",
      "font-family": "var(--font-sans)",
      "font-size": 9,
      "font-weight": 700,
      height: "data(size)",
      label: "data(label)",
      "text-background-color": "#f8faf9",
      "text-background-opacity": 0.9,
      "text-background-padding": "3px",
      "text-margin-y": 8,
      "text-valign": "bottom",
      width: "data(size)",
    },
  },
  {
    selector: "node:selected",
    style: {
      "border-color": "#f3b33d",
      "border-width": 5,
      "overlay-color": "#f3b33d",
      "overlay-opacity": 0.12,
      "overlay-padding": 8,
    },
  },
  {
    selector: ".focus-node",
    style: {
      "border-color": "#f3b33d",
      "border-width": 5,
      "font-size": 10,
      "text-background-opacity": 1,
      "z-index": 10,
    },
  },
  {
    selector: "edge",
    style: {
      "curve-style": "bezier",
      "line-color": "#9ba8aa",
      opacity: 0.65,
      "target-arrow-color": "#748286",
      "target-arrow-shape": "triangle",
      "arrow-scale": 0.9,
      width: "data(width)",
    },
  },
  {
    selector: ".focus-edge",
    style: {
      "line-color": "#547a78",
      opacity: 0.9,
      "target-arrow-color": "#365f5d",
    },
  },
];

function shortGid(gid: string): string {
  return `…${gid.slice(-6)}`;
}

export function MoneyGraph({ graph, loading, error, onNodeSelect }: MoneyGraphProps) {
  const { t, compactKzt, count } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [edgeTooltip, setEdgeTooltip] = useState<EdgeTooltip | null>(null);
  const onNodeSelectRef = useRef(onNodeSelect);
  onNodeSelectRef.current = onNodeSelect;

  const elements = useMemo<ElementDefinition[]>(() => {
    if (!graph) return [];
    const values = graph.edges.map((edge) => Math.log1p(edge.sum_kzt));
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;
    const spread = Math.max(max - min, 1);
    const nodes: ElementDefinition[] = graph.nodes.map((node) => ({
      group: "nodes",
      data: {
        id: node.gid,
        label: shortGid(node.gid),
        color: roleColors[node.role],
        size: node.is_selected ? 34 : 19 + node.priority_score * 9,
        isSelected: node.is_selected ? 1 : 0,
      },
      classes: node.is_selected ? "focus-node" : "",
    }));
    const edges: ElementDefinition[] = graph.edges.map((edge, index) => ({
      group: "edges",
      data: {
        id: `${edge.source_gid}-${edge.target_gid}-${index}`,
        source: edge.source_gid,
        target: edge.target_gid,
        width: 1.2 + ((Math.log1p(edge.sum_kzt) - min) / spread) * 5.8,
        sumKzt: edge.sum_kzt,
        transactionCount: edge.transaction_count,
      },
      classes:
        edge.source_gid === graph.selected_gid || edge.target_gid === graph.selected_gid
          ? "focus-edge"
          : "",
    }));
    return [...nodes, ...edges];
  }, [graph]);

  useEffect(() => {
    if (!containerRef.current || !graph || !elements.length) return;
    cyRef.current?.destroy();
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: stylesheet,
      minZoom: 0.45,
      maxZoom: 2.4,
      wheelSensitivity: 0.18,
      layout: {
        name: "concentric",
        animate: false,
        fit: true,
        padding: 54,
        minNodeSpacing: 42,
        concentric: (node) => Number(node.data("isSelected")) * 10,
        levelWidth: () => 1,
      },
    });
    cy.on("tap", "node", (event) => {
      setEdgeTooltip(null);
      onNodeSelectRef.current(event.target.id());
    });
    const showEdgeTooltip = (event: cytoscape.EventObject) => {
      setEdgeTooltip({
        x: event.renderedPosition.x,
        y: event.renderedPosition.y,
        sumKzt: Number(event.target.data("sumKzt")),
        transactionCount: Number(event.target.data("transactionCount")),
      });
    };
    cy.on("mouseover tap", "edge", showEdgeTooltip);
    cy.on("mouseout", "edge", () => setEdgeTooltip(null));
    cy.on("pan zoom", () => setEdgeTooltip(null));
    cyRef.current = cy;

    const observer = new ResizeObserver(() => {
      cy.resize();
      cy.fit(undefined, 48);
    });
    observer.observe(containerRef.current);
    return () => {
      observer.disconnect();
      cy.destroy();
      cyRef.current = null;
    };
  }, [elements, graph]);

  return (
    <div className="graph-stage">
      <div ref={containerRef} className="graph-canvas" aria-label={t("Directed ego money graph")} />
      {edgeTooltip ? (
        <div className="edge-tooltip" style={{ left: edgeTooltip.x, top: edgeTooltip.y }}>
          <strong>{compactKzt(edgeTooltip.sumKzt)}</strong>
          <span>{count(edgeTooltip.transactionCount, "transactions")}</span>
        </div>
      ) : null}
      {!graph && !loading && !error ? (
        <div className="graph-state">
          <span className="state-icon">◎</span>
          <strong>{t("Select an investigation")}</strong>
          <p>{t("Choose a priority or search an exact GID to load its observed network.")}</p>
        </div>
      ) : null}
      {loading ? (
        <div className="graph-state graph-state-loading">
          <span className="spinner" />
          <strong>{t("Loading observed network")}</strong>
        </div>
      ) : null}
      {error ? (
        <div className="graph-state graph-state-error">
          <span className="state-icon">!</span>
          <strong>{t("Network unavailable")}</strong>
          <p>{error}</p>
        </div>
      ) : null}
      {graph ? (
        <div className="graph-status">
          <span>{count(graph.displayed_neighbor_count, "neighbors")}</span>
          {graph.truncated ? <span className="graph-limit">{t("bounded view")}</span> : null}
        </div>
      ) : null}
      <div className="graph-help">{t("Scroll to zoom · drag to pan · hover an edge for flow · click a node to investigate")}</div>
    </div>
  );
}

export { roleColors };
