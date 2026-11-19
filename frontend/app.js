const $ = (id) => document.getElementById(id);
let selectedFile = null;
let mode = "file";

/* ---------------- fond étoilé ---------------- */
(() => {
  const c = $("stars"), ctx = c.getContext("2d");
  let stars = [];
  const resize = () => {
    c.width = innerWidth; c.height = innerHeight;
    stars = Array.from({ length: Math.min(180, innerWidth / 6) }, () => ({
      x: Math.random() * c.width, y: Math.random() * c.height,
      r: Math.random() * 1.6 + .2, s: Math.random() * .3 + .05, t: Math.random() * 6,
    }));
  };
  const draw = () => {
    ctx.clearRect(0, 0, c.width, c.height);
    for (const s of stars) {
      s.y -= s.s; s.t += .03;
      if (s.y < 0) { s.y = c.height; s.x = Math.random() * c.width; }
      ctx.globalAlpha = .4 + Math.sin(s.t) * .4;
      ctx.fillStyle = "#fff";
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 7); ctx.fill();
    }
    requestAnimationFrame(draw);
  };
  addEventListener("resize", resize); resize(); draw();
})();

/* ---------------- statut API ---------------- */
fetch("/api/health").then(r => r.json()).then(d => { if (d.demo) $("demo-badge").classList.remove("hidden"); }).catch(() => {});

/* ---------------- choix du modèle ---------------- */
let MODELS = [];
const savedModel = (() => { try { return localStorage.getItem("aura-model"); } catch { return null; } })();
function describeModel() {
  const m = MODELS.find(x => x.id === $("model-select").value);
  $("model-desc").textContent = m ? m.description : "";
}
fetch("/api/models").then(r => r.json()).then(list => {
  MODELS = list;
  const sel = $("model-select");
  sel.innerHTML = "";
  const familles = [...new Set(list.map(m => m.famille))];
  for (const f of familles) {
    const group = document.createElement("optgroup");
    group.label = f === "pré-entraîné" ? "Pré-entraînés (CamemBERT)" : f === "de zéro" ? "Entraînés de zéro" : f;
    for (const m of list.filter(x => x.famille === f)) {
      const o = document.createElement("option");
      o.value = m.id; o.textContent = m.label;
      group.appendChild(o);
    }
    sel.appendChild(group);
  }
  const def = list.find(m => m.id === savedModel) || list.find(m => m.default) || list[0];
  if (def) sel.value = def.id;
  describeModel();
}).catch(() => { $("model-select").innerHTML = "<option value=''>Modèle par défaut</option>"; });
$("model-select").addEventListener("change", () => {
  describeModel();
  try { localStorage.setItem("aura-model", $("model-select").value); } catch {}
});

/* ---------------- onglets ---------------- */
document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b === btn));
  mode = btn.dataset.tab;
  $("tab-file").classList.toggle("hidden", mode !== "file");
  $("tab-text").classList.toggle("hidden", mode !== "text");
  refreshButton();
}));

function refreshButton() {
  $("scan-btn").disabled = mode === "file" ? !selectedFile : $("text-input").value.trim().length < 3;
}

/* ---------------- fichier / drag & drop ---------------- */
const dz = $("dropzone");
function setFile(f) {
  if (!f) return;
  selectedFile = f;
  $("file-name").textContent = `📄 ${f.name} · ${(f.size / 1024).toFixed(1)} Ko`;
  $("file-name").classList.remove("hidden");
  refreshButton();
}
$("file-input").addEventListener("change", e => setFile(e.target.files[0]));
["dragenter", "dragover"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove("drag"); }));
dz.addEventListener("drop", e => setFile(e.dataTransfer.files[0]));

$("text-input").addEventListener("input", e => { $("char-count").textContent = e.target.value.length; refreshButton(); });

