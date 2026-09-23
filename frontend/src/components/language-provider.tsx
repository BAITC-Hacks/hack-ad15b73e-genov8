"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { formatCount, translate, type Locale, type MessageKey } from "@/lib/translations";
import { translateEvidence } from "@/lib/translate-evidence";

const LanguageContext = createContext<{ locale: Locale; setLocale: (locale: Locale) => void } | null>(null);
const storageKey = "moneygraph.locale";

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("ru");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved === "ru" || saved === "kk" || saved === "en") setLocale(saved);
    } catch { /* The interface also works when storage is disabled. */ }
    setReady(true);
  }, []);
  useEffect(() => {
    document.documentElement.lang = locale;
    if (ready) {
      try { localStorage.setItem(storageKey, locale); } catch { /* Keep the in-memory selection. */ }
    }
  }, [locale, ready]);
  return <LanguageContext.Provider value={{ locale, setLocale }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("LanguageProvider is required");
  const { locale } = context;
  const numberLocale = locale === "en" ? "en-US" : locale === "ru" ? "ru-RU" : (
    Intl.NumberFormat.supportedLocalesOf("kk-KZ").length ? "kk-KZ" : "ru-RU"
  );
  return {
    ...context,
    numberLocale,
    t: (key: MessageKey) => translate(locale, key),
    count: (value: number, kind: "nodes" | "transactions" | "neighbors") => formatCount(locale, value, kind),
    evidence: (value: string) => translateEvidence(locale, value),
    compactKzt: (value: number) => {
      if (locale !== "kk") return new Intl.NumberFormat(numberLocale, { notation: "compact", maximumFractionDigits: 1 }).format(value) + " ₸";
      const magnitude = Math.abs(value);
      const [divisor, unit] = magnitude >= 1e12 ? [1e12, " трлн"] : magnitude >= 1e9 ? [1e9, " млрд"] : magnitude >= 1e6 ? [1e6, " млн"] : magnitude >= 1e3 ? [1e3, " мың"] : [1, ""];
      return new Intl.NumberFormat(numberLocale, { maximumFractionDigits: 1 }).format(value / divisor) + unit + " ₸";
    },
    percent: (value: number | null, digits = 0) => value === null ? translate(locale, "Not available") : new Intl.NumberFormat(numberLocale, { style: "percent", minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value),
  };
}

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useLanguage();
  return (
    <div className="language-switcher" role="group" aria-label={t("Language")}>
      <button type="button" lang="ru" aria-pressed={locale === "ru"} onClick={() => setLocale("ru")}>Русский</button>
      <button type="button" lang="kk" aria-pressed={locale === "kk"} onClick={() => setLocale("kk")}>Қазақша</button>
      <button type="button" lang="en" aria-pressed={locale === "en"} onClick={() => setLocale("en")}>English</button>
    </div>
  );
}
