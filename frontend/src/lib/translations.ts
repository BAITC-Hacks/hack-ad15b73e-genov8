export type Locale = "ru" | "kk" | "en";

export const messages = {
  "AI Investigator": {"ru":"AI-помощник расследования","kk":"Тергеуге арналған AI көмекші"},
  "Optional · grounded MoneyGraph tools": {"ru":"Анализ на основе данных MoneyGraph","kk":"MoneyGraph деректеріне негізделген талдау"},
  "Unavailable": {"ru":"Недоступен","kk":"Қолжетімсіз"},
  "5-call limit": {"ru":"До 5 проверок","kk":"5 тексеруге дейін"},
  "Ask about this node or the observed network…": {"ru":"Спросите об этом узле или наблюдаемых связях…","kk":"Осы түйін немесе бақыланған байланыстар туралы сұраңыз…"},
  "Ask about the observed network…": {"ru":"Спросите о наблюдаемых связях…","kk":"Бақыланған байланыстар туралы сұраңыз…"},
  "Investigation question": {"ru":"Вопрос для расследования","kk":"Тергеу сұрағы"},
  "Ask": {"ru":"Спросить","kk":"Сұрау"},
  "Suggested investigation questions": {"ru":"Примеры вопросов","kk":"Сұрақ үлгілері"},
  "Why high priority?": {"ru":"Почему высокий приоритет?","kk":"Неге басымдығы жоғары?"},
  "Find consolidators": {"ru":"Найти консолидаторов","kk":"Жинақтаушыларды табу"},
  "Removal impact": {"ru":"Влияние удаления","kk":"Жоюдың әсері"},
  "Why is GID {gid} high priority?": {"ru":"Почему у узла GID {gid} высокий приоритет?","kk":"GID {gid} түйінінің басымдығы неге жоғары?"},
  "Show high-priority consolidators.": {"ru":"Покажи консолидаторов с высоким приоритетом.","kk":"Басымдығы жоғары жинақтаушыларды көрсет."},
  "What would happen if we removed GID {gid}?": {"ru":"Что изменится, если удалить узел GID {gid}?","kk":"GID {gid} түйінін жойсақ, не өзгереді?"},
  "Checking observed evidence": {"ru":"Проверка наблюдаемых данных","kk":"Бақыланған деректерді тексеру"},
  "Running bounded read-only tools": {"ru":"Проверки без изменения данных","kk":"Деректерді өзгертпей тексеру"},
  "Investigator request failed": {"ru":"Не удалось выполнить запрос","kk":"Сұрауды орындау мүмкін болмады"},
  "The AI investigator could not complete this request.": {"ru":"AI-помощник не смог выполнить запрос. Попробуйте ещё раз.","kk":"AI көмекші сұрауды орындай алмады. Қайталап көріңіз."},
  "Configuration": {"ru":"Настройка","kk":"Баптау"},
  "Grounded finding": {"ru":"Вывод на основе данных","kk":"Деректерге негізделген қорытынды"},
  "Close investigator result": {"ru":"Закрыть ответ помощника","kk":"Көмекшінің жауабын жабу"},
  "Referenced GIDs": {"ru":"Упомянутые GID","kk":"Аталған GID"},
  "Factual activity": {"ru":"Выполненные проверки","kk":"Орындалған тексерулер"},
  "Node card": {"ru":"Карточка узла","kk":"Түйін карточкасы"},
  "Common receivers": {"ru":"Общие получатели","kk":"Ортақ алушылар"},
  "Paths": {"ru":"Пути переводов","kk":"Аударым жолдары"},
  "Filter nodes": {"ru":"Отбор узлов","kk":"Түйіндерді іріктеу"},
  "Cluster summary": {"ru":"Сводка по кластеру","kk":"Кластер қорытындысы"},
  "Removal simulation": {"ru":"Моделирование удаления","kk":"Жоюды модельдеу"},
  "GID": {"ru":"GID","kk":"GID"},
  "GIDs": {"ru":"GID","kk":"GID"},
  "Maximum hops": {"ru":"Максимум переходов","kk":"Ең көп өту саны"},
  "Source GID": {"ru":"GID отправителя","kk":"Жіберуші GID"},
  "Target GID": {"ru":"GID получателя","kk":"Алушы GID"},
  "Role": {"ru":"Роль","kk":"Рөл"},
  "Minimum priority": {"ru":"Минимальный приоритет","kk":"Ең төмен басымдық"},
  "Minimum observed amount": {"ru":"Минимальная наблюдаемая сумма","kk":"Ең төмен бақыланған сома"},
  "Limit": {"ru":"Лимит","kk":"Шек"},
  "Question must contain at least 3 characters.": {"ru":"Введите минимум 3 символа.","kk":"Кемінде 3 таңба енгізіңіз."},
  "Investigation workspace": {
    "ru": "Рабочая область расследования",
    "kk": "Тергеу жұмыс кеңістігі"
  },
  "Dataset summary": {
    "ru": "Сводка по данным",
    "kk": "Деректер жиынтығының қорытындысы"
  },
  "Nodes": {
    "ru": "Узлы",
    "kk": "Түйіндер"
  },
  "Observed flow": {
    "ru": "Наблюдаемый поток",
    "kk": "Бақыланған ағын"
  },
  "Seeds": {
    "ru": "Исходные узлы",
    "kk": "Бастапқы түйіндер"
  },
  "Clusters": {
    "ru": "Кластеры",
    "kk": "Кластерлер"
  },
  "Depth-4 boundary": {
    "ru": "Граница глубины 4",
    "kk": "4-деңгей шекарасы"
  },
  "API unavailable": {
    "ru": "API недоступен",
    "kk": "API қолжетімсіз"
  },
  "Deterministic snapshot": {
    "ru": "Воспроизводимый срез",
    "kk": "Қайталанатын деректер кесіндісі"
  },
  "Investigation queue": {
    "ru": "Очередь расследования",
    "kk": "Тергеу кезегі"
  },
  "Priority nodes": {
    "ru": "Приоритетные узлы",
    "kk": "Басым түйіндер"
  },
  "Exact GID search": {
    "ru": "Поиск по точному GID",
    "kk": "Нақты GID бойынша іздеу"
  },
  "Search GID": {
    "ru": "Найти GID",
    "kk": "GID іздеу"
  },
  "Ranked by explainable priority": {
    "ru": "Рейтинг с обоснованием приоритета",
    "kk": "Негізделген басымдық рейтингі"
  },
  "Could not load queue": {
    "ru": "Не удалось загрузить очередь",
    "kk": "Кезекті жүктеу мүмкін болмады"
  },
  "Observed movement": {
    "ru": "Наблюдаемые переводы",
    "kk": "Бақыланған аударымдар"
  },
  "Money graph": {
    "ru": "Граф переводов",
    "kk": "Аударымдар графы"
  },
  "Graph role legend": {
    "ru": "Роли узлов графа",
    "kk": "Граф түйіндерінің рөлдері"
  },
  "Selected entity": {
    "ru": "Выбранный объект",
    "kk": "Таңдалған нысан"
  },
  "Investigation": {
    "ru": "Расследование",
    "kk": "Тергеу"
  },
  "Depth": {
    "ru": "Глубина",
    "kk": "Тереңдік"
  },
  "No node selected": {
    "ru": "Узел не выбран",
    "kk": "Түйін таңдалмаған"
  },
  "Select a queue row or search an exact GID.": {
    "ru": "Выберите узел в очереди или найдите его по точному GID.",
    "kk": "Кезектен түйінді таңдаңыз немесе нақты GID бойынша іздеңіз."
  },
  "Seed node": {
    "ru": "Исходный узел",
    "kk": "Бастапқы түйін"
  },
  "Non-seed": {
    "ru": "Не исходный",
    "kk": "Бастапқы емес"
  },
  "Priority": {
    "ru": "Приоритет",
    "kk": "Басымдық"
  },
  "Role confidence": {
    "ru": "Уверенность в роли",
    "kk": "Рөлге сенімділік"
  },
  "Observability limitation": {
    "ru": "Ограничение наблюдаемости",
    "kk": "Бақылау шектеуі"
  },
  "Investigation hypothesis": {
    "ru": "Гипотеза расследования",
    "kk": "Тергеу болжамы"
  },
  "Incoming": {
    "ru": "Входящие",
    "kk": "Кіріс"
  },
  "Outgoing": {
    "ru": "Исходящие",
    "kk": "Шығыс"
  },
  "Unique senders": {
    "ru": "Уникальные отправители",
    "kk": "Бірегей жіберушілер"
  },
  "Unique recipients": {
    "ru": "Уникальные получатели",
    "kk": "Бірегей алушылар"
  },
  "observed counterparties": {
    "ru": "наблюдаемые контрагенты",
    "kk": "бақыланған контрагенттер"
  },
  "Pass-through": {
    "ru": "Транзитная доля",
    "kk": "Транзиттік үлес"
  },
  "Near-time flow": {
    "ru": "Быстрые переводы",
    "kk": "Жедел аударымдар"
  },
  "Seed paths": {
    "ru": "Связанные исходные узлы",
    "kk": "Байланысты бастапқы түйіндер"
  },
  "Priority signals": {
    "ru": "Факторы приоритета",
    "kk": "Басымдық факторлары"
  },
  "Role strength": {
    "ru": "Выраженность роли",
    "kk": "Рөлдің айқындылығы"
  },
  "Money significance": {
    "ru": "Значимость сумм",
    "kk": "Сомалардың маңыздылығы"
  },
  "Structural importance": {
    "ru": "Структурная значимость",
    "kk": "Құрылымдық маңыздылық"
  },
  "Seed connectivity": {
    "ru": "Связь с исходными узлами",
    "kk": "Бастапқы түйіндермен байланыс"
  },
  "Anomaly evidence": {
    "ru": "Признаки аномалий",
    "kk": "Аномалия белгілері"
  },
  "Betweenness": {
    "ru": "Посредническая центральность",
    "kk": "Аралық орталықтылық"
  },
  "Cluster context": {
    "ru": "Контекст кластера",
    "kk": "Кластер контексі"
  },
  "Cluster": {
    "ru": "Кластер",
    "kk": "Кластер"
  },
  "Internal flow": {
    "ru": "Внутренний поток",
    "kk": "Ішкі ағын"
  },
  "Seed nodes": {
    "ru": "Исходные узлы",
    "kk": "Бастапқы түйіндер"
  },
  "Important GIDs": {
    "ru": "Ключевые GID",
    "kk": "Маңызды GID"
  },
  "Directed ego money graph": {
    "ru": "Направленный граф переводов выбранного узла",
    "kk": "Таңдалған түйіннің бағытталған аударымдар графы"
  },
  "Select an investigation": {
    "ru": "Выберите объект расследования",
    "kk": "Тергеу нысанын таңдаңыз"
  },
  "Choose a priority or search an exact GID to load its observed network.": {
    "ru": "Выберите приоритетный узел или найдите его по GID, чтобы загрузить наблюдаемые связи.",
    "kk": "Бақыланған байланыстарды жүктеу үшін басым түйінді таңдаңыз немесе GID бойынша іздеңіз."
  },
  "Loading observed network": {
    "ru": "Загрузка наблюдаемых связей",
    "kk": "Бақыланған байланыстар жүктелуде"
  },
  "Network unavailable": {
    "ru": "Граф недоступен",
    "kk": "Граф қолжетімсіз"
  },
  "bounded view": {
    "ru": "ограниченная выборка",
    "kk": "шектеулі көрініс"
  },
  "Scroll to zoom · drag to pan · hover an edge for flow · click a node to investigate": {
    "ru": "Колесо — масштаб · перетаскивание — перемещение · наведите на ребро для деталей · нажмите на узел для анализа",
    "kk": "Дөңгелек — масштаб · сүйреу — жылжыту · мәлімет үшін қырға меңзеңіз · талдау үшін түйінді басыңыз"
  },
  "Not available": {
    "ru": "Нет данных",
    "kk": "Деректер жоқ"
  },
  "Enter the exact numeric GID.": {
    "ru": "Введите точный числовой GID.",
    "kk": "Нақты сандық GID енгізіңіз."
  },
  "Unable to load this investigation.": {
    "ru": "Не удалось загрузить данные расследования. Проверьте подключение к API.",
    "kk": "Тергеу деректерін жүктеу мүмкін болмады. API байланысын тексеріңіз."
  },
  "Unable to load MoneyGraph.": {
    "ru": "Не удалось загрузить MoneyGraph. Проверьте подключение к API.",
    "kk": "MoneyGraph жүктеу мүмкін болмады. API байланысын тексеріңіз."
  },
  "Node not found": {
    "ru": "Узел с таким GID не найден",
    "kk": "Мұндай GID бар түйін табылмады"
  },
  "Language": {
    "ru": "Язык интерфейса",
    "kk": "Интерфейс тілі"
  },
  "coordinator": {
    "ru": "Координатор",
    "kk": "Үйлестіруші"
  },
  "consolidator": {
    "ru": "Консолидатор",
    "kk": "Жинақтаушы"
  },
  "distributor": {
    "ru": "Распределитель",
    "kk": "Үлестіруші"
  },
  "transit": {
    "ru": "Транзитный",
    "kk": "Транзиттік"
  },
  "terminal": {
    "ru": "Конечный",
    "kk": "Соңғы"
  },
  "peripheral": {
    "ru": "Периферийный",
    "kk": "Шеткі"
  }
} as const;