/* ---------------- scan ---------------- */
const SCAN_MSGS = [
  "Calibrage des chakras…", "Lecture des vibrations du texte…", "Consultation des esprits du NLP…",
  "Vectorisation TF-IDF de ton âme…", "Négociation avec le gradient…", "Mesure du taux de rizz lexical…",
  "Alignement des planètes et des embeddings…", "Calcul du softmax cosmique…",
];
const wait = ms => new Promise(r => setTimeout(r, ms));
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* texte qui se « décode » caractère par caractère */
function scramble(el, text) {
  const glyphs = "!<>-_/[]{}=+*^?#ΔΣΩ01";
  clearInterval(el._scr);
  if (REDUCED) { el.textContent = text; return; }
  let f = 0; const total = 14;
  el._scr = setInterval(() => {
    const k = Math.floor(text.length * ++f / total);
    el.textContent = text.slice(0, k) + [...text.slice(k)].map(ch => ch === " " ? " " : glyphs[Math.random() * glyphs.length | 0]).join("");
    if (f >= total) { clearInterval(el._scr); el.textContent = text; }
  }, 30);
}

/* couleur hex (#rrggbb) ou hsl(...) avec une transparence */
const alpha = (col, a) => col[0] === "#"
  ? col.slice(0, 7) + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, "0")
  : col.replace(")", ` / ${a})`);

