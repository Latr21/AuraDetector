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
// Couleur stable par catégorie (hash du nom -> teinte)
function colorFor(label) {
  let h = 0;
  for (const ch of label) h = (h * 31 + ch.charCodeAt(0)) % 360;
  return `hsl(${h}, 95%, 65%)`;
}
const EMOJIS = ["🔥", "⚡", "🌌", "💎", "🌈", "🪐", "🦄", "👑", "🌪️", "🧿", "☄️", "🍀"];
const emojiFor = label => EMOJIS[[...label].reduce((a, c) => a + c.charCodeAt(0), 0) % EMOJIS.length];

function rankFor(p) {
  if (p >= .9) return ["👑 AURA LÉGENDAIRE", "L'IA est formelle. Aucun doute. Ce texte est né pour ça."];
  if (p >= .75) return ["🔥 AURA ÉPIQUE", "Très forte énergie détectée. Le modèle est quasi sûr de lui."];
  if (p >= .55) return ["✨ AURA SOLIDE", "Bonne vibe, mais quelques ondes parasites."];
  if (p >= .35) return ["🌫️ AURA FLOUE", "Le texte hésite entre plusieurs mondes… et le modèle aussi."];
  return ["🫠 AURA EN CRISE", "Même l'IA ne sait pas trop quoi penser de toi."];
}

function showResult(d) {
  show("result-card");
  const color = colorFor(d.category);
  document.documentElement.style.setProperty("--aura", color);
  $("aura-emoji").textContent = emojiFor(d.category);
  $("category").textContent = d.category;
  $("proba").textContent = (d.probability * 100).toFixed(1) + " %";
  const [rank, roast] = rankFor(d.probability);
  $("rank").textContent = rank;
  $("roast").textContent = roast;
  $("n-chars").textContent = d.n_chars;
  $("preview-text").textContent = d.preview + (d.n_chars > 280 ? "…" : "");

  // points d'aura : la confiance du modèle convertie en "aura"
  const points = Math.round(d.probability * 10000);
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

  burst(emojiFor(d.category), d.probability >= .55 ? 40 : 15);
  window.__lastResult = { ...d, points };
}

function countUp(el, target) {
  const start = performance.now(), dur = 1500;
  const step = now => {
    const t = Math.min((now - start) / dur, 1);
    el.textContent = "+" + Math.round(target * (1 - Math.pow(1 - t, 3))).toLocaleString("fr-FR");
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
  const txt = `🔮 Aura Detector : mon texte = ${r.category} (${(r.probability * 100).toFixed(1)}%), +${r.points} AURA ✨`;
  try { await navigator.clipboard.writeText(txt); $("copy-btn").textContent = "✅ Copié !"; }
  catch { $("copy-btn").textContent = "❌ Copie impossible"; }
  setTimeout(() => ($("copy-btn").textContent = "📋 Copier mon score"), 1500);
});
