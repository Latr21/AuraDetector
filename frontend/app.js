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

$("scan-btn").addEventListener("click", async () => {
  $("error").classList.add("hidden");
  const fd = new FormData();
  if (mode === "file") fd.append("file", selectedFile); else fd.append("text", $("text-input").value);
  fd.append("model", $("model-select").value || "");

  show("scan-card");
  let i = 0, p = 0;
  $("scan-msg").textContent = SCAN_MSGS[0];
  const msgTimer = setInterval(() => { $("scan-msg").textContent = SCAN_MSGS[++i % SCAN_MSGS.length]; }, 700);
  const barTimer = setInterval(() => { p = Math.min(p + Math.random() * 12, 92); $("progress-bar").style.width = p + "%"; }, 200);

  try {
    const [res] = await Promise.all([fetch("/api/predict", { method: "POST", body: fd }), wait(2400)]); // suspense obligatoire
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Erreur inconnue");
    $("progress-bar").style.width = "100%";
    await wait(300);
    showResult(data);
  } catch (err) {
    show("input-card");
    $("error").textContent = "💀 " + err.message;
    $("error").classList.remove("hidden");
    $("input-card").classList.add("shake");
    setTimeout(() => $("input-card").classList.remove("shake"), 500);
  } finally {
    clearInterval(msgTimer); clearInterval(barTimer);
  }
});

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

function showResult(d) {
  show("result-card");
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
  countUp($("aura-points"), points);

  $("bars").innerHTML = "";
  d.probabilities.forEach(({ label, probability }) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `<span class="bar-label"></span><div class="bar-track"><div class="bar-fill"></div></div><span class="bar-val">${(probability * 100).toFixed(1)}%</span>`;
    row.querySelector(".bar-label").textContent = label;
    row.querySelector(".bar-fill").style.background = colorFor(label);
    $("bars").appendChild(row);
    requestAnimationFrame(() => requestAnimationFrame(() => { row.querySelector(".bar-fill").style.width = probability * 100 + "%"; }));
  });

  burst(emojiFor(d.category), { "Aura Divine": 55, "Forte Aura": 35, "Aura Correcte": 12, "Anti-Aura": 8 }[d.category] || 15);
  window.__lastResult = { ...d, points };
}

function countUp(el, target) {
  const start = performance.now(), dur = 1500;
  const step = now => {
    const t = Math.min((now - start) / dur, 1);
    const v = Math.round(target * (1 - Math.pow(1 - t, 3)));
    el.textContent = (v >= 0 ? "+" : "−") + Math.abs(v).toLocaleString("fr-FR");
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function burst(emoji, n) {
  const orb = $("aura-orb").getBoundingClientRect();
  const cx = orb.left + orb.width / 2, cy = orb.top + orb.height / 2;
  for (let i = 0; i < n; i++) {
    const s = document.createElement("span");
    s.className = "particle";
    s.textContent = Math.random() < .5 ? emoji : ["✨", "⭐", "💫"][i % 3];
    const a = Math.random() * Math.PI * 2, dist = 120 + Math.random() * 260;
    s.style.left = cx + "px"; s.style.top = cy + "px";
    s.style.setProperty("--dx", Math.cos(a) * dist + "px");
    s.style.setProperty("--dy", Math.sin(a) * dist + "px");
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