/* ---------------- moteur du scanner (canvas) ---------------- */
const Scanner = (() => {
  const c = $("scan-canvas"), ctx = c.getContext("2d");
  const S = 260, C = S / 2, TAU = Math.PI * 2;
  let raf = 0, last = 0, t = 0, phase = 0, energy = 0, spawnAcc = 0, wordAcc = 0, readAcc = 0;
  let parts = [], words = [], pool = [], lock = null;

  function fit() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    c.width = c.height = S * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  const rnd = (a, b) => a + Math.random() * (b - a);
  const dir = () => (Math.random() < .5 ? 1 : -1);

  function spawnParticle() {
    parts.push({ a: rnd(0, TAU), r: rnd(C - 6, C + 6), w: rnd(.6, 1.4) * dir(), v: rnd(22, 50), size: rnd(.8, 2.6), hue: rnd(0, 360) });
  }
  function spawnWord() {
    if (!pool.length || words.length >= 5) return;
    words.push({ txt: pool[Math.random() * pool.length | 0], a: rnd(0, TAU), r: C - 14, w: rnd(.3, .6) * dir(), v: rnd(16, 26), life: 0 });
  }

  function draw(now) {
    const dt = Math.min((now - last) / 1000, .05); last = now; t += dt;
    const k = lock ? (lock.dur ? Math.min((now - lock.t) / lock.dur, 1) : 1) : 0; // 0 → 1 pendant le verrouillage
    phase += dt * (1 + k * 6);                                                     // tout s'emballe au verrouillage
    energy *= Math.pow(.25, dt);
    const col = lock ? lock.color : `hsl(${(t * 70) % 360} 100% 66%)`;

    ctx.clearRect(0, 0, S, S);

    // halo central qui grossit avec l'énergie absorbée
    let g = ctx.createRadialGradient(C, C, 0, C, C, C);
    g.addColorStop(0, alpha(col, Math.min(1, .3 + energy * .5 + k * .6)));
    g.addColorStop(.45, alpha(col, .08 + k * .2));
    g.addColorStop(1, alpha(col, 0));
    ctx.fillStyle = g; ctx.fillRect(0, 0, S, S);

    ctx.save(); ctx.translate(C, C);

    // balayage radar
    if (ctx.createConicGradient) {
      const a = phase * 2.6;
      g = ctx.createConicGradient(a, 0, 0);
      g.addColorStop(0, alpha(col, 0)); g.addColorStop(.82, alpha(col, 0)); g.addColorStop(1, alpha(col, .45));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, C - 18, 0, TAU); ctx.fill();
      ctx.strokeStyle = alpha(col, .9); ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * (C - 18), Math.sin(a) * (C - 18)); ctx.stroke();
    }

    // graduations extérieures
    ctx.save(); ctx.rotate(phase * .4); ctx.strokeStyle = col; ctx.lineWidth = 1.5;
    for (let i = 0; i < 72; i++) {
      const long = i % 6 === 0;
      ctx.globalAlpha = long ? .9 : .3;
      ctx.beginPath(); ctx.moveTo(C - 3, 0); ctx.lineTo(C - (long ? 14 : 8), 0); ctx.stroke();
      ctx.rotate(TAU / 72);
    }
    ctx.restore(); ctx.globalAlpha = 1;

    // anneaux pointillés contrarotatifs
    [[C - 26, 1.1, [18, 12], 2], [C - 46, -1.7, [3, 7], 2.5], [C - 66, 2.4, [40, 24], 1.5]].forEach(([r, sp, dash, lw]) => {
      ctx.save(); ctx.rotate(phase * sp); ctx.setLineDash(dash);
      ctx.strokeStyle = alpha(col, .75); ctx.lineWidth = lw;
      ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke(); ctx.restore();
    });

    // onde de « fréquence d'aura » autour du noyau
    const amp = 2 + energy * 9 + k * 10;
    ctx.strokeStyle = alpha(col, .95); ctx.lineWidth = 2; ctx.beginPath();
    for (let i = 0; i <= 120; i++) {
      const a = i / 120 * TAU;
      const r = 42 + Math.sin(a * 7 + phase * 5) * amp * .6 + Math.sin(a * 13 - phase * 8) * amp * .4;
      i ? ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r) : ctx.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    ctx.closePath(); ctx.stroke();

    // particules aspirées en spirale (ou expulsées au verrouillage)
    if (!lock) for (spawnAcc += dt * 45; spawnAcc > 1; spawnAcc--) spawnParticle();
    ctx.lineCap = "round";
    parts = parts.filter(p => {
      const pr = p.r, pa = p.a;
      if (p.out) { p.r += p.v * dt; p.v *= Math.pow(.4, dt); }
      else { p.a += p.w * dt * (1 + 50 / p.r); p.r -= p.v * dt * (1 + (C - p.r) / 35); }
      if (!p.out && p.r < 24) { energy = Math.min(1.5, energy + .04); return false; }
      if (p.out && (p.r > C + 20 || p.v < 8)) return false;
      // traînée : du point précédent (étiré) au point courant
      const tr = pr + (pr - p.r) * 2, ta = pa + (pa - p.a) * 2;
      ctx.strokeStyle = lock ? lock.color : `hsl(${(p.hue + t * 70) % 360} 100% 72%)`;
      ctx.globalAlpha = p.out ? Math.max(0, 1 - p.r / (C + 20)) : Math.min(1, (C + 6 - p.r) / 30);
      ctx.lineWidth = p.size;
      ctx.beginPath(); ctx.moveTo(Math.cos(ta) * tr, Math.sin(ta) * tr); ctx.lineTo(Math.cos(p.a) * p.r, Math.sin(p.a) * p.r); ctx.stroke();
      return true;
    });
    ctx.globalAlpha = 1;

    // mots du texte absorbés par le noyau
    if (!lock && (wordAcc += dt) > .5) { wordAcc = 0; spawnWord(); }
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    words = words.filter(w => {
      w.life += dt; w.a += w.w * dt; w.r -= w.v * dt * (1 + (C - w.r) / 60);
      if (w.r < 26) { energy = Math.min(1.5, energy + .3); return false; }
      const a = Math.min(1, w.life * 2) * Math.min(1, (w.r - 26) / 30) * (1 - k);
      if (a <= 0 && lock) return false;
      ctx.font = `600 ${9 + (w.r / C) * 6}px "Space Grotesk", sans-serif`;
      ctx.fillStyle = `rgba(255,255,255,${a})`;
      ctx.fillText(w.txt, Math.cos(w.a) * w.r, Math.sin(w.a) * w.r);
      return true;
    });

    // onde de choc + flash au verrouillage
    if (lock) {
      ctx.strokeStyle = alpha(lock.color, 1 - k); ctx.lineWidth = 8 * (1 - k) + 1;
      ctx.beginPath(); ctx.arc(0, 0, 20 + k * C * 1.1, 0, TAU); ctx.stroke();
      ctx.fillStyle = `rgba(255,255,255,${Math.pow(k, 3) * .9})`;
      ctx.beginPath(); ctx.arc(0, 0, C, 0, TAU); ctx.fill();
    }
    ctx.restore();

    // compteur qui s'affole pendant la lecture
    if (!lock && (readAcc += dt) > .08) {
      readAcc = 0;
      const v = Math.round(rnd(-1, 1) * (1500 + t * 2500));
      $("scan-reading").textContent = (v >= 0 ? "+" : "−") + Math.abs(v).toLocaleString("fr-FR");
    }

    if (!REDUCED) raf = requestAnimationFrame(draw);
  }

  return {
    start(sourceWords) {
      cancelAnimationFrame(raf); fit();
      parts = []; words = []; lock = null; t = phase = energy = spawnAcc = wordAcc = readAcc = 0;
      pool = sourceWords;
      for (let i = 0; i < 30; i++) { spawnParticle(); parts[i].r = rnd(30, C); }
      const core = $("scan-core"); core.textContent = "👁️"; core.classList.remove("locked");
      $("scan-reading").style.color = "";
      last = performance.now(); raf = requestAnimationFrame(draw);
    },
    // verrouille le signal sur la couleur de la catégorie, puis explose
    lock(color, emoji) {
      const dur = REDUCED ? 0 : 750;
      lock = { color, t: performance.now(), dur };
      parts.forEach(p => { p.out = true; p.v = rnd(120, 320); });
      for (let i = 0; i < 70; i++) parts.push({ a: rnd(0, TAU), r: 20, w: 0, v: rnd(150, 420), size: rnd(1, 3), out: true });
      const core = $("scan-core"); core.textContent = emoji; core.classList.add("locked");
      $("scan-reading").textContent = "VERROUILLÉ"; $("scan-reading").style.color = color;
      if (REDUCED) draw(performance.now());
      return wait(dur + 50);
    },
    stop() { cancelAnimationFrame(raf); },
  };
})();

