# Interface localization

[Русский](frontend-localization.md) · [Қазақша](frontend-localization.kk.md) · **English**

The interface supports Russian (the default), Kazakh, and English.
The “Русский / Қазақша / English” switcher is in the top bar.
The selection is saved in localStorage under `moneygraph.locale`; if storage is unavailable,
switching continues to work until the page is reloaded.
Changing the language does not reload data or reset the selected node.

Interface text and role labels are defined in
`frontend/src/lib/translations.ts`. English text is stored in the dictionary keys;
API explanations are shown in their original form for English.
Language context, amount and percentage formatting, and the switcher are in
`frontend/src/components/language-provider.tsx`.
The document's `lang` attribute updates on switching; the browser tab title is MoneyGraph.

API explanations are translated using complete known templates in
`frontend/src/lib/translate-evidence.ts`. Numeric values and caveats are preserved.
When the backend adds a template, add it to that file:
unknown explanations are shown in their original form to avoid distorting their meaning.
API responses and CSV files are not modified.

Checks from the repository root (Node.js 24):

```powershell
node --test frontend/tests/localization.test.cjs
cd frontend
npm.cmd run build
```

Manual check: start the backend and frontend, switch language, select a node,
then switch again and confirm that the selected node stays the same. Reload the page
and check language persistence. Check search, errors, and narrow screens.

## AI investigator

The panel, suggested questions, tool labels, and parameter labels are translated into
all three languages. A suggested question is sent in the current interface language.
The `POST /api/investigator` request contains `question`, `locale` (`ru`, `kk`, or `en`),
and `selected_gid`. The selected GID is sent separately and does not consume the question's text limit.
Older clients that omit `locale` retain English.

The backend adds a language instruction to the shared grounding rules for every model call.
The instruction requires translating explanations and caveats while preserving identifiers
and numeric facts. Messages for missing configuration, errors, empty answers, and
unconfirmed GIDs are also localized.
The instruction dictionary is in `backend/app/agent/localization.py`.

On language change, the panel clears the current question and answer, cancels waiting for the
previous response, and shows new suggestions. This does not automatically trigger another
paid request. Ask again to receive an answer in a different language.

Backend check without external AI requests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
```

The language policy uses the Responses API `instructions` parameter:
https://developers.openai.com/api/docs/guides/text

[MoneyGraph README](../README.en.md)