export type MessageKey = keyof typeof messages;

export function translate(locale: Locale, key: MessageKey): string {
  if (locale === "en") return key;
  return messages[key][locale];
}

export function formatCount(locale: Locale, value: number, kind: "nodes" | "transactions" | "neighbors"): string {
  const numberLocale = locale === "en" ? "en-US" : locale === "kk" && Intl.NumberFormat.supportedLocalesOf("kk-KZ").length ? "kk-KZ" : "ru-RU";
  const number = new Intl.NumberFormat(numberLocale).format(value);
  if (locale === "en") {
    const word = { nodes: "node", transactions: "transaction", neighbors: "nearby node" }[kind];
    return number + " " + word + (value === 1 ? "" : "s");
  }
  if (locale === "kk") return number + " " + { nodes: "түйін", transactions: "транзакция", neighbors: "көршілес түйін" }[kind];
  const forms = {
    nodes: { one: "узел", few: "узла", other: "узлов" },
    transactions: { one: "транзакция", few: "транзакции", other: "транзакций" },
    neighbors: { one: "соседний узел", few: "соседних узла", other: "соседних узлов" },
  }[kind];
  const rule = new Intl.PluralRules("ru").select(value);
  return number + " " + (rule === "one" ? forms.one : rule === "few" ? forms.few : forms.other);
}
