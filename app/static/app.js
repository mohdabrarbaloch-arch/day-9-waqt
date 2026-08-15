/* Waqt SPA — vanilla JS, zero build step */

const API = "";
const state = {
  lat: 24.8607,
  lng: 67.0011,
  tz: "Asia/Karachi",
  cityName: "Karachi, Pakistan",
  method: 1,
  asr: 0,
  today: null,       // today's times result
  nextName: null,
  nextAt: null,      // Date
  token: localStorage.getItem("waqt_token") || null,
  monthYear: (() => { const d = new Date(); return { y: d.getFullYear(), m: d.getMonth() + 1 }; })(),
};

const $ = (sel) => document.querySelector(sel);
const fmt2 = (n) => String(n).padStart(2, "0");

/* ---------------- helpers ---------------- */
async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  const res = await fetch(API + path, { ...opts, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

/* ---------------- location ---------------- */
async function loadTimes() {
  const q = new URLSearchParams({
    latitude: state.lat,
    longitude: state.lng,
    timezone: state.tz,
    method: state.method,
    asr_juristic: state.asr,
  });
  try {
    const data = await api(`/api/times?${q}`);
    state.today = data;
    renderToday(data);
  } catch (e) {
    $("#next-prayer-name").textContent = "Error";
    $("#next-prayer-time").textContent = "—";
    $("#countdown").textContent = e.message;
  }
}

function renderToday(data) {
  const d = new Date(data.date + "T00:00:00");
  const dateStr = d.toLocaleDateString("en-PK", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  $("#date-line").textContent = dateStr + (data.is_special_day ? " · Jumu'ah" : "");
  $("#badge-city").textContent = state.cityName;
  $("#badge-method").textContent = data.method_name + (data.asr_juristic === 2 ? " · Hanafi Asr" : "");

  const names = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"];
  names.forEach((n, i) => {
    const row = document.querySelectorAll(".time-row")[i];
    row.querySelector(".t-name").textContent = n.charAt(0).toUpperCase() + n.slice(1);
    row.querySelector(".t-time").textContent = data.times[n];
  });

  computeNext(data.times);
}

function computeNext(times) {
  const now = new Date();
  let best = null;
  for (const [name, value] of Object.entries(times)) {
    const [h, m] = value.split(":").map(Number);
    const cand = new Date(now);
    cand.setHours(h, m, 0, 0);
    if (cand <= now) cand.setDate(cand.getDate() + 1);
    if (!best || cand < best.at) best = { name, at: cand };
  }
  state.nextName = best.name;
  state.nextAt = best.at;
  $("#next-prayer-name").textContent = best.name.charAt(0).toUpperCase() + best.name.slice(1);
  $("#next-prayer-time").textContent = `${fmt2(best.at.getHours())}:${fmt2(best.at.getMinutes())}`;
  tick();
}

function tick() {
  const now = new Date();
  const diff = Math.max(0, state.nextAt - now);
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  $("#countdown").textContent = `in ${fmt2(h)}:${fmt2(m)}:${fmt2(s)}`;
  setTimeout(tick, 1000);
}

/* ---------------- city search ---------------- */
async function searchCity(q) {
  if (!q.trim()) { $("#city-results").classList.add("hidden"); return; }
  try {
    const cities = await api(`/api/cities?query=${encodeURIComponent(q)}&limit=8`);
    const ul = $("#city-results");
    ul.innerHTML = "";
    if (!cities.length) {
      const li = document.createElement("li");
      li.textContent = "No matches — pick a nearby city.";
      ul.appendChild(li);
    }
    cities.forEach((c) => {
      const li = document.createElement("li");
      li.innerHTML = `${c.name} <small>${c.country}</small>`;
      li.onclick = () => {
        state.lat = c.lat; state.lng = c.lng; state.tz = c.timezone;
        state.cityName = `${c.name}, ${c.country}`;
        $("#city-search").value = c.name;
        $("#city-results").classList.add("hidden");
        $("#location-display").textContent = `📍 ${state.cityName}`;
        loadTimes();
      };
      ul.appendChild(li);
    });
    ul.classList.remove("hidden");
  } catch (e) { /* ignore */ }
}

/* ---------------- methods ---------------- */
async function loadMethods() {
  try {
    const methods = await api("/api/methods");
    const sel = $("#method-select");
    sel.innerHTML = "";
    methods.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = `${m.name} (${m.region})`;
      if (m.id === 1) opt.selected = true;
      sel.appendChild(opt);
    });
  } catch (_) {}
}

/* ---------------- monthly timetable ---------------- */
async function loadMonth() {
  const { y, m } = state.monthYear;
  $("#month-label").textContent = new Date(y, m - 1, 1).toLocaleDateString("en-PK", { month: "long", year: "numeric" });
  const q = new URLSearchParams({ year: y, month: m, latitude: state.lat, longitude: state.lng, timezone: state.tz, method: state.method, asr_juristic: state.asr });
  try {
    const data = await api(`/api/times/month?${q}`);
    const tbody = $("#month-body");
    tbody.innerHTML = "";
    const todayStr = new Date().toISOString().slice(0, 10);
    data.days.forEach((day) => {
      const tr = document.createElement("tr");
      if (day.is_special_day) tr.classList.add("friday");
      if (day.date === todayStr) tr.classList.add("today-row");
      const d = new Date(day.date + "T00:00:00");
      const label = d.toLocaleDateString("en-PK", { weekday: "short", day: "numeric" });
      tr.innerHTML = `<td>${label}</td><td>${day.times.fajr}</td><td>${day.times.sunrise}</td><td>${day.times.dhuhr}</td><td>${day.times.asr}</td><td>${day.times.maghrib}</td><td>${day.times.isha}</td>`;
      tbody.appendChild(tr);
    });
  } catch (e) {
    $("#month-body").innerHTML = `<tr><td colspan="7">${e.message}</td></tr>`;
  }
}

/* ---------------- qibla ---------------- */
async function loadQibla() {
  try {
    const data = await api(`/api/qibla?latitude=${state.lat}&longitude=${state.lng}`);
    $("#qibla-bearing").textContent = data.bearing_degrees + "°";
    $("#qibla-cardinal").textContent = data.bearing_cardinal;
    drawQibla(data.bearing_degrees);
  } catch (_) {}
}

function drawQibla(bearing) {
  const canvas = $("#qibla-canvas");
  const ctx = canvas.getContext("2d");
  const cx = 150, cy = 150;
  ctx.clearRect(0, 0, 300, 300);

  // rings
  ctx.strokeStyle = "rgba(212,175,55,0.25)";
  ctx.lineWidth = 1;
  [80, 110, 140].forEach((r) => {
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
  });

  // cardinal ticks
  ctx.fillStyle = "#8b94a7";
  ctx.font = "13px Inter, sans-serif";
  ctx.textAlign = "center";
  [["N", 0], ["E", 90], ["S", 180], ["W", 270]].forEach(([label, deg]) => {
    const rad = (deg - 90) * Math.PI / 180;
    const x = cx + Math.cos(rad) * 118;
    const y = cy + Math.sin(rad) * 118;
    ctx.fillText(label, x, y + 4);
  });

  // north needle (white)
  ctx.strokeStyle = "#eef1f6";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx, cy - 105);
  ctx.stroke();

  // qibla needle (gold gradient)
  const rad = (bearing - 90) * Math.PI / 180;
  const grad = ctx.createLinearGradient(cx, cy, cx + Math.cos(rad) * 100, cy + Math.sin(rad) * 100);
  grad.addColorStop(0, "#d4af37");
  grad.addColorStop(1, "#f5e08c");
  ctx.strokeStyle = grad;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + Math.cos(rad) * 105, cy + Math.sin(rad) * 105);
  ctx.stroke();

  // center dot
  ctx.fillStyle = "#f5e08c";
  ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2); ctx.fill();
}