function scanWords() {
  const base = ["vibes", "rizz", "charisme", "flow", "aura", "énergie", "prestance"];
  if (mode === "text") {
    const w = $("text-input").value.split(/[\s,.;:!?'"()«»]+/).filter(x => x.length > 3).slice(0, 60);
    return w.length ? w : base;
  }
  return selectedFile ? [...selectedFile.name.replace(/\.[^.]+$/, "").split(/[\s_\-.]+/).filter(Boolean), ...base] : base;
}

$("scan-btn").addEventListener("click", async () => {
  $("error").classList.add("hidden");
  const fd = new FormData();
  if (mode === "file") fd.append("file", selectedFile); else fd.append("text", $("text-input").value);
  fd.append("model", $("model-select").value || "");

  show("scan-card");
  Scanner.start(scanWords());
  let i = 0, p = 0;
  scramble($("scan-msg"), SCAN_MSGS[0]);
  const msgTimer = setInterval(() => scramble($("scan-msg"), SCAN_MSGS[++i % SCAN_MSGS.length]), 900);
  const barTimer = setInterval(() => { p = Math.min(p + Math.random() * 12, 92); $("progress-bar").style.width = p + "%"; }, 200);

  try {
    const [res] = await Promise.all([fetch("/api/predict", { method: "POST", body: fd }), wait(2600)]); // suspense obligatoire
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Erreur inconnue");
    clearInterval(msgTimer); clearInterval(barTimer);
    $("progress-bar").style.width = "100%";
    scramble($("scan-msg"), "Aura détectée !");
    await Scanner.lock(colorFor(data.category), emojiFor(data.category));
    flash(colorFor(data.category));
    showResult(data);
  } catch (err) {
    show("input-card");
    $("error").textContent = "💀 " + err.message;
    $("error").classList.remove("hidden");
    $("input-card").classList.add("shake");
    setTimeout(() => $("input-card").classList.remove("shake"), 500);
  } finally {
    clearInterval(msgTimer); clearInterval(barTimer);
    Scanner.stop();
  }
});

function flash(color) {
  const f = $("flash");
  f.style.setProperty("--flash", color);
  f.classList.remove("on"); void f.offsetWidth; f.classList.add("on");
}

function show(id) {
  ["input-card", "scan-card", "result-card"].forEach(c => $(c).classList.toggle("hidden", c !== id));
  if (id === "scan-card") $("progress-bar").style.width = "0";
}

/* ---------------- résultat ---------------- */
// Tout dépend de la CLASSE prédite (et du score), jamais de la seule confiance du modèle.
const CLASSES = {
  "Anti-Aura":     { color: "#ff5c7a", emoji: "💀", rank: "💀 ANTI-AURA",
                     roast: ["Aïe. L'aura est partie sans laisser d'adresse.", "Même le silence aurait eu plus d'aura."] },
  "Aura Correcte": { color: "#7fd4ff", emoji: "🙂", rank: "🙂 AURA CORRECTE",
                     roast: ["Propre, honnête, sans éclat : le texte fait le job.", "Ni gênant ni mémorable. Une aura de mardi après-midi."] },
  "Forte Aura":    { color: "#ffb347", emoji: "🔥", rank: "🔥 FORTE AURA",
                     roast: ["Ça claque. La foule a réagi.", "Réplique qui fait mouche : respect."] },
  "Aura Divine":   { color: "#ffd84d", emoji: "👑", rank: "👑 AURA DIVINE",
                     roast: ["Formule mémorable. On la recopiera dans des carnets.", "Les dieux de la rhétorique applaudissent debout."] },
};
const colorFor = label => (CLASSES[label] || {}).color || "#b86bff";
const emojiFor = label => (CLASSES[label] || {}).emoji || "✨";
const pick = arr => arr[Math.floor(Math.random() * arr.length)];

function confidenceNote(p) {
  if (p >= .85) return "Le modèle est sûr de lui.";
  if (p >= .6) return "Le modèle est plutôt confiant.";
  return "Le modèle hésite : à prendre avec des pincettes.";
}

let GIFS = {};
fetch("/api/gifs").then(r => r.json()).then(g => { GIFS = g; }).catch(() => {});
function showGif(category) {
  const list = GIFS[category] || [];
  const img = $("aura-gif");
  if (!list.length) { img.classList.add("hidden"); return; }
  img.src = encodeURI(pick(list));
  img.classList.remove("hidden");
}

const TIERS = { "Anti-Aura": "anti", "Aura Correcte": "ok", "Forte Aura": "forte", "Aura Divine": "divine" };

function shockwave(n = 3) {
  const o = $("aura-orb").getBoundingClientRect();
  for (let i = 0; i < n; i++) {
    const s = document.createElement("span");
    s.className = "shockwave";
    s.style.left = o.left + o.width / 2 + "px"; s.style.top = o.top + o.height / 2 + "px";
    s.style.animationDelay = i * .14 + "s";
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 1600);
  }
}

function showResult(d) {
  show("result-card");
  const card = $("result-card"), tier = TIERS[d.category] || "ok";
  card.dataset.tier = tier;
  card.classList.remove("reveal"); void card.offsetWidth; card.classList.add("reveal");
  $("aura-points").classList.remove("pop");
  const cls = CLASSES[d.category] || { rank: d.category, roast: [""] };
  document.documentElement.style.setProperty("--aura", colorFor(d.category));
  $("aura-emoji").textContent = emojiFor(d.category);
  $("category").textContent = d.category;
  $("proba").textContent = (d.probability * 100).toFixed(1) + " %";
  $("score-wrap").classList.toggle("hidden", d.score === undefined || d.demo);
  if (d.score !== undefined) $("score").textContent = (d.score > 0 ? "+" : "") + d.score;
  $("model-used").textContent = d.model ? d.model.label : "modèle par défaut";
  $("rank").textContent = cls.rank;
  $("roast").textContent = pick(cls.roast) + " " + confidenceNote(d.probability);
  showGif(d.category);
  $("n-chars").textContent = d.n_chars;
  $("preview-text").textContent = d.preview + (d.n_chars > 280 ? "…" : "");

  // points d'aura : le score (-100..+100) × 100, négatif pour l'Anti-Aura
  const CENTRES = { "Anti-Aura": -55, "Aura Correcte": 7, "Forte Aura": 50, "Aura Divine": 87 };
  const score = d.score !== undefined ? d.score : (CENTRES[d.category] ?? 0);
  const points = Math.round(score * 100);
  $("aura-points").textContent = "+0";
  setTimeout(() => countUp($("aura-points"), points, () => $("aura-points").classList.add("pop")), REDUCED ? 0 : 450);

  $("bars").innerHTML = "";
  d.probabilities.forEach(({ label, probability }, i) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `<span class="bar-label"></span><div class="bar-track"><div class="bar-fill"></div></div><span class="bar-val">${(probability * 100).toFixed(1)}%</span>`;
    row.querySelector(".bar-label").textContent = label;
    row.querySelector(".bar-fill").style.background = colorFor(label);
    row.querySelector(".bar-fill").style.transitionDelay = 1 + i * .12 + "s";
    $("bars").appendChild(row);
    requestAnimationFrame(() => requestAnimationFrame(() => { row.querySelector(".bar-fill").style.width = probability * 100 + "%"; }));
  });

  // l'orbe atterrit, puis onde de choc + particules (qui tombent pour l'Anti-Aura)
  setTimeout(() => {
    shockwave(tier === "divine" ? 4 : tier === "forte" ? 3 : tier === "anti" ? 1 : 2);
    burst(emojiFor(d.category), { divine: 60, forte: 35, ok: 14, anti: 12 }[tier], tier === "anti");
    if (tier === "divine" || tier === "forte") {
      document.body.classList.remove("quake"); void document.body.offsetWidth;
      document.body.classList.add("quake");
      setTimeout(() => document.body.classList.remove("quake"), 700);
    }
  }, REDUCED ? 0 : 380);
  window.__lastResult = { ...d, points };
  resetBoost(d);
}

