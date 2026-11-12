#!/usr/bin/env python3
"""Validates the daily pages and regenerates everything derived from daily/pages.json.

daily/pages.json is the source of truth: one entry per daily page (date, slug, file,
title, summary, tags, cards) plus the long-form guides at the repo root. From it this
script, run from the repo root:

  1. checks every daily page (citations resolve, every source is cited, every claim
     paragraph carries a citation, images are local files with a credit, tags are
     known, Traditional Chinese and English blocks pair up);
  2. fills each daily page's header (date, title, summary, tags) and its review
     section (one card each from the pages 1, 3, 7 and 14 days earlier);
  3. adds Simplified Chinese: every data-l="zh-Hant" block gets a converted
     data-l="zh-Hans" sibling (OpenCC tw2sp, Taiwan phrasing to mainland phrasing),
     regenerated on every run, so only zh-Hant and en are ever written by hand;
  4. regenerates index.html (tag filter, newest first) and README.md.

It writes nothing when a check fails.

    python3 .claude/skills/daily-parenting-page/scripts/build_site.py [--check-only]

Needs: pip install beautifulsoup4 opencc-python-reimplemented
"""

import argparse
import copy
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment
import opencc

SITE_URL = "https://frizfealer.github.io/pregancy_knowledge_base/"
REPO_URL = "https://github.com/frizfealer/pregancy_knowledge_base"
LANGS = ("zh-Hant", "zh-Hans", "en")
REVIEW_OFFSETS = (1, 3, 7, 14)

# Tag vocabulary. group drives the chip color: topic, stage or kind.
TAGS = {
    "health": ("topic", "健康", "Health"),
    "education": ("topic", "教育", "Education"),
    "mind": ("topic", "心靈", "Mind"),
    "growth": ("topic", "成長", "Growth"),
    "resources": ("topic", "實用資源", "Resources"),
    "early": ("stage", "孕早期", "First trimester"),
    "mid": ("stage", "孕中期", "Second trimester"),
    "late": ("stage", "孕晚期", "Third trimester"),
    "newborn": ("stage", "新生兒（0–3 個月）", "Newborn (0–3 mo)"),
    "infant": ("stage", "嬰兒（3–12 個月）", "Infant (3–12 mo)"),
    "toddler": ("stage", "幼兒（1–3 歲）", "Toddler (1–3 y)"),
    "learn": ("kind", "學習", "Lesson"),
    "curated": ("kind", "精選連結", "Curated links"),
}
WEEK_TAG = re.compile(r"w([1-9]|[1-3][0-9]|4[0-2])$")

T2S = opencc.OpenCC("tw2sp")
# Taiwan terms OpenCC leaves as-is, mapped to mainland usage. Add pairs as new ones show up.
MAINLAND = {
    "行事历": "日历", "超音波": "超声波", "药局": "药房", "公克": "克", "公分": "厘米",
    "英吋": "英寸", "筛检": "筛查", "荷尔蒙": "激素", "胰岛素阻抗": "胰岛素抵抗",
    "忧郁": "抑郁", "咨商": "心理咨询", "信赖区间": "置信区间", "社经": "社会经济",
    "（含国语、粤语、台语）": "（含普通话、粤语、闽南语）",
    "「": "“", "」": "”",
}


def hans(text):
    out = T2S.convert(text)
    for tw, cn in MAINLAND.items():
        out = out.replace(tw, cn)
    return out


def tri(d):
    """Returns {zh-Hant, zh-Hans, en} from a {zh-Hant, en} dict, converting zh-Hans."""
    return {"zh-Hant": d["zh-Hant"], "zh-Hans": hans(d["zh-Hant"]), "en": d["en"]}


def tag_label(tag):
    """Returns (group, {lang: label}) for a known tag id."""
    m = WEEK_TAG.fullmatch(tag)
    if m:
        n = m[1]
        return "stage", tri({"zh-Hant": f"孕 {n} 週", "en": f"Week {n}"})
    group, zh, en = TAGS[tag]
    return group, tri({"zh-Hant": zh, "en": en})


