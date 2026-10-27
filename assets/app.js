/* VitaPals — search, food finder, vitamin check, myth of the week. No tracking, nothing sent anywhere. */
(function () {
  "use strict";
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var cache = {};
  function load(path) {
    if (!cache[path]) cache[path] = fetch(path).then(function (r) { return r.json(); });
    return cache[path];
  }
  var norm = function (s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };

  /* ---------- Header height, for the sticky "on this page" chips ---------- */
  var hdr = document.querySelector(".site-header");
  var setH = function () { if (hdr) document.documentElement.style.setProperty("--hh", hdr.offsetHeight + "px"); };
  setH(); window.addEventListener("resize", setH);

  /* ---------- Keep the active tab visible ---------- */
  document.querySelectorAll(".strip .on").forEach(function (a) {
    var s = a.parentNode; s.scrollLeft = a.offsetLeft - s.clientWidth / 2 + a.clientWidth / 2;
  });

  /* ---------- Site search ---------- */
  var STOP = { a: 1, an: 1, the: 1, i: 1, my: 1, is: 1, are: 1, do: 1, does: 1, of: 1, "in": 1, "for": 1, to: 1, and: 1, or: 1, what: 1, which: 1, can: 1, should: 1, me: 1, much: 0 };
  var SYN = { dose: "need", dosage: "need", amount: "need", fatigue: "tired", exhausted: "tired", energy: "tired", veg: "vegetarian", veggie: "vegetarian", pregnant: "pregnancy", hormones: "hormonal", hormone: "hormonal", thyroid: "thyroid", folic: "folate", sun: "sunshine", sunlight: "sunshine" };
  var POPULAR = [["Vitamin B12", "/vitamin-b12/"], ["Vitamin D", "/vitamin-d/"], ["Always tired?", "/guides/tired/"], ["Food finder", "/tools/food-finder/"]];
  var words = function (s) { return norm(s).split(/[^a-z0-9-]+/).filter(Boolean); };
  // A term matches a word if it is the word (short terms like "d" or "b12") or starts it (longer terms like "veget").
  var hit = function (list, w) { for (var i = 0; i < list.length; i++) { var x = list[i]; if (x === w || (w.length >= 3 && x.indexOf(w) === 0)) return true; } return false; };
  document.querySelectorAll("[data-search]").forEach(function (box) {
    var input = box.querySelector("input"), out = box.querySelector(".results");
    var run = function () {
      var raw = input.value.trim();
      if (raw.length < 2) { out.innerHTML = ""; return; }
      Promise.all([load("/assets/search.json"), load("/assets/foods.json")]).then(function (res) {
        var idx = res[0], foods = res[1], hits = [];
        var terms = words(raw).filter(function (w) { return !STOP[w]; });
        if (terms.length > 1) terms = terms.filter(function (w) { return w !== "vitamin" && w !== "vitamins"; });
        if (!terms.length) { out.innerHTML = ""; return; }
        terms = terms.map(function (w) { return SYN[w] || w; });
        var need = terms.length === 1 ? 1 : Math.ceil(terms.length / 2);
        idx.forEach(function (it) {
          var t = words(it.t), x = words(it.x || ""), s = words(it.s || ""), score = 0, matched = 0;
          terms.forEach(function (w) {
            if (hit(t, w)) { score += 5; matched++; } else if (hit(x, w)) { score += 3; matched++; } else if (hit(s, w)) { score += 1; matched++; }
          });
          if (matched >= need && score > 0) hits.push({ t: it.t, u: it.u, k: it.k, sc: score + matched * 2 - (it.m ? 1 : 0) });
        });
        var seen = {}, q = norm(raw);
        foods.forEach(function (f) {
          var fn = norm(f.f);
          if (!seen[f.v] && (fn.indexOf(q) > -1 || (terms.length === 1 && terms[0].length >= 3 && fn.indexOf(terms[0]) > -1))) {
            seen[f.v] = 1; hits.push({ t: f.f + " → " + f.n, u: f.u + "#foods", k: "Food", sc: 2 });
          }
        });
        hits.sort(function (a, b) { return b.sc - a.sc; });
        var li = function (h) { return '<li><a href="' + h.u + '">' + esc(h.t) + "<small>" + esc(h.k) + "</small></a></li>"; };
        out.innerHTML = hits.length ? hits.slice(0, 6).map(li).join("") :
          '<li class="none">No exact match. Popular pages:</li>' + POPULAR.map(function (p) { return li({ t: p[0], u: p[1], k: "Popular" }); }).join("");
      });
    };
    input.addEventListener("input", run);
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { var a = out.querySelector("a"); if (a) { ev.preventDefault(); location.href = a.href; } }
    });
  });

  /* ---------- Myth of the week (home) ---------- */
  var mythData = document.getElementById("myths-data"), mythBox = document.getElementById("myth-week");
  if (mythData && mythBox) {
    try {
      var myths = JSON.parse(mythData.textContent), week = Math.floor(Date.now() / 6048e5), pick = [];
      for (var i = 0; i < 3; i++) pick.push(myths[(week * 3 + i) % myths.length]);
      mythBox.innerHTML = pick.map(function (m) {
        return '<div class="myth"><div class="m"><b>Myth</b>' + esc(m.m) + '</div><div class="f"><b>Fact</b>' + esc(m.f) +
          ' <a href="/vitamin-' + m.v.toLowerCase() + '/#myths">Vitamin ' + esc(m.v) + " →</a></div></div>";
      }).join("");
    } catch (e) { /* keep the static myths */ }
  }

  /* ---------- Food finder ---------- */
  var ff = document.getElementById("food-finder");
  if (ff) {
    var q = document.getElementById("ff-q"), out = document.getElementById("ff-out"), pop = document.getElementById("ff-pop");
    var popular = ["Spinach", "Eggs", "Milk", "Chickpeas", "Almonds", "Salmon", "Amla", "Banana", "Sweet potato", "Mushrooms", "Dal", "Broccoli"];
    pop.innerHTML = popular.map(function (p) { return '<button type="button">' + esc(p) + "</button>"; }).join("");
    pop.addEventListener("click", function (ev) { if (ev.target.tagName === "BUTTON") { q.value = ev.target.textContent; render(); } });
    var render = function () {
      var term = norm(q.value.trim());
      if (term.length < 2) { out.innerHTML = '<p class="tnote" style="margin-top:14px">Start typing, or tap a popular food above.</p>'; return; }
      load("/assets/foods.json").then(function (foods) {
        var groups = {};
        foods.forEach(function (f) {
          if (norm(f.f).indexOf(term) === -1) return;
          var key = f.f;
          (groups[key] = groups[key] || []).push(f);
        });
        var keys = Object.keys(groups).sort(function (a, b) {
          var ma = Math.max.apply(null, groups[a].map(function (x) { return x.p || 0; }));
          var mb = Math.max.apply(null, groups[b].map(function (x) { return x.p || 0; }));
          return mb - ma;
        });
        if (!keys.length) { out.innerHTML = '<p style="margin-top:14px">No matches for "' + esc(q.value) + '". Try a simpler word, like "beans" or "milk".</p>'; return; }
        out.innerHTML = keys.slice(0, 25).map(function (k) {
          var rows = groups[k].sort(function (a, b) { return (b.p || 0) - (a.p || 0); }).map(function (f) {
            var right = f.p != null
              ? '<div class="dv"><div class="b"><span style="width:' + Math.min(f.p, 100) + '%"></span></div><em>' + f.p + "%</em></div><small style=\"color:var(--muted)\">" + esc(f.a) + " per " + esc(f.s) + "</small>"
              : (f.in ? '<small style="color:var(--muted)">Good everyday source · Indian kitchen</small>' : '<small style="color:var(--muted)">' + esc(f.a) + " per " + esc(f.s) + "</small>");
            return '<div class="ff-row"><a href="' + f.u + '#foods" style="color:' + "var(--brand)" + '">' + esc(f.n) + "</a><div>" + right + "</div></div>";
          }).join("");
          return '<div class="ff-group"><h3>' + esc(k) + "</h3>" + rows + "</div>";
        }).join("");
      });
    };
    q.addEventListener("input", render);
    var startQ = new URLSearchParams(location.search).get("q");
    if (startQ) q.value = startQ;
    render();
  }

  /* ---------- Vitamin check ---------- */
  var form = document.getElementById("vcheck");
  if (form) {
    var KEY = "vitapals-check";
    try { var saved = JSON.parse(localStorage.getItem(KEY) || "null"); if (saved) Object.keys(saved).forEach(function (n) {
      var els = form.querySelectorAll('[name="' + n + '"]');
      els.forEach(function (el) { if (el.type === "radio") el.checked = el.value === saved[n]; else if (el.type === "checkbox") el.checked = !!saved[n]; });
    }); } catch (e) {}
    var prog = document.getElementById("vcheck-prog");
    var radios = {}; form.querySelectorAll('input[type="radio"]').forEach(function (el) { radios[el.name] = 1; });
    var total = Object.keys(radios).length;
    var tally = function () {
      var n = Object.keys(radios).filter(function (nm) { return form.querySelector('input[name="' + nm + '"]:checked'); }).length;
      if (prog) prog.textContent = n + " of " + total + " answered" + (n < total ? " · questions 12 and 13 are optional" : " · ready when you are");
    };
    form.addEventListener("change", tally); tally();
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var a = {};
      form.querySelectorAll("input").forEach(function (el) { if (el.type === "radio" && el.checked) a[el.name] = el.value; if (el.type === "checkbox") a[el.name] = el.checked; });
      try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {}
      var R = {};
      var add = function (v, lvl, why) { var w = { hi: 3, md: 2 }[lvl]; if (!R[v]) R[v] = { lvl: lvl, w: w, why: [] }; else if (w > R[v].w) { R[v].lvl = lvl; R[v].w = w; } R[v].why.push(why); };
      if (a.diet === "vegan") { add("B12", "hi", "B12 is only found naturally in animal foods. Vegans need fortified foods or a supplement."); add("D", "md", "Few plant foods contain vitamin D."); add("B2", "md", "Dairy is a main source of B2. Choose fortified plant milks."); }
      if (a.diet === "veg") add("B12", "md", "Vegetarians often run low on B12, even with dairy.");
      if (a.diet !== "omni") { add("Fe", "md", "Plant iron is absorbed less, so vegetarians need 1.8 times as much."); add("Zn", "md", "Zinc from beans and grains is absorbed less. Soaking and sprouting help."); }
      if (a.diet === "vegan") { add("Ca", "md", "Without dairy, choose fortified soy milk, calcium-set tofu, ragi and til."); add("I", "md", "Dairy, eggs and seafood are big iodine sources. Use iodized salt."); }
      if (a.dairy === "rare") add("Ca", "hi", "Dairy and fortified foods are the main calcium sources.");
      if (a.salt === "no") add("I", "hi", "Packaged foods rarely use iodized salt, so the salt you cook with matters.");
      if (a.periods === "heavy") add("Fe", "hi", "Heavy periods are a common reason for low iron. Ask about a ferritin test.");
      if (a.age === "50" || a.age === "71") { add("B12", "md", "After 50, your body absorbs less B12 from food."); add("B6", "md", "B6 needs rise slightly after 50."); }
      if (a.age === "71") { add("D", "hi", "After 70, you need more vitamin D (800 IU) and your skin makes less."); add("Ca", "md", "After 70, everyone needs 1,200 mg of calcium a day."); }
      if (a.preg === "yes") { add("B9", "hi", "Folic acid (400 mcg daily) is recommended before and during early pregnancy."); add("A", "md", "Avoid high-dose retinol supplements during pregnancy."); if (a.diet !== "omni") add("B12", "hi", "B12 is vital for your baby's development."); add("Fe", "hi", "Iron needs rise to 27 mg a day in pregnancy."); add("I", "hi", "Iodine needs rise in pregnancy. Check that your prenatal has 150 mcg."); }
      if (a.sun === "rare") add("D", "hi", "Little daylight on your skin means less vitamin D made.");
      if (a.skin === "dark") add("D", "md", "Darker skin makes less vitamin D from the same sunlight.");
      if (a.greens === "rare") { add("B9", "hi", "Leafy greens, dals and beans are top folate sources."); add("K", "md", "Leafy greens are the main source of vitamin K."); add("A", "md", "Greens and orange veg supply beta-carotene."); }
      if (a.greens === "some") add("B9", "md", "A daily bowl of dal or greens makes folate easy.");
      if (a.fruit === "rare") add("C", "hi", "Fresh fruit and raw veggies are the main vitamin C sources.");
      if (a.nuts === "rare") add("E", "md", "Nuts, seeds and their oils are the best vitamin E sources.");
      if (a.smoke) add("C", "hi", "Smokers need 35 mg more vitamin C a day.");
      if (a.alcohol) { add("B1", "hi", "Alcohol blocks B1 absorption."); add("B9", "md", "Alcohol lowers folate."); add("B6", "md", "Alcohol breaks down B6 faster."); }
      if (a.metformin) add("B12", "hi", "Long-term metformin lowers B12. Ask about a yearly check.");
      if (a.acid) add("B12", "hi", "Acid reducers lower B12 absorption over time.");
      if (a.warfarin) { add("K", "md", "Keep vitamin K intake steady, not low. Your dose depends on it."); add("E", "md", "Avoid high-dose vitamin E with blood thinners."); }
      if (a.seizure) { add("B9", "md", "Some seizure medicines lower folate."); add("B6", "md", "Some seizure medicines lower B6."); add("B7", "md", "Some seizure medicines lower biotin."); }
      var MIN = { Fe: ["Iron", "/iron/"], Ca: ["Calcium", "/calcium/"], Zn: ["Zinc", "/zinc/"], I: ["Iodine", "/iodine/"] };
      var nm = function (v) { return MIN[v] ? MIN[v][0] : "Vitamin " + v; }, lk = function (v) { return MIN[v] ? MIN[v][1] : "/vitamin-" + v.toLowerCase() + "/"; };
      var list = Object.keys(R).sort(function (x, y) { return R[y].w - R[x].w; });
      var out = document.getElementById("vcheck-out");
      var html = "<h2 style=\"margin-bottom:6px\">Your results</h2>";
      if (!list.length) html += '<div class="item"><span class="lvl ok">Looking good</span><div><strong>Nothing stands out.</strong><p style="margin:4px 0 0;color:var(--muted)">Your answers suggest a varied diet and lifestyle. Keep eating a mix of whole foods. Browse any vitamin to learn more.</p></div></div>';
      list.forEach(function (v) {
        var r = R[v], label = r.lvl === "hi" ? "Look closer" : "Worth watching";
        html += '<div class="item"><span class="lvl ' + r.lvl + '">' + label + '</span><div><strong><a href="' + lk(v) + '">' + nm(v) + '</a></strong><ul class="clean" style="margin-top:4px">' +
          r.why.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + '</ul><a href="' + lk(v) + '#foods">See the best foods →</a></div></div>';
      });
      html += '<div class="note" style="margin-top:14px"><p><strong>Next step:</strong> share this with your doctor. They can decide whether a blood test makes sense. This is not a diagnosis. <a href="#" onclick="window.print();return false">Print or save as PDF</a></p></div>';
      out.innerHTML = html;
      out.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
})();