/* ---------------- booster d'aura ---------------- */
const BOOST_MAX = 500;   // même limite que le backend
const BOOST_MSGS = ["On cherche de meilleures formules…", "Notre modèle note chaque variante…", "On retouche les meilleures versions mot à mot…"];
let boostText = "";

function resetBoost(d) {
  // texte complet si saisi au clavier, sinon l'extrait du fichier (seulement s'il est complet)
  boostText = mode === "text" ? $("text-input").value.trim() : (d.n_chars <= 280 ? d.preview : "");
  $("boost").classList.add("hidden");
  $("boost-result").classList.add("hidden");
  const ok = boostText.length >= 3 && boostText.length <= BOOST_MAX && !d.demo;
  $("boost-btn").disabled = !ok;
  $("boost-btn").title = ok ? "" : `Le booster marche sur une phrase ou un court passage (${BOOST_MAX} caractères max).`;
}

const fmtScore = s => (s > 0 ? "+" : "") + s;
function chip(el, r) {
  el.textContent = `${emojiFor(r.category)} ${r.category} · ${fmtScore(r.score)}`;
  el.style.color = colorFor(r.category);
}

$("boost-btn").addEventListener("click", async () => {
  const btn = $("boost-btn"), status = $("boost-status");
  btn.disabled = true;
  $("boost").classList.remove("hidden");
  $("boost-result").classList.add("hidden");
  status.classList.add("loading");
  let i = 0; status.textContent = BOOST_MSGS[0];
  const timer = setInterval(() => { status.textContent = BOOST_MSGS[Math.min(++i, BOOST_MSGS.length - 1)]; }, 4000);
  const fd = new FormData();
  fd.append("text", boostText);
  fd.append("model", $("model-select").value || "");
  try {
    const res = await fetch("/api/improve", { method: "POST", body: fd });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail || "Erreur inconnue");
    showBoost(d);
  } catch (err) {
    status.textContent = "💀 " + err.message;
    btn.disabled = false;
  } finally {
    clearInterval(timer); status.classList.remove("loading");
  }
});