def spans(d, tag="span", hans=True):
    """Returns one element per language, for a {lang: text} dict.

    hans=False leaves out zh-Hans, for page content that add_hans() converts later.
    """
    langs = LANGS if hans else ("zh-Hant", "en")
    return "".join(f'<{tag} data-l="{l}">{html.escape(d[l])}</{tag}>' for l in langs)


def tags_html(tags, hans=True):
    items = ""
    for t in tags:
        group, label = tag_label(t)
        items += f'<li class="tag t-{group}">{spans(label, hans=hans)}</li>'
    return f'<ul class="tags">{items}</ul>'


# ---------- checks ----------

def check_registry(reg, root):
    errors = []
    slugs = set()
    for p in reg["pages"]:
        where = f'pages.json entry {p.get("slug", "?")}'
        for key in ("date", "slug", "file", "title", "summary", "tags", "cards"):
            if key not in p:
                errors.append(f"{where}: missing {key}")
        if errors:
            continue
        try:
            dt.date.fromisoformat(p["date"])
        except ValueError:
            errors.append(f"{where}: date {p['date']!r} isn't YYYY-MM-DD")
        if p["slug"] in slugs:
            errors.append(f"{where}: slug used twice")
        slugs.add(p["slug"])
        if not (root / p["file"]).is_file():
            errors.append(f"{where}: file {p['file']} missing")
        for key in ("title", "summary"):
            if not all(p[key].get(l) for l in ("zh-Hant", "en")):
                errors.append(f"{where}: {key} needs zh-Hant and en")
        for t in p["tags"]:
            if t not in TAGS and not WEEK_TAG.fullmatch(t):
                errors.append(f"{where}: unknown tag {t!r} (add it to TAGS in build_site.py first)")
        if not any(TAGS.get(t, ("",))[0] == "topic" for t in p["tags"]):
            errors.append(f"{where}: needs at least one topic tag")
        if not any(TAGS.get(t, ("",))[0] == "kind" for t in p["tags"]):
            errors.append(f"{where}: needs a kind tag (learn or curated)")
        if not p["cards"]:
            errors.append(f"{where}: needs at least one card")
        for i, c in enumerate(p["cards"], 1):
            for side in ("q", "a"):
                if not all(c.get(side, {}).get(l) for l in ("zh-Hant", "en")):
                    errors.append(f"{where}: card {i} {side} needs zh-Hant and en")
    for g in reg.get("guides", []):
        if not (root / g["file"]).is_file():
            errors.append(f"guide {g['file']} missing")
    return errors


