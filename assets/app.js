/* Ousia Research · front door — interactions. No dependencies. */
(() => {
  "use strict";
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── print edition ─────────────────────────────────────────────────────── */
  const EDITIONS = ["ink", "bone", "riso"];
  const setEdition = (name) => {
    if (!EDITIONS.includes(name)) name = "ink";
    document.documentElement.dataset.edition = name;
    $$(".editions button").forEach(b =>
      b.setAttribute("aria-pressed", String(b.dataset.set === name)));
    try { localStorage.setItem("ousia.edition", name); } catch (_) {}
  };
  $$(".editions button").forEach(b =>
    b.addEventListener("click", () => setEdition(b.dataset.set)));
  let stored = null;
  try { stored = localStorage.getItem("ousia.edition"); } catch (_) {}
  setEdition(stored || "ink");

  /* ── hero parallax ─────────────────────────────────────────────────────── */
  const layers = $$(".hero .layer");
  if (layers.length && !reduce) {
    const depth = [0, 6, 15, 26, 40];           // percent of scroll, far → near
    let ticking = false;
    const paint = () => {
      const y = Math.min(window.scrollY, window.innerHeight * 1.2);
      layers.forEach((el, i) => {
        const d = (depth[i] ?? 20) * (y / 100);
        el.style.transform = `translate3d(0, ${d.toFixed(2)}px, 0)`;
      });
      ticking = false;
    };
    addEventListener("scroll", () => {
      if (!ticking) { ticking = true; requestAnimationFrame(paint); }
    }, { passive: true });
    paint();
  }

  /* ── route stations light as they arrive ───────────────────────────────── */
  const stations = $$(".station");
  if (stations.length) {
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("on"); });
      }, { rootMargin: "-35% 0px -35% 0px" });
      stations.forEach(s => io.observe(s));
    } else {
      stations.forEach(s => s.classList.add("on"));
    }
  }

  /* ── ledger ────────────────────────────────────────────────────────────── */
  const TIER = {
    "CONFIRMED":      { cls: "CONFIRMED", label: "CONFIRMED" },
    "OPEN RISK":      { cls: "OPEN",      label: "OPEN RISK" },
    "COULDN'T CHECK": { cls: "COULDNT",   label: "COULDN'T CHECK" }
  };
  const esc = (s) => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

  const renderDetail = (rec) => {
    const t = TIER[rec.tier] || TIER["OPEN RISK"];
    $("#ledger-detail").innerHTML = `
      <span class="tier-tag ${t.cls}">${t.label}</span>
      <h3>${esc(rec.claim)}</h3>
      <dl>
        <div><dt>how we know</dt><dd>${esc(rec.source_type)}</dd></div>
        <div><dt>the read</dt><dd>${esc(rec.source)}</dd></div>
        <div><dt>raw</dt><dd>${esc(rec.raw)}</dd></div>
        <div><dt>as published</dt><dd>${esc(rec.normalized)}</dd></div>
      </dl>
      <p class="note">${esc(rec.note)}</p>`;
  };

  const buildLedger = (data) => {
    const list = $("#ledger-items");
    const host = $("#ledger-detail");
    if (!list || !host) return;
    const records = data.records || [];
    if (!records.length) return;

    list.innerHTML = records.map((r, i) => {
      const t = TIER[r.tier] || TIER["OPEN RISK"];
      return `<button type="button" role="tab" id="tab-${i}" aria-controls="ledger-detail"
        aria-selected="${i === 0}" data-i="${i}">
        <span class="marker ${t.cls === "CONFIRMED" ? "t1" : t.cls === "OPEN" ? "t2" : "t3"}"
          aria-hidden="true"></span>
        <span class="claim">${esc(r.claim)}<span class="tier-mini ${t.cls}">${t.label}</span></span></button>`;
    }).join("");

    const buttons = $$("#ledger-items button");
    const select = (i) => {
      buttons.forEach((b, j) => b.setAttribute("aria-selected", String(i === j)));
      renderDetail(records[i]);
    };
    buttons.forEach(b => b.addEventListener("click", () => select(Number(b.dataset.i))));
    list.addEventListener("keydown", (e) => {
      const cur = buttons.findIndex(b => b.getAttribute("aria-selected") === "true");
      const next = e.key === "ArrowDown" ? cur + 1 : e.key === "ArrowUp" ? cur - 1 : -1;
      if (next >= 0 && next < buttons.length) { e.preventDefault(); buttons[next].focus(); select(next); }
    });
    select(0);
    if (data.correction_rule) {
      const c = $("#corrections");
      if (c) c.textContent = "Corrections: " + data.correction_rule;
    }
  };

  /* ── tracks, from the build manifest ───────────────────────────────────── */
  const human = (n) => n < 1024 ? n + " B" : (n / 1024).toFixed(1) + " KB";
  const buildTracks = (manifest) => {
    const host = $("#tracks-list");
    if (!host || !manifest.items) return;
    const sections = [...new Set(manifest.items.map(i => i.section))];
    host.innerHTML = sections.map(sec => {
      const items = manifest.items.filter(i => i.section === sec);
      const title = items[0].section_title;
      return `<div class="card">
        <span class="meta">${esc(title)} · ${items.length} item${items.length > 1 ? "s" : ""}</span>
        ${items.map(i => `<p><a href="${esc(i.url)}">${esc(i.title)}</a>
          <span class="meta"> · ${human(i.bytes)} · <code>${esc(i.sha256.slice(0, 12))}</code></span></p>`).join("")}
      </div>`;
    }).join("");
    const stamp = $("#built");
    if (stamp) stamp.textContent =
      `built ${manifest.built} · ${manifest.items.length} published items · generated by ${manifest.generator}`;
  };

  /* ── load the data the page needs ──────────────────────────────────────── */
  const get = (url) => fetch(url, { cache: "no-cache" }).then(r => {
    if (!r.ok) throw new Error(url + " → " + r.status);
    return r.json();
  });

  get("/data/records.json").then(buildLedger).catch(() => {
    const d = $("#ledger-detail");
    if (d) d.innerHTML = `<p class="fine">The ledger could not be loaded. It is a static file:
      <a href="/data/records.json">/data/records.json</a>.</p>`;
  });
  get("/data/manifest.json").then(buildTracks).catch(() => {
    const t = $("#tracks-list");
    if (t) t.innerHTML = `<p class="fine">Manifest unavailable.
      <a href="/data/manifest.json">/data/manifest.json</a>.</p>`;
  });
})();