function showBoost(d) {
  const best = d.meilleur;
  $("boost-status").textContent = d.gain > 0
    ? `Meilleure version parmi ${d.n_essais} variantes, selon ${d.model.label} :`
    : `Aucune des ${d.n_essais} variantes ne bat l'original selon ${d.model.label} : ton texte avait déjà de l'aura. Voici la meilleure quand même :`;
  $("boost-note").innerHTML = "";
  $("boost-note").append(`Variantes générées par ${d.generateur}, puis `);
  const fort = document.createElement("strong"); fort.textContent = "notre modèle d'aura";
  $("boost-note").append(fort, " note chacune et garde la meilleure. Gratuit, sans API payante.");
  $("boost-text").textContent = best.texte;
  chip($("boost-before"), d.original);
  chip($("boost-after"), best);
  $("boost-gain").textContent = (d.gain >= 0 ? "+" : "−") + Math.abs(d.gain * 100).toLocaleString("fr-FR") + " AURA";
  $("boost-n").textContent = d.n_essais;
  $("boost-others").closest("details").classList.toggle("hidden", !d.autres.length);
  if (d.mode === "local") $("boost-status").textContent +=
    " (mode retouche : on polit ta phrase. Pour des phrases vraiment nouvelles, installe un LLM gratuit : ollama pull mistral)";
  $("boost-others").innerHTML = "";
  d.autres.forEach(r => {
    const li = document.createElement("li");
    li.textContent = r.texte + " ";
    const s = document.createElement("span"); s.className = "s"; s.textContent = `(${r.category}, ${fmtScore(r.score)})`;
    li.appendChild(s); $("boost-others").appendChild(li);
  });
  $("boost-result").classList.remove("hidden");
  if (d.gain > 0) burst(emojiFor(best.category), 25);
  window.__boost = best.texte;
}