def check_page(soup, rel, root):
    errors = []
    if not soup.find(id="head"):
        errors.append('no <header id="head"> (the build fills it)')
    if not soup.find("section", id="review"):
        errors.append('no <section id="review"> (the build fills it)')
    sources = soup.select("ol.sources > li")
    if not sources:
        errors.append("no <ol class=\"sources\"> list")
    ids = set()
    for li in sources:
        a = li.find("a", href=True)
        if not li.get("id") or not a or not re.match(r"https?://", a["href"]):
            errors.append(f"source item needs an id and an http(s) link: {li.get_text(' ', strip=True)[:80]}")
        ids.add(li.get("id"))
    cited = set()
    for a in soup.select('a[href^="#"]'):
        target = a["href"][1:]
        if target.startswith("s") and target[1:].isdigit():
            cited.add(target)
            if target not in ids:
                errors.append(f"citation #{target} has no source")
    for sid in ids - cited:
        errors.append(f"source #{sid} is never cited")
    # Every paragraph or list item in a claims block carries a citation.
    for block in soup.select(".claims"):
        for el in block.find_all(["p", "li"]):
            if el.find_parent(class_="nocite") or "nocite" in (el.get("class") or []):
                continue
            if el.find(["p", "li"]):  # judged at the innermost level
                continue
            if not el.get_text(strip=True):
                continue
            if not el.find("sup"):
                errors.append(f"uncited claim: {el.get_text(' ', strip=True)[:70]}")
    # Images: local file, inside a figure with a credit.
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if re.match(r"(https?:)?//", src):
            errors.append(f"image {src} is hotlinked; download a public-domain or CC copy into daily/img/")
            continue
        if not (root / rel).parent.joinpath(src).resolve().is_file():
            errors.append(f"image {src} missing")
        fig = img.find_parent("figure")
        if not fig or not fig.select_one("figcaption .credit"):
            errors.append(f"image {src} needs a <figure> with a figcaption .credit (author, license, link)")
        if not img.get("alt"):
            errors.append(f"image {src} needs alt text")
    for svg in soup.find_all("svg"):
        if not (svg.get("aria-label") or svg.find("title")):
            errors.append("an <svg> needs aria-label or <title>")
    if soup.find(attrs={"data-l": "zh-Hans", "data-auto": False}):
        errors.append("write only zh-Hant and en; zh-Hans is generated")
    n_hant = len(soup.find_all(attrs={"data-l": "zh-Hant"}))
    n_en = len(soup.find_all(attrs={"data-l": "en"}))
    if n_hant != n_en:
        errors.append(f"{n_hant} zh-Hant blocks but {n_en} en blocks; each block needs its pair")
    for el in soup.find_all(attrs={"data-l": True}):
        if el.find_parent(attrs={"data-l": True}):
            errors.append("data-l blocks must not nest")
            break
    return errors


# ---------- page rendering ----------

def head_html(p):
    date = dt.date.fromisoformat(p["date"])
    title, summary = tri(p["title"]), tri(p["summary"])
    return (f'<p class="date">{date:%Y-%m-%d}</p>'
            f'<h1>{spans(title, hans=False)}</h1>'
            f'<p class="prose">{spans(summary, hans=False)}</p>'
            f'{tags_html(p["tags"], hans=False)}')


def review_html(p, by_date):
    date = dt.date.fromisoformat(p["date"])
    heading = tri({"zh-Hant": "複習：之前學過的", "en": "Review: from earlier days"})
    out = f'<h2>{spans(heading, hans=False)}</h2>'
    cards = 0
    for off in REVIEW_OFFSETS:
        old = by_date.get(date - dt.timedelta(days=off))
        if not old:
            continue
        card = old["cards"][date.toordinal() % len(old["cards"])]
        q, a = tri(card["q"]), tri(card["a"])
        ago = tri({"zh-Hant": f"{off} 天前", "en": f"{off} day{'s' if off > 1 else ''} ago"})
        link = Path(old["file"]).name
        out += (f'<details><summary class="card-q">{spans(q, hans=False)} '
                f'<span class="review-from">· <a href="{html.escape(link)}">{spans(ago, hans=False)}</a></span></summary>'
                f'<p>{spans(a, hans=False)}</p></details>')
        cards += 1
    if not cards:
        note = tri({"zh-Hant": "這裡之後會出現 1、3、7、14 天前各一張複習卡，隔越久再考一次，記得越牢。",
                    "en": "From tomorrow, one card each from 1, 3, 7 and 14 days ago shows up here. Spacing reviews out makes them stick."})
        out += f'<p>{spans(note, hans=False)}</p>'
    return out


def add_hans(soup):
    for el in soup.find_all(attrs={"data-auto": "hans"}):
        el.decompose()
    for el in soup.find_all(attrs={"data-l": "zh-Hant"}):
        twin = copy.copy(el)
        twin["data-l"] = "zh-Hans"
        twin["data-auto"] = "hans"
        if twin.get("id"):
            del twin["id"]
        for s in twin.find_all(string=True):
            if not isinstance(s, Comment):
                s.replace_with(hans(str(s)))
        for t in [twin] + twin.find_all(True):
            for attr in ("alt", "title", "aria-label"):
                if t.get(attr):
                    t[attr] = hans(t[attr])
            if t.get("id") and t is not twin:
                t["id"] = t["id"] + "-hans"
        el.insert_after(twin)


