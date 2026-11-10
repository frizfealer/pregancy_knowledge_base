// Language switch and index tag filter. Everything works without JS: zh-Hant shows and all entries list.
(function () {
  var LANGS = ["zh-Hant", "zh-Hans", "en"];
  var HTML_LANG = { "zh-Hant": "zh-Hant", "zh-Hans": "zh-Hans", "en": "en" };

  function stored() {
    try { return localStorage.getItem("lang"); } catch (e) { return null; }
  }
  function store(l) {
    try { localStorage.setItem("lang", l); } catch (e) { /* storage blocked: choice lasts this visit */ }
  }
  function setLang(l) {
    if (LANGS.indexOf(l) < 0) return;
    document.body.setAttribute("data-lang", l);
    document.documentElement.setAttribute("lang", HTML_LANG[l]);
    document.querySelectorAll(".langs button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-set-lang") === l));
    });
    var t = document.querySelector('meta[name="title-' + l + '"]');
    if (t) document.title = t.getAttribute("content");
  }

  var fromUrl = new URLSearchParams(location.search).get("lang");
  setLang(fromUrl || stored() || "zh-Hant");
  document.querySelectorAll(".langs button").forEach(function (b) {
    b.addEventListener("click", function () {
      var l = b.getAttribute("data-set-lang");
      setLang(l);
      store(l);
    });
  });

  // Index: one active tag at a time; "all" clears it.
  var chips = document.querySelectorAll(".filters .chip");
  if (chips.length) {
    var filter = function (tag) {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.getAttribute("data-tag") === tag)); });
      document.querySelectorAll(".entry").forEach(function (e) {
        var tags = (e.getAttribute("data-tags") || "").split(" ");
        e.parentElement.hidden = !(tag === "all" || tags.indexOf(tag) >= 0);
      });
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function () { filter(c.getAttribute("data-tag")); });
    });
    filter("all");
  }
})();