$("boost-copy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(window.__boost || ""); $("boost-copy").textContent = "✅ Copié !"; }
  catch { $("boost-copy").textContent = "❌ Copie impossible"; }
  setTimeout(() => ($("boost-copy").textContent = "📋 Copier la version boostée"), 1500);
});
$("boost-scan").addEventListener("click", () => {
  // remet la version boostée dans la zone de texte et relance un scan complet
  document.querySelector('.tab[data-tab="text"]').click();
  $("text-input").value = window.__boost || "";
  $("char-count").textContent = $("text-input").value.length;
  refreshButton(); $("scan-btn").click();
});

function countUp(el, target, done) {
  const start = performance.now(), dur = REDUCED ? 0 : 1500;
  const step = now => {
    const t = dur ? Math.min((now - start) / dur, 1) : 1;
    const v = Math.round(target * (1 - Math.pow(1 - t, 3)));
    el.textContent = (v >= 0 ? "+" : "−") + Math.abs(v).toLocaleString("fr-FR");
    if (t < 1) requestAnimationFrame(step); else if (done) done();
  };
  requestAnimationFrame(step);
}

function burst(emoji, n, fall = false) {
  const orb = $("aura-orb").getBoundingClientRect();
  const cx = orb.left + orb.width / 2, cy = orb.top + orb.height / 2;
  for (let i = 0; i < n; i++) {
    const s = document.createElement("span");
    s.className = "particle";
    s.textContent = Math.random() < .5 ? emoji : (fall ? ["💧", "🥀", "📉"] : ["✨", "⭐", "💫"])[i % 3];
    const a = Math.random() * Math.PI * 2, dist = 120 + Math.random() * 260;
    s.style.left = cx + "px"; s.style.top = cy + "px";
    s.style.setProperty("--dx", (fall ? (Math.random() - .5) * 260 : Math.cos(a) * dist) + "px");
    s.style.setProperty("--dy", (fall ? 180 + Math.random() * 280 : Math.sin(a) * dist) + "px");
    if (fall) s.style.animationTimingFunction = "cubic-bezier(.5, 0, .9, .6)";
    s.style.setProperty("--rot", (Math.random() * 720 - 360) + "deg");
    s.style.animationDelay = Math.random() * .3 + "s";
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 2000);
  }
}

/* ---------------- actions ---------------- */
$("again-btn").addEventListener("click", () => {
  selectedFile = null; $("file-input").value = ""; $("file-name").classList.add("hidden");
  $("text-input").value = ""; $("char-count").textContent = "0";
  refreshButton(); show("input-card");
});
$("copy-btn").addEventListener("click", async () => {
  const r = window.__lastResult; if (!r) return;
  const txt = `🔮 Aura Detector : mon texte = ${r.category} (${(r.probability * 100).toFixed(1)}%), ${r.points >= 0 ? "+" : "−"}${Math.abs(r.points)} AURA ✨` +
    (r.model ? ` [${r.model.label}]` : "");
  try { await navigator.clipboard.writeText(txt); $("copy-btn").textContent = "✅ Copié !"; }
  catch { $("copy-btn").textContent = "❌ Copie impossible"; }
  setTimeout(() => ($("copy-btn").textContent = "📋 Copier mon score"), 1500);
});