def set_meta(soup, p):
    title = tri(p["title"])
    head = soup.head
    for m in head.find_all("meta", attrs={"name": re.compile("^title-")}):
        m.decompose()
    for l in LANGS:
        m = soup.new_tag("meta", attrs={"name": f"title-{l}", "content": title[l]})
        head.append(m)
    if head.title:
        head.title.string = title["zh-Hant"]
    desc = head.find("meta", attrs={"name": "description"})
    if desc:
        desc["content"] = p["summary"]["zh-Hant"]


def fill(soup, el_id, inner):
    el = soup.find(id=el_id)
    el.clear()
    el.append(BeautifulSoup(inner, "html.parser"))


# ---------- index and README ----------

def render_index(reg):
    pages = sorted(reg["pages"], key=lambda p: (p["date"], p["slug"]), reverse=True)
    used = []
    for p in pages + reg.get("guides", []):
        for t in p["tags"]:
            if t not in used:
                used.append(t)
    order = {"topic": 0, "stage": 1, "kind": 2}
    def sort_key(t):
        group = tag_label(t)[0]
        week = int(WEEK_TAG.fullmatch(t)[1]) if WEEK_TAG.fullmatch(t) else 0
        return (order[group], week, list(TAGS).index(t) if t in TAGS else 99)
    chips = f'<button class="chip" type="button" data-tag="all" aria-pressed="true">{spans(tri({"zh-Hant": "全部", "en": "All"}))}</button>'
    for t in sorted(used, key=sort_key):
        chips += f'<button class="chip" type="button" data-tag="{t}" aria-pressed="false">{spans(tag_label(t)[1])}</button>'

    def entry(p, href, date=""):
        return (f'<li><a class="entry" href="{html.escape(href)}" data-tags="{" ".join(p["tags"])}">'
                f'{f"<span class=date>{date}</span>" if date else ""}'
                f'<div class="title">{spans(tri(p["title"]))}</div>'
                f'<p>{spans(tri(p["summary"]))}</p>{tags_html(p["tags"])}</a></li>')

    daily = "".join(entry(p, p["file"], p["date"]) for p in pages)
    guides = "".join(entry(g, g["file"]) for g in reg.get("guides", []))
    title = tri({"zh-Hant": "孕期與育兒，每天學一點", "en": "Pregnancy and parenting, a little every day"})
    intro = tri({"zh-Hant": "每天一頁：先講白話重點，再講原理和細節。每個說法都附來源，資料來自 ACOG、CDC、AAP、NIH 等公開指引。",
                 "en": "One page a day: the plain-language point first, then the why and the details. Every claim links its source: ACOG, CDC, AAP, NIH and other public guidance."})
    h_daily = tri({"zh-Hant": "每日一頁", "en": "Daily pages"})
    h_guides = tri({"zh-Hant": "長篇指南", "en": "In-depth guides"})
    guides_note = tri({"zh-Hant": "（目前只有繁體中文）", "en": "(Traditional Chinese only for now)"})
    disclaimer = tri({"zh-Hant": "本站整理公開指引，不能取代產檢醫師或小兒科醫師的個別建議。",
                      "en": "These pages summarize public guidance and don't replace advice from your own OB or pediatrician."})
    meta = "".join(f'<meta name="title-{l}" content="{html.escape(title[l])}">' for l in LANGS)
    return f"""<!doctype html>
<!-- Generated by build_site.py from daily/pages.json; edit that and rerun. -->
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title["zh-Hant"])}</title>{meta}
<meta name="description" content="{html.escape(intro["zh-Hant"])}">
<link rel="stylesheet" href="assets/daily.css">
<noscript><style>.langs, .filters {{ display: none; }}</style></noscript>
</head><body data-lang="zh-Hant"><div class="wrap">
<nav class="topbar"><span class="home">{spans(tri({"zh-Hant": "孕期知識庫", "en": "Pregnancy notes"}))}</span>
<div class="langs" role="group" aria-label="Language"><button type="button" data-set-lang="zh-Hant" aria-pressed="true">繁</button><button type="button" data-set-lang="zh-Hans" aria-pressed="false">简</button><button type="button" data-set-lang="en" aria-pressed="false">EN</button></div></nav>
<header class="head"><h1>{spans(title)}</h1><p class="intro">{spans(intro)}</p></header>
<div class="filters" role="group" aria-label="Filter by tag">{chips}</div>
<h2>{spans(h_daily)}</h2>
<ul class="list">{daily}</ul>
<h2>{spans(h_guides)} <small class="intro">{spans(guides_note)}</small></h2>
<ul class="list">{guides}</ul>
<p class="disclaimer">{spans(disclaimer)}</p>
</div><script src="assets/daily.js"></script></body></html>
"""