/* ---------------- auth + saved locations ---------------- */
let isRegister = false;

function setAuthUI() {
  const box = $("#auth-box");
  const list = $("#saved-list");
  if (state.token) {
    box.classList.add("hidden");
    list.classList.remove("hidden");
    loadSaved();
  } else {
    box.classList.remove("hidden");
    list.classList.add("hidden");
  }
}

$("#auth-toggle").onclick = () => {
  isRegister = !isRegister;
  $("#auth-name").style.display = isRegister ? "" : "none";
  $("#auth-submit").textContent = isRegister ? "Register" : "Login";
  $("#auth-toggle").textContent = isRegister ? "or Login" : "or Register";
};

$("#auth-form").onsubmit = async (e) => {
  e.preventDefault();
  const msg = $("#auth-msg");
  msg.className = "auth-msg";
  try {
    const body = { email: $("#auth-email").value, password: $("#auth-password").value };
    if (isRegister) body.name = $("#auth-name").value || "User";
    const data = await api(isRegister ? "/api/auth/register" : "/api/auth/login", { method: "POST", body: JSON.stringify(body) });
    state.token = data.access_token;
    localStorage.setItem("waqt_token", data.access_token);
    msg.textContent = isRegister ? "Account created — you're signed in! 🎉" : "Signed in!";
    msg.classList.add("ok");
    setAuthUI();
  } catch (err) {
    msg.textContent = err.message;
    msg.classList.add("err");
  }
};

