---
name: daily-parenting-page
description: Write and publish one pregnancy or parenting learning page a day to frizfealer/pregancy_knowledge_base on GitHub Pages, in Traditional Chinese, Simplified Chinese and English, with sourced claims, images and tags. Use for "today's parenting page", "make the daily page", the daily scheduled run, or when asked to add, fix or republish a page on that site.
---

# Daily parenting page

One page a day that teaches one thing about pregnancy or parenting, matched to where the
family is now, and publishes it to <https://frizfealer.github.io/pregancy_knowledge_base/>.

- Repo: `frizfealer/pregancy_knowledge_base`, served by GitHub Pages from `main` at `/`.
- `<skill>` below is this folder: `.claude/skills/daily-parenting-page/` inside the repo.
- `daily/pages.json` is the registry. `build_site.py` turns it into the index, README,
  page headers, review cards and Simplified Chinese. Never hand-edit those outputs.
- Read `references/page-guide.md` before writing and `references/sources-and-images.md`
  before researching. `references/stage-topics.md` lists what matters at each stage.

## Inputs

- **Due date**: from the request or the scheduled-task prompt. Never write it, the
  child's name or any family detail into the repo: the site is public.
- **Today**: the date in America/New_York.
- Gestational week = 40 − ceil(days until due date / 7), clamped to 4..42. After birth,
  use the baby's age in weeks or months instead.

## 1. Set up

1. Clone the repo with push access (in a cloud session: `add_repo` with `access: "push"`,
   then `git clone --depth 1`). Otherwise `git pull`.
2. `pip install --break-system-packages beautifulsoup4 opencc-python-reimplemented pillow`.
3. If `daily/pages.json` already has an entry dated today, stop: say which page it is.

## 2. Pick today's topic

1. Read `daily/pages.json`: the last ~14 entries' slugs, titles and tags.
2. Pick one topic that is useful **now or within the next 2–6 weeks** for this stage
   (see `references/stage-topics.md`), not already covered, and that balances the topic
   tags over the past week: `health`, `education`, `mind`, `growth`, `resources`.
3. Pick the kind: `learn` (a lesson, the default) or `curated` (about 1 in 4 days, and
   whenever a few excellent pages already explain the topic better than a summary could).
   Practical asks (NYC childcare, breast pumps, car seats, insurance) are `resources`.
4. Done when you can state the topic in one sentence and the one thing a reader should
   do or know after reading.

## 3. Research

Follow `references/sources-and-images.md`. In short:

- Before searching, write down the "why" questions from the page guide for each point
  you plan to make; search for their answers too, not only for the facts.
- Read the actual pages (WebFetch), not search snippets. Every factual sentence needs a
  source you fetched today. Record each source's title, publisher and reviewed date.
- Medical claims need a tier-1 source (CDC, NIH/MedlinePlus/NICHD/NIDDK, womenshealth.gov,
  FDA, WHO, AAP/HealthyChildren, NHS). When sources disagree, show both, don't pick one
  silently.
- Never invent a number, study, quote, price, product spec or link. If you can't verify
  something, leave it out.
- Paraphrase. At most one quote per source, under 15 words.

## 4. Images

At least one figure per page; aim for two. In order of preference: your own inline SVG
diagram when there's a real structure (a timeline, a sequence, a comparison), then an
openly licensed photo fetched with `<skill>/scripts/fetch_image.py` (Commons public
domain / CC0 / CC BY / CC BY-SA, or a U.S. government public-domain image). Otherwise link
to the image's page in the text. Never hotlink, never use an image you can't license.

## 5. Write the page

Copy `<skill>/assets/page-template.html` to `daily/YYYY-MM-DD-<slug>.html` and fill it,
following `references/page-guide.md`. The essentials:

- The title is a one-line hook that makes the reader want to open it. No name, no due
  date, no week number in the title; the stage goes in tags (`early`, `w13`, ...).
- Order: guess first → the plain-language version → why → details → do today → cards →
  review (auto) → sources. Simple before principle before detail.
- Keep asking "why" (see "Keep asking why" in the page guide): why do it, why now, the
  reader's obvious objection, why this way, how much it helps. Research those answers in
  step 3 like any other claim; they are what makes the Why section convincing. At least
  one card should test a "why".
- Write zh-Hant and en for every block, as `data-l` siblings. Never write zh-Hans.
- Put factual paragraphs and list items inside `.claims`; each one ends with a
  `<sup><a href="#sN">N</a></sup>` citation.
- 3–5 cards: questions whose answers are worth remembering a week later.

Then add the entry to `daily/pages.json` (date, slug, file, title, summary, tags, the
source URLs and the same cards as the page). Tags: at least one topic tag, the stage tag
or tags, the week tag `wN` while pregnant, and one kind tag. New tags go into `TAGS` in
`build_site.py` first, with zh-Hant and English labels.

## 6. Build and check

1. From the repo root: `python3 <skill>/scripts/build_site.py`. Fix everything it reports;
   it writes nothing until the pages pass.
2. Verify each claim: for every citation, re-read the cited page and confirm it says
   what the sentence says (numbers, weeks, units, conditions). Fix or drop anything that
   doesn't match. This step is not optional.
3. Render the page at 1100px and 390px (Playwright with `/usr/bin/google-chrome` if
   present) in all three languages; check no horizontal page scroll, figures legible,
   no console errors.
4. Check every external link resolves (WebFetch or a HEAD request).

## 7. Publish

1. `git add -A && git status`, then commit `Add daily page YYYY-MM-DD: <slug>` and push to
   `main` (`git fetch origin main` and rebase first if the push is rejected).
2. Wait a minute, then WebFetch the live page URL
   `https://frizfealer.github.io/pregancy_knowledge_base/daily/<file>.html` until it shows
   the new title (Pages usually updates within a few minutes).
3. Report: the hook title, the page URL, the tags, and one line on what it teaches.

## Fixing or republishing a page

Edit the page or its `pages.json` entry, rerun the build, recheck the changed claims,
commit `Update daily page YYYY-MM-DD: <what>`, push.
