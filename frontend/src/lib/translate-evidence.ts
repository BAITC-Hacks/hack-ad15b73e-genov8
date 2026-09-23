import type { Locale } from "./translations";

// Match complete backend templates; preserve unfamiliar text rather than inventing an explanation.
// Values are kept verbatim so the translation cannot change the underlying evidence.
export const evidenceTemplates: readonly (readonly [string, string, string])[] = [
  [
    "Depth 4 boundary: {0} from {1} senders; downstream activity is unobserved, so no terminal conclusion.",
    "Граница глубины 4: {0} от отправителей ({1}); дальнейшая активность не наблюдается, поэтому вывод о конечном узле невозможен.",
    "4-деңгей шекарасы: жіберушілерден ({1}) {0}; әрі қарайғы белсенділік бақыланбайды, сондықтан соңғы түйін деген қорытынды жасауға болмайды."
  ],
  [
    "Coordination signs: {0} senders, {1} recipients, {2} in/{3} out; structural {4}.",
    "Признаки координации: отправителей — {0}, получателей — {1}, входящие — {2}, исходящие — {3}; структурная значимость — {4}.",
    "Үйлестіру белгілері: жіберушілер — {0}, алушылар — {1}, кіріс — {2}, шығыс — {3}; құрылымдық маңыздылық — {4}."
  ],
  [
    "Distribution signs: {0} recipients, {1} out in {2} tx; investigation hypothesis.",
    "Признаки распределения: получателей — {0}, исходящие — {1}, транзакций — {2}; гипотеза расследования.",
    "Үлестіру белгілері: алушылар — {0}, шығыс — {1}, транзакциялар — {2}; тергеу болжамы."
  ],
  [
    "Consolidation signs: {0} senders, {1} in, {2} recipients; investigation hypothesis.",
    "Признаки консолидации: отправителей — {0}, входящие — {1}, получателей — {2}; гипотеза расследования.",
    "Жинақтау белгілері: жіберушілер — {0}, кіріс — {1}, алушылар — {2}; тергеу болжамы."
  ],
  [
    "Pass-through signs: {0} sent onward; {1} outgoing value within 0-2 days; hypothesis only.",
    "Признаки транзита: {0} переведено далее; {1} исходящей суммы — в течение 0–2 дней; только гипотеза.",
    "Транзит белгілері: {0} әрі қарай аударылған; шығыс сомасының {1} бөлігі 0–2 күн ішінде аударылған; тек болжам."
  ],
  [
    "Observed depth {0}: {1} retained ({2}) with {3} recipients; terminal-behavior hypothesis.",
    "Наблюдаемая глубина — {0}: удержано {1} ({2}), получателей — {3}; гипотеза поведения конечного узла.",
    "Бақыланған тереңдік — {0}: сақталған сома — {1} ({2}), алушылар — {3}; соңғы түйін мінез-құлқы туралы болжам."
  ],
  [
    "Seed: {0} recipients and {1} observed out; incoming flow is incomplete; investigation hypothesis only.",
    "Исходный узел: получателей — {0}, наблюдаемые исходящие — {1}; входящие данные неполны; только гипотеза расследования.",
    "Бастапқы түйін: алушылар — {0}, бақыланған шығыс — {1}; кіріс деректері толық емес; тек тергеу болжамы."
  ],
  [
    "Peripheral pattern: {0} senders, {1} recipients, {2} observed flow; no stronger rule matched.",
    "Периферийная структура: отправителей — {0}, получателей — {1}, наблюдаемый поток — {2}; более выраженных признаков не выявлено.",
    "Шеткі құрылым: жіберушілер — {0}, алушылар — {1}, бақыланған ағын — {2}; күштірек белгілер анықталмады."
  ],
  [
    "Depth 4 is the traversal boundary. Outgoing activity is unobserved, so zero observed out-degree is not terminal evidence.",
    "Глубина 4 — граница обхода графа. Исходящая активность не наблюдается, поэтому отсутствие исходящих связей не доказывает, что узел конечный.",
    "4-деңгей — графты шолу шекарасы. Шығыс белсенділігі бақыланбайды, сондықтан шығыс байланыстарының болмауы түйіннің соңғы екенін дәлелдемейді."
  ],
  [
    "Seed incoming flow is incomplete; pass-through and retained-funds conclusions are not used.",
    "Данные о входящем потоке исходного узла неполны; выводы о транзите и удержании средств не используются.",
    "Бастапқы түйіннің кіріс ағыны туралы деректер толық емес; транзит пен қаражатты сақтау туралы қорытындылар қолданылмайды."
  ],
  [
    "Isolated in the observed graph; no transactional hypothesis.",
    "Изолирован в наблюдаемом графе; гипотезы о переводах нет.",
    "Бақыланған графта оқшауланған; аударымдар туралы болжам жоқ."
  ],
  [
    "Depth-4 boundary community; downstream behavior is unobserved.",
    "Сообщество на границе глубины 4; дальнейшая активность не наблюдается.",
    "4-деңгей шекарасындағы қауымдастық; әрі қарайғы белсенділік бақыланбайды."
  ],
  [
    "Investigation hypothesis: multi-seed coordination network.",
    "Гипотеза расследования: сеть координации с несколькими исходными узлами.",
    "Тергеу болжамы: бірнеше бастапқы түйіні бар үйлестіру желісі."
  ],
  [
    "Investigation hypothesis: coordination-centered transfer network.",
    "Гипотеза расследования: сеть переводов с центром координации.",
    "Тергеу болжамы: үйлестіруге негізделген аударымдар желісі."
  ],
  [
    "Investigation hypothesis: distribution-centered transfer network.",
    "Гипотеза расследования: сеть переводов с центром распределения.",
    "Тергеу болжамы: үлестіруге негізделген аударымдар желісі."
  ],
  [
    "Investigation hypothesis: consolidation-centered transfer network.",
    "Гипотеза расследования: сеть переводов с центром консолидации.",
    "Тергеу болжамы: жинақтауға негізделген аударымдар желісі."
  ],
  [
    "Investigation hypothesis: pass-through transfer network.",
    "Гипотеза расследования: сеть транзитных переводов.",
    "Тергеу болжамы: транзиттік аударымдар желісі."
  ],
  [
    "Investigation hypothesis: observed retention-centered network.",
    "Гипотеза расследования: сеть с наблюдаемым удержанием средств.",
    "Тергеу болжамы: қаражаттың сақталуы байқалатын желісі."
  ],
  [
    "Investigation hypothesis: mixed or peripheral transfer network.",
    "Гипотеза расследования: сеть смешанных или периферийных переводов.",
    "Тергеу болжамы: аралас немесе шеткі аударымдар желісі."
  ]
];

const escapeRegex = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const compiled = evidenceTemplates.map(([source, ru, kk]) => ({
  pattern: new RegExp("^" + source.split(/\{\d+\}/).map(escapeRegex).join("(.*?)") + "$"),
  ru, kk,
}));

export function translateEvidence(locale: Locale, text: string): string {
  if (locale === "en") return text;
  const caveat = " Seed inflow incomplete.";
  const hasCaveat = text.endsWith(caveat);
  const base = hasCaveat ? text.slice(0, -caveat.length) : text;
  for (const rule of compiled) {
    const match = base.match(rule.pattern);
    if (!match) continue;
    const translated = rule[locale].replace(/\{(\d+)\}/g, (_, index: string) => match[Number(index) + 1]);
    return translated + (hasCaveat ? (locale === "ru" ? " Данные о входящем потоке исходного узла неполны." : " Бастапқы түйіннің кіріс ағыны туралы деректер толық емес.") : "");
  }
  return text;
}