def render_readme(reg):
    pages = sorted(reg["pages"], key=lambda p: (p["date"], p["slug"]), reverse=True)
    def label(t):
        return tag_label(t)[1]["zh-Hant"]
    rows = "".join(f'| {p["date"]} | [{p["title"]["zh-Hant"]}]({p["file"]}) | {", ".join(label(t) for t in p["tags"])} |\n'
                   for p in pages)
    guides = "".join(f'| [{g["title"]["zh-Hant"]}]({g["file"]}) | {g["summary"]["zh-Hant"]} |\n' for g in reg.get("guides", []))
    return f"""# pregancy_knowledge_base

<!-- Generated by .claude/skills/daily-parenting-page/scripts/build_site.py from daily/pages.json; edit that and rerun. -->

孕期與育兒的每日學習頁，繁中、简中、English。資料來自 ACOG、CDC、AAP、NIH 等公開指引，每個說法都附來源。

📖 **線上閱讀：** {SITE_URL}

## 每日一頁

| 日期 | 標題 | 標籤 |
| --- | --- | --- |
{rows}
## 長篇指南

| 指南 | 內容 |
| --- | --- |
{guides}
## 怎麼產生的

每頁由 Claude 依 `.claude/skills/daily-parenting-page/` 的規則撰寫，`daily/pages.json` 是索引的來源；
改完執行 `python3 .claude/skills/daily-parenting-page/scripts/build_site.py` 重新產生首頁、簡中與複習卡。

> 本文整理自公開指引，不能取代產檢醫師的個別建議。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true", help="validate without writing")
    a = ap.parse_args()
    root = Path.cwd()
    reg_path = root / "daily" / "pages.json"
    if not reg_path.is_file():
        sys.exit("run from the repo root; daily/pages.json not found")
    reg = json.loads(reg_path.read_text())

    errors = check_registry(reg, root)
    if errors:
        sys.exit("pages.json:\n  " + "\n  ".join(errors))
    by_date = {}
    for p in sorted(reg["pages"], key=lambda p: p["slug"]):
        by_date.setdefault(dt.date.fromisoformat(p["date"]), p)

    outputs = {}
    all_errors = []
    for p in reg["pages"]:
        path = root / p["file"]
        soup = BeautifulSoup(path.read_text(), "html.parser")
        errs = check_page(soup, p["file"], root)
        all_errors += [f"{p['file']}: {e}" for e in errs]
        if errs:
            continue
        fill(soup, "head", head_html(p))
        fill(soup, "review", review_html(p, by_date))
        set_meta(soup, p)
        add_hans(soup)
        outputs[path] = str(soup)
    if all_errors:
        sys.exit("Fix these, nothing was written:\n  " + "\n  ".join(all_errors))
    if a.check_only:
        print(f"ok: {len(reg['pages'])} pages pass")
        return
    for path, text in outputs.items():
        path.write_text(text)
    (root / "index.html").write_text(render_index(reg))
    (root / "README.md").write_text(render_readme(reg))
    print(f"built {len(outputs)} daily pages, index.html and README.md")


if __name__ == "__main__":
    main()
