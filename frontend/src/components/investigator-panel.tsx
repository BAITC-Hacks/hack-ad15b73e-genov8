"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { useLanguage } from "@/components/language-provider";
import { translate, type Locale, type MessageKey } from "@/lib/translations";

import {
  moneyGraphApi,
  type InvestigatorResponse,
  type ToolCallRecord,
} from "@/lib/api";

interface InvestigatorPanelProps {
  selectedGid: string | null;
  onNodeSelect: (gid: string) => void;
}

const toolLabels: Record<ToolCallRecord["name"], MessageKey> = {
  node_card: "Node card", common_receivers: "Common receivers", paths: "Paths",
  filter_nodes: "Filter nodes", cluster_summary: "Cluster summary", what_if_remove: "Removal simulation",
};
const argumentLabels: Record<string, MessageKey> = {
  gid: "GID", gids: "GIDs", max_hops: "Maximum hops", src_gid: "Source GID",
  dst_gid: "Target GID", role: "Role", cluster_id: "Cluster", min_priority: "Minimum priority",
  min_observed_kzt: "Minimum observed amount", limit: "Limit",
};

function argumentSummary(argumentsValue: Record<string, unknown>, locale: Locale): string {
  const parts = Object.entries(argumentsValue)
    .filter(([, value]) => value !== null)
    .map(([key, value]) => {
      const rendered = key === "role" && typeof value === "string" && ["coordinator", "consolidator", "distributor", "transit", "terminal", "peripheral"].includes(value)
        ? translate(locale, value as MessageKey)
        : Array.isArray(value) ? value.join(", ") : String(value);
      return `${argumentLabels[key] ? translate(locale, argumentLabels[key]) : key}: ${rendered}`;
    });
  return parts.join(" · ");
}

export function InvestigatorPanel(props: InvestigatorPanelProps) {
  const { locale } = useLanguage();
  return <LocalizedInvestigatorPanel key={locale} {...props} />;
}

function LocalizedInvestigatorPanel({ selectedGid, onNodeSelect }: InvestigatorPanelProps) {
  const { t, locale } = useLanguage();
  const requestAbort = useRef<AbortController | null>(null);
  useEffect(() => () => requestAbort.current?.abort(), []);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<InvestigatorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<MessageKey | null>(null);

  async function ask(questionText: string) {
    const trimmed = questionText.trim();
    if (!trimmed || loading) return;
    if (trimmed.length < 3) { setError("Question must contain at least 3 characters."); return; }
    setQuestion(trimmed);
    setLoading(true);
    setError(null);
    setResult(null);
    const controller = new AbortController();
    requestAbort.current = controller;
    try {
      const response = await moneyGraphApi.investigate(trimmed, locale, selectedGid, controller.signal);
      if (!controller.signal.aborted) setResult(response);
    } catch {
      if (!controller.signal.aborted) setError("The AI investigator could not complete this request.");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void ask(question);
  }

  const unavailable = result?.status === "unavailable";

  return (
    <section className={`investigator-panel ${result || error ? "investigator-panel-open" : ""}`} aria-label={t("AI Investigator")}>
      <div className="investigator-heading">
        <div className="investigator-title">
          <span className="investigator-mark" aria-hidden="true">✦</span>
          <div>
            <strong>{t("AI Investigator")}</strong>
            <span>{t("Optional · grounded MoneyGraph tools")}</span>
          </div>
        </div>
        <span className={unavailable ? "investigator-state investigator-state-off" : "investigator-state"}>
          {t(unavailable ? "Unavailable" : "5-call limit")}
        </span>
      </div>

      <form className="investigator-form" onSubmit={submit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={t(selectedGid ? "Ask about this node or the observed network…" : "Ask about the observed network…")}
          maxLength={1000}
          disabled={loading}
          aria-label={t("Investigation question")}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? <span className="spinner spinner-small" /> : t("Ask")}
        </button>
      </form>

      {!result && !error && !loading ? (
        <div className="investigator-suggestions" aria-label={t("Suggested investigation questions")}>
          <button type="button" disabled={!selectedGid} onClick={() => void ask(t("Why is GID {gid} high priority?").replace("{gid}", selectedGid ?? ""))}>
            {t("Why high priority?")}
          </button>
          <button type="button" onClick={() => void ask(t("Show high-priority consolidators."))}>
            {t("Find consolidators")}
          </button>
          <button type="button" disabled={!selectedGid} onClick={() => void ask(t("What would happen if we removed GID {gid}?").replace("{gid}", selectedGid ?? ""))}>
            {t("Removal impact")}
          </button>
        </div>
      ) : null}

      {loading ? (
        <div className="investigator-progress">
          <span className="spinner" />
          <div><strong>{t("Checking observed evidence")}</strong><span>{t("Running bounded read-only tools")}</span></div>
        </div>
      ) : null}

      {error ? (
        <div className="investigator-message investigator-message-error">
          <strong>{t("Investigator request failed")}</strong>
          <p>{t(error)}</p>
        </div>
      ) : null}

      {result ? (
        <div className={`investigator-result ${unavailable ? "investigator-result-unavailable" : ""}`}>
          <div className="investigator-answer-head">
            <span>{t(unavailable ? "Configuration" : "Grounded finding")}</span>
            <button type="button" onClick={() => setResult(null)} aria-label={t("Close investigator result")}>×</button>
          </div>
          <p className="investigator-answer">{result.answer}</p>

          {result.referenced_gids.length ? (
            <div className="investigator-references">
              <span>{t("Referenced GIDs")}</span>
              <div>
                {result.referenced_gids.map((gid) => (
                  <button type="button" key={gid} onClick={() => onNodeSelect(gid)}>{gid}</button>
                ))}
              </div>
            </div>
          ) : null}

          {result.tool_calls.length ? (
            <div className="investigator-activity">
              <span>{t("Factual activity")}</span>
              <ol>
                {result.tool_calls.map((call, index) => (
                  <li key={`${call.name}-${index}`}>
                    <i className={call.status === "ok" ? "" : "activity-error"}>{index + 1}</i>
                    <div>
                      <strong>{t(toolLabels[call.name])}</strong>
                      <span>{argumentSummary(call.arguments, locale)}</span>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