async function loadSaved() {
  try {
    const rows = await api("/api/locations");
    const list = $("#saved-list");
    list.innerHTML = "";
    if (!rows.length) {
      list.innerHTML = `<p class="hint">No saved locations yet. Tap ♡ Save on the location you use daily.</p>`;
      return;
    }
    rows.forEach((row) => {
      const div = document.createElement("div");
      div.className = "saved-item";
      div.innerHTML = `<div><div class="s-name">${row.name}</div><div class="s-meta">${row.latitude.toFixed(4)}, ${row.longitude.toFixed(4)} · ${row.timezone}</div></div>
        <button title="Delete">✕</button>`;
      div.querySelector(".s-name").onclick = () => {
        state.lat = row.latitude; state.lng = row.longitude; state.tz = row.timezone;
        state.cityName = row.name;
        $("#location-display").textContent = `📍 ${row.name}`;
        loadTimes(); loadQibla(); loadMonth();
      };
      div.querySelector("button").onclick = async () => {
        try { await api(`/api/locations/${row.id}`, { method: "DELETE" }); loadSaved(); } catch (_) {}
      };
      list.appendChild(div);
    });
  } catch (err) {
    $("#saved-list").innerHTML = `<p class="hint err">${err.message}</p>`;
  }
}

$("#btn-save").onclick = async () => {
  if (!state.token) { $("#auth-msg").textContent = "Sign in first to save locations."; $("#auth-msg").className = "auth-msg err"; window.location.hash = "#saved"; return; }
  try {
    await api("/api/locations", {
      method: "POST",
      body: JSON.stringify({ name: state.cityName.split(",")[0], latitude: state.lat, longitude: state.lng, timezone: state.tz }),
    });
    loadSaved();
  } catch (e) {
    $("#auth-msg").textContent = e.message;
    $("#auth-msg").className = "auth-msg err";
  }
};

/* ---------------- events ---------------- */
let searchTimer;
$("#city-search").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => searchCity(e.target.value), 220);
});
$("#method-select").addEventListener("change", (e) => {
  state.method = Number(e.target.value);
  loadTimes(); loadMonth();
});
$("#asr-select").addEventListener("change", (e) => {
  state.asr = Number(e.target.value);
  loadTimes(); loadMonth();
});
$("#prev-month").onclick = () => {
  state.monthYear.m -= 1;
  if (state.monthYear.m === 0) { state.monthYear.m = 12; state.monthYear.y -= 1; }
  loadMonth();
};
$("#next-month").onclick = () => {
  state.monthYear.m += 1;
  if (state.monthYear.m === 13) { state.monthYear.m = 1; state.monthYear.y += 1; }
  loadMonth();
};
$("#qibla").addEventListener("click", () => loadQibla());

/* ---------------- boot ---------------- */
(async function init() {
  $("#location-display").textContent = `📍 ${state.cityName}`;
  loadMethods();
  loadTimes();
  loadMonth();
  loadQibla();
  setAuthUI();
})();
