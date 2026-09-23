const { test } = require("node:test");
const assert = require("node:assert/strict");
const { formatCount, messages, translate } = require("../src/lib/translations.ts");
const { translateEvidence, evidenceTemplates } = require("../src/lib/translate-evidence.ts");

test("Russian counts use the correct plural forms; Kazakh nouns stay unchanged", () => {
  for (const [value, word] of [[1, "узел"], [2, "узла"], [5, "узлов"], [11, "узлов"], [21, "узел"], [24, "узла"]]) {
    assert.equal(formatCount("ru", value, "nodes"), value + " " + word);
  }
  assert.equal(formatCount("ru", 1, "transactions"), "1 транзакция");
  assert.equal(formatCount("ru", 22, "transactions"), "22 транзакции");
  assert.equal(formatCount("kk", 22, "transactions"), "22 транзакция");
});

test("All three languages cover every UI message", () => {
  for (const [key, entry] of Object.entries(messages)) {
    assert.equal(translate("en", key), key);
    assert.ok(entry.ru.trim());
    assert.ok(entry.kk.trim());
  }
});

test("English counts and evidence keep their original meaning", () => {
  assert.equal(formatCount("en", 1, "transactions"), "1 transaction");
  assert.equal(formatCount("en", 2, "transactions"), "2 transactions");
  assert.equal(formatCount("en", 1200, "nodes"), "1,200 nodes");
  assert.equal(formatCount("en", 1, "neighbors"), "1 nearby node");
  assert.equal(formatCount("en", 3, "neighbors"), "3 nearby nodes");
  for (const [source] of evidenceTemplates) assert.equal(translateEvidence("en", source), source);
});

test("Investigator suggestions are localized and preserve the exact selected GID", () => {
  const gid = "100000004156082100";
  for (const key of ["Why is GID {gid} high priority?", "What would happen if we removed GID {gid}?"]) {
    for (const locale of ["en", "ru", "kk"]) {
      const prompt = translate(locale, key).replace("{gid}", gid);
      assert.ok(prompt.includes(gid));
      assert.ok(!prompt.includes("{gid}"));
      if (locale !== "en") assert.notEqual(translate(locale, key), key);
    }
  }
});

test("Every known backend template translates without dropping numeric evidence", () => {
  for (const [source] of evidenceTemplates) {
    const input = source.replace(/\{(\d+)\}/g, (_, index) => String(800 + Number(index)));
    for (const locale of ["ru", "kk"]) {
      const result = translateEvidence(locale, input);
      assert.notEqual(result, input);
      for (const value of input.match(/\d+/g) || []) assert.ok(result.includes(value), value + " was lost");
    }
  }
});

test("Seed caveat is retained and unfamiliar evidence is left intact", () => {
  const input = "Distribution signs: 12 recipients, KZT2.3m out in 29 tx; investigation hypothesis. Seed inflow incomplete.";
  assert.match(translateEvidence("ru", input), /неполны/);
  assert.match(translateEvidence("kk", input), /толық емес/);
  for (const locale of ["ru", "kk"]) {
    assert.ok(translateEvidence(locale, input).includes("KZT2.3m"));
    assert.equal(translateEvidence(locale, "New evidence from the server"), "New evidence from the server");
  }
});
