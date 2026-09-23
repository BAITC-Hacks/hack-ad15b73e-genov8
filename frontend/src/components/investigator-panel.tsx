"use client";

import { FormEvent, useState } from "react";

import {
  ApiError,
  moneyGraphApi,
  type InvestigatorResponse,
  type ToolCallRecord,
} from "@/lib/api";

interface InvestigatorPanelProps {
  selectedGid: string | null;
  onNodeSelect: (gid: string) => void;
}

function toolLabel(name: ToolCallRecord["name"]): string {
  return name.replaceAll("_", " ");
}

function argumentSummary(argumentsValue: Record<string, unknown>): string {
  const parts = Object.entries(argumentsValue)
    .filter(([, value]) => value !== null)
    .map(([key, value]) => {
      const rendered = Array.isArray(value) ? value.join(", ") : String(value);
      return `${key.replaceAll("_", " ")}: ${rendered}`;
    });
  return parts.join(" · ");
}

export function InvestigatorPanel({ selectedGid, onNodeSelect }: InvestigatorPanelProps) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<InvestigatorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(questionText: string) {
    const trimmed = questionText.trim();
    if (!trimmed || loading) return;
    setQuestion(trimmed);
    setLoading(true);
    setError(null);
    setResult(null);
    const contextualQuestion = selectedGid && !trimmed.includes(selectedGid)
      ? `${trimmed}\n\nSelected MoneyGraph GID for references such as "this node": ${selectedGid}.`
      : trimmed;
    try {
      setResult(await moneyGraphApi.investigate(contextualQuestion));
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "The AI investigator could not complete this request.",
      );
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void ask(question);
  }

  const unavailable = result?.status === "unavailable";

  return (
    <section className={`investigator-panel ${result || error ? "investigator-panel-open" : ""}`} aria-label="AI Investigator">
      <div className="investigator-heading">
        <div className="investigator-title">
          <span className="investigator-mark" aria-hidden="true">✦</span>
          <div>
            <strong>AI Investigator</strong>
            <span>Optional · grounded MoneyGraph tools</span>
          </div>
        </div>
        <span className={unavailable ? "investigator-state investigator-state-off" : "investigator-state"}>
          {unavailable ? "Unavailable" : "5-call limit"}
        </span>
      </div>

      <form className="investigator-form" onSubmit={submit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={selectedGid ? "Ask about this node or the observed network…" : "Ask about the observed network…"}
          maxLength={1000}
          disabled={loading}
          aria-label="Investigation question"
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? <span className="spinner spinner-small" /> : "Ask"}
        </button>
      </form>

      {!result && !error && !loading ? (
        <div className="investigator-suggestions" aria-label="Suggested investigation questions">
          <button type="button" disabled={!selectedGid} onClick={() => void ask(`Why is GID ${selectedGid} high priority?`)}>
            Why high priority?
          </button>
          <button type="button" onClick={() => void ask("Show high-priority consolidators.")}>
            Find consolidators
          </button>
          <button type="button" disabled={!selectedGid} onClick={() => void ask(`What would happen if we removed GID ${selectedGid}?`)}>
            Removal impact
          </button>
        </div>
      ) : null}

      {loading ? (
        <div className="investigator-progress">
          <span className="spinner" />
          <div><strong>Checking observed evidence</strong><span>Running bounded read-only tools</span></div>
        </div>
      ) : null}

      {error ? (
        <div className="investigator-message investigator-message-error">
          <strong>Investigator request failed</strong>
          <p>{error}</p>
        </div>
      ) : null}

      {result ? (
        <div className={`investigator-result ${unavailable ? "investigator-result-unavailable" : ""}`}>
          <div className="investigator-answer-head">
            <span>{unavailable ? "Configuration" : "Grounded finding"}</span>
            <button type="button" onClick={() => setResult(null)} aria-label="Close investigator result">×</button>
          </div>
          <p className="investigator-answer">{result.answer}</p>

          {result.referenced_gids.length ? (
            <div className="investigator-references">
              <span>Referenced GIDs</span>
              <div>
                {result.referenced_gids.map((gid) => (
                  <button type="button" key={gid} onClick={() => onNodeSelect(gid)}>{gid}</button>
                ))}
              </div>
            </div>
          ) : null}

          {result.tool_calls.length ? (
            <div className="investigator-activity">
              <span>Factual activity</span>
              <ol>
                {result.tool_calls.map((call, index) => (
                  <li key={`${call.name}-${index}`}>
                    <i className={call.status === "ok" ? "" : "activity-error"}>{index + 1}</i>
                    <div>
                      <strong>{toolLabel(call.name)}</strong>
                      <span>{argumentSummary(call.arguments)}</span>
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
