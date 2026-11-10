# Page guide

The reader is a busy parent-to-be reading on a phone. They want one useful thing per day,
explained so it sticks, with nothing they have to take on faith.

## The title is the hook

One line, concrete, a little surprising or immediately useful. It should make someone tap.

- Good: 「孕早期快結束了：先把這 4 件事排進行事曆」, 「寶寶哭不一定是餓：先看這 3 個訊號」,
  「吸乳器保險可能幫你付：先問這 2 個問題」
- Bad: 「第 13 週須知」 (says nothing), 「關於妊娠糖尿病」 (a topic, not a point),
  anything with the due date, a name or the week number.

The summary under it states the takeaway in one or two sentences.

## Order: simple → why → detail

1. **先猜一猜 / Guess first** — one question in a closed `<details>`, answered with a
   citation. Pick something people get wrong or never thought about.
2. **第一步・白話版 / The short version** — what to know, in plain words, with the main
   figure. A reader who stops here should still have the point.
3. **第二步・原理 / Why** — the mechanism behind it. Short `h3` per idea.
4. **第三步・細節 / Details** — the table, numbers, edge cases, where sources disagree,
   when to call the doctor.
5. **今天就能做 / Do today** — 2–4 concrete actions. Advice, so no citations needed (no
   `.claims` class).
6. **自我測驗 / Check yourself** — 3–5 flashcards, the same ones as in `pages.json`.
7. `<section id="review">` — left empty; the build fills it with cards from 1, 3, 7 and
   14 days earlier.
8. **來源 / Sources** — `<ol class="sources">`, items `id="s1"`… with title, publisher,
   reviewed date.

Define every term the first time it appears (「胰島素阻抗」（身體細胞對胰島素的反應變差）).
State numbers with units and what they count. Keep paragraphs to 2–3 sentences.

## Curated pages

When a few excellent pages already teach the topic well, the page mostly points to them:

- Same header, guess-first question and cards.
- A `<ul class="picks">` of 3–5 links. For each: the title as a link, the publisher in
  `.src`, two sentences on what it covers and why it's worth the click, written in your
  own words. These summaries are claims: put the list in `.claims` and cite the linked
  page itself.
- A short "do today" callout.

## Languages

Write each block twice, Traditional Chinese then English, as siblings:

```html
<p data-l="zh-Hant">…<sup><a href="#s1">1</a></sup></p>
<p data-l="en">…<sup><a href="#s1">1</a></sup></p>
```

Inline: `<h2><span data-l="zh-Hant">…</span><span data-l="en">…</span></h2>`. Whole lists
and tables can be duplicated per language. Don't nest `data-l` blocks. Never write
`zh-Hans`: the build converts zh-Hant with OpenCC (tw2sp) plus the `MAINLAND` term list in
`build_site.py`; when you spot a Taiwan-only term in the Simplified output, add a pair there.

English is a real translation for an English reader, not a word-for-word gloss.

## Figures

- SVG diagram: `<figure class="flow-diagram"><svg viewBox="0 0 1000 H" role="img"
  aria-label="…">`, text 14–15px, colors only from CSS variables (`var(--accent)`,
  `var(--green)`, `var(--gold)`, `var(--muted)`, `var(--line)`, `var(--accent-soft)`,
  `var(--green-soft)`), labels as `<text data-l="zh-Hant">` / `<text data-l="en">` pairs.
  Draw only real structure: a timeline, a sequence, a comparison, a cycle. On phones the
  diagram scrolls sideways at full size.
- Photos: `<figure><img src="img/…" alt="…" width height loading="lazy"><figcaption>…
  <span class="credit">author · license link · source link</span></figcaption></figure>`,
  using the credit line `fetch_image.py` prints.

## Accessibility and tone

- Calm, warm, plain. No fear-mongering, no exclamation marks, no emoji.
- Never diagnose; say when to call the doctor and cite it.
- Every page ends with the disclaimer that it doesn't replace the OB's or pediatrician's
  advice.
