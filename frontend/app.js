/* ============================================================
   Saarthi — single-page app
   3 pages: Apply / Assistant / Dashboard
   Talks to the FastAPI backend on :8000
   ============================================================ */

const API = "http://localhost:8000/api";
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

// -----------------------------------------------------------
// Router
// -----------------------------------------------------------
const routes = { apply: renderApply, assistant: renderAssistant, dashboard: renderDashboard };
function go() {
  const hash = location.hash.replace(/^#\/?/, "") || "apply";
  const fn = routes[hash] || routes.apply;
  $$(".nav-link").forEach((a) => {
    a.classList.toggle("bg-white/10", a.dataset.route === hash);
    a.classList.toggle("text-brand-200", a.dataset.route === hash);
  });
  $("#page").innerHTML = `<div class="fade-in">${fn()}</div>`;
  if (window.feather) feather.replace();
  if (hash === "dashboard") setTimeout(initDashboard, 50);
  if (hash === "assistant") setTimeout(initAssistant, 50);
  if (hash === "apply")     setTimeout(initApply, 50);
}
window.addEventListener("hashchange", go);

// -----------------------------------------------------------
// API helpers
// -----------------------------------------------------------
async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

const fmtINR = (n) => "₹" + Math.round(n).toLocaleString("en-IN");
const pct    = (n) => (n * 100).toFixed(1) + "%";
const colorFor = (decision) =>
  decision === "approve" ? "emerald" : decision === "refer" ? "amber" : "rose";
const badge = (decision) => {
  const c = colorFor(decision);
  return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-${c}-100 text-${c}-700 border border-${c}-200">
    <span class="w-1.5 h-1.5 rounded-full bg-${c}-500"></span>${decision.toUpperCase()}</span>`;
};

// ============================================================
// PAGE 1: /apply — Customer-facing application
// ============================================================
const PRODUCTS = [
  { type: "Two Wheeler", min: 35000, max: 120000, tenure: 24 },
  { type: "Used Car", min: 150000, max: 600000, tenure: 48 },
  { type: "Tractor", min: 300000, max: 1200000, tenure: 60 },
  { type: "Used Commercial Vehicle", min: 250000, max: 900000, tenure: 48 },
  { type: "Three Wheeler", min: 120000, max: 350000, tenure: 36 },
  { type: "Consumer Durable", min: 8000, max: 60000, tenure: 12 },
  { type: "Personal Loan", min: 30000, max: 200000, tenure: 24 },
  { type: "Mobile Loan", min: 6000, max: 30000, tenure: 9 },
  { type: "Gold Loan", min: 20000, max: 500000, tenure: 12 },
];

function renderApply() {
  return `
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Left: form -->
    <div class="lg:col-span-2">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <h2 class="text-2xl font-bold text-ink-900">Apply for a loan</h2>
        <p class="text-sm text-slate-500 mt-1">Saarthi gives you a decision in under 60 seconds. Fill in your details — your data is safe and used only for this application.</p>

        <form id="applyForm" class="mt-6 space-y-6">

          <!-- Step 1: Personal -->
          <fieldset>
            <legend class="text-sm font-semibold text-ink-700 mb-3">1. Personal</legend>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label class="block">
                <span class="text-xs text-slate-600">Age</span>
                <input type="number" name="age" value="34" min="18" max="80" required class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" />
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Monthly income (₹)</span>
                <input type="number" name="monthly_income_inr" value="28000" min="2000" required class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" />
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Employment</span>
                <select name="employment" class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500">
                  <option>Salaried</option><option>Self Employed Business</option>
                  <option selected>Farmer</option><option>Daily Wage</option>
                  <option>Gig Worker</option><option>Driver</option><option>Homemaker</option>
                </select>
              </label>
            </div>
          </fieldset>

          <!-- Step 2: Loan -->
          <fieldset>
            <legend class="text-sm font-semibold text-ink-700 mb-3">2. Loan</legend>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label class="block">
                <span class="text-xs text-slate-600">Loan type</span>
                <select id="loanType" name="loan_type" class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500">
                  ${PRODUCTS.map(p => `<option value="${p.type}" ${p.type==='Tractor'?'selected':''}>${p.type}</option>`).join("")}
                </select>
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Loan amount (₹)</span>
                <input type="number" name="loan_amount_inr" id="loanAmount" value="450000" min="1000" required class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" />
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Tenure (months)</span>
                <input type="number" name="loan_tenure_months" id="loanTenure" value="60" min="1" max="120" required class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" />
              </label>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              <label class="block">
                <span class="text-xs text-slate-600">State</span>
                <select name="state" class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500">
                  ${["Tamil Nadu","Karnataka","Maharashtra","UP","Bihar","Rajasthan","Gujarat","MP","West Bengal","Andhra","Telangana"].map(s => `<option ${s==='Tamil Nadu'?'selected':''}>${s}</option>`).join("")}
                </select>
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">District</span>
                <input type="text" name="district" value="Madurai" class="mt-1 w-full rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" />
              </label>
            </div>
          </fieldset>

          <!-- Step 3: Agri (toggle based on Farmer/Tractor) -->
          <fieldset id="agriBox" class="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <legend class="text-sm font-semibold text-emerald-800 mb-3">3. Agricultural (auto-shown for farmers / tractor loans)</legend>
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <label class="block">
                <span class="text-xs text-slate-600">Land (acres)</span>
                <input type="number" name="land_acres" value="4.5" step="0.1" class="mt-1 w-full rounded-lg border-emerald-300" />
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Crop</span>
                <select name="crop_type" class="mt-1 w-full rounded-lg border-emerald-300">
                  ${["Paddy","Wheat","Sugarcane","Cotton","Maize","Groundnut","Soybean","Vegetables","Pulses"].map(c => `<option ${c==='Paddy'?'selected':''}>${c}</option>`).join("")}
                </select>
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">NDVI (0-1)</span>
                <input type="number" name="ndvi_score" value="0.72" min="0" max="1" step="0.01" class="mt-1 w-full rounded-lg border-emerald-300" />
              </label>
              <label class="block">
                <span class="text-xs text-slate-600">Rainfall 30d (mm)</span>
                <input type="number" name="rainfall_30d_mm" value="-12" class="mt-1 w-full rounded-lg border-emerald-300" />
              </label>
            </div>
            <p class="text-[11px] text-emerald-700 mt-2">NDVI & rainfall are mock values for the demo. In production, Saarthi pulls from Sentinel-2 satellite + IMD weather APIs in real time.</p>
          </fieldset>

          <div class="flex items-center gap-3 pt-2">
            <button type="submit" id="scoreBtn" class="px-6 py-3 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold hover:from-brand-600 hover:to-brand-700 shadow-lg shadow-brand-500/20 transition">Run Saarthi Score →</button>
            <button type="button" id="loadDemoBtn" class="px-4 py-3 rounded-lg bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 text-sm">Load demo applicant</button>
            <span id="applyError" class="text-rose-600 text-sm"></span>
          </div>
        </form>
      </div>
    </div>

    <!-- Right: live results panel -->
    <div class="lg:col-span-1">
      <div id="scoreResult" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 min-h-[400px]">
        <div class="text-center text-slate-400 mt-12">
          <div class="text-5xl mb-3">🤖</div>
          <p class="text-sm">Submit the form to see Saarthi's decision, score breakdown, and loan recommendation here.</p>
        </div>
      </div>
    </div>
  </div>
  `;
}

function initApply() {
  const form = $("#applyForm");
  if (!form) return;

  // loan type presets
  $("#loanType").addEventListener("change", (e) => {
    const p = PRODUCTS.find(p => p.type === e.target.value);
    if (p) {
      $("#loanAmount").value = Math.round((p.min + p.max) / 2 / 1000) * 1000;
      $("#loanTenure").value = p.tenure;
    }
  });

  // demo loader
  $("#loadDemoBtn").addEventListener("click", () => {
    form.age.value = 34;
    form.monthly_income_inr.value = 28000;
    form.employment.value = "Farmer";
    form.loan_type.value = "Tractor";
    form.loan_amount_inr.value = 450000;
    form.loan_tenure_months.value = 60;
    form.state.value = "Tamil Nadu";
    form.district.value = "Madurai";
    form.land_acres.value = 4.5;
    form.crop_type.value = "Paddy";
    form.ndvi_score.value = 0.72;
    form.rainfall_30d_mm.value = -12;
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const data = Object.fromEntries(fd.entries());
    // numeric coercion
    ["age","monthly_income_inr","loan_amount_inr","loan_tenure_months","land_acres","ndvi_score","rainfall_30d_mm"]
      .forEach(k => data[k] = parseFloat(data[k] || 0));
    data.is_agricultural = (data.employment === "Farmer" || data.loan_type === "Tractor") ? 1 : 0;
    // default fraud fields (not shown in UI for brevity)
    data.existing_loans = 0; data.default_history = 0; data.dti = 0;
    data.app_velocity_30d = 1; data.email_age_days = 800; data.phone_age_days = 600;
    data.ip_geo_mismatch = 0; data.device_shared_count_30d = 0; data.disposable_email = 0;
    data.device = "Android-Samsung"; data.browser = "Chrome";
    data.email = "demo@saarthi.in"; data.phone = "+919999999999"; data.name = "Demo Applicant";

    $("#scoreBtn").disabled = true;
    $("#scoreBtn").textContent = "Scoring…";
    try {
      const r = await api("/score", { method: "POST", body: data });
      renderScoreResult(r);
    } catch (err) {
      $("#applyError").textContent = "Error: " + err.message;
    } finally {
      $("#scoreBtn").disabled = false;
      $("#scoreBtn").textContent = "Run Saarthi Score →";
    }
  });
}

function renderScoreResult(r) {
  const decision = r.decision;
  const c = colorFor(decision);
  const ring = c === "emerald" ? "from-emerald-400 to-emerald-600" : c === "amber" ? "from-amber-400 to-amber-600" : "from-rose-400 to-rose-600";
  const rec = r.loan_recommendation;

  // SHAP bars
  const maxAbs = Math.max(...r.top_3_reasons.map(x => Math.abs(x.contribution)));
  const reasons = r.top_3_reasons.map(x => {
    const w = (Math.abs(x.contribution) / maxAbs) * 100;
    const sign = x.contribution >= 0 ? "bg-emerald-500" : "bg-rose-500";
    const label = x.contribution >= 0 ? "↑" : "↓";
    return `
      <div>
        <div class="flex items-center justify-between text-[11px] text-slate-600 mb-1">
          <span class="font-mono">${x.feature}</span>
          <span class="${x.contribution>=0?'text-emerald-700':'text-rose-700'} font-semibold">${label} ${Math.abs(x.contribution).toFixed(1)}</span>
        </div>
        <div class="bg-slate-100 rounded h-2 overflow-hidden">
          <div class="shap-bar ${sign} bar" style="width:${w.toFixed(1)}%"></div>
        </div>
      </div>`;
  }).join("");

  const fraudBlock = r.fraud_flags.length === 0
    ? `<div class="flex items-center gap-2 text-emerald-700 text-sm"><span class="w-2 h-2 rounded-full bg-emerald-500"></span>No risk signals — clean</div>`
    : `<div class="space-y-1">
        <div class="text-rose-700 text-sm font-semibold">⚠ ${r.fraud_flags.length} risk signal${r.fraud_flags.length>1?'s':''}</div>
        <ul class="text-xs text-slate-700 list-disc list-inside space-y-0.5">
          ${r.fraud_flags.map(f => `<li>${f}</li>`).join("")}
        </ul>
      </div>`;

  $("#scoreResult").innerHTML = `
    <div class="text-center mb-4">
      <div class="text-[11px] uppercase tracking-widest text-slate-500">Saarthi Decision</div>
      <div class="mt-2 inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br ${ring} text-white text-3xl font-bold ring-brand">
        ${Math.round(r.credit_score)}
      </div>
      <div class="mt-2 text-xs text-slate-500">Credit Score (300-900)</div>
      <div class="mt-3">${badge(decision)}</div>
    </div>

    <div class="grid grid-cols-3 gap-2 mb-4 text-center">
      <div class="bg-slate-50 rounded-lg p-2">
        <div class="text-[10px] text-slate-500 uppercase">Default Risk</div>
        <div class="text-lg font-bold ${r.default_probability > 0.20 ? 'text-rose-600' : r.default_probability > 0.08 ? 'text-amber-600' : 'text-emerald-600'}">${pct(r.default_probability)}</div>
      </div>
      <div class="bg-slate-50 rounded-lg p-2">
        <div class="text-[10px] text-slate-500 uppercase">Fraud Score</div>
        <div class="text-lg font-bold ${r.fraud_score > 0.5 ? 'text-rose-600' : r.fraud_score > 0.25 ? 'text-amber-600' : 'text-emerald-600'}">${r.fraud_score.toFixed(2)}</div>
      </div>
      <div class="bg-slate-50 rounded-lg p-2">
        <div class="text-[10px] text-slate-500 uppercase">Anomaly</div>
        <div class="text-lg font-bold ${r.anomaly_score < 0 ? 'text-rose-600' : 'text-slate-700'}">${r.anomaly_score.toFixed(2)}</div>
      </div>
    </div>

    <div class="border-t border-slate-200 pt-4 mb-4">
      <div class="text-[11px] uppercase tracking-widest text-slate-500 mb-2">Why this score (top 3 reasons)</div>
      <div class="space-y-2">${reasons}</div>
    </div>

    <div class="border-t border-slate-200 pt-4 mb-4">
      <div class="text-[11px] uppercase tracking-widest text-slate-500 mb-2">Fraud signals</div>
      ${fraudBlock}
    </div>

    <div class="border-t border-slate-200 pt-4">
      <div class="text-[11px] uppercase tracking-widest text-slate-500 mb-2">Loan recommendation</div>
      <div class="grid grid-cols-2 gap-2 text-sm">
        <div class="bg-brand-50 rounded-lg p-2"><div class="text-[10px] text-slate-500 uppercase">Max eligible</div><div class="font-bold text-brand-800">${fmtINR(rec.max_eligible_amount)}</div></div>
        <div class="bg-brand-50 rounded-lg p-2"><div class="text-[10px] text-slate-500 uppercase">EMI / month</div><div class="font-bold text-brand-800">${fmtINR(rec.monthly_emi_inr)}</div></div>
        <div class="bg-slate-50 rounded-lg p-2"><div class="text-[10px] text-slate-500 uppercase">Tenure</div><div class="font-semibold">${rec.suggested_tenure_months} mo</div></div>
        <div class="bg-slate-50 rounded-lg p-2"><div class="text-[10px] text-slate-500 uppercase">Rate</div><div class="font-semibold">${rec.suggested_interest_rate_pct}% p.a.</div></div>
      </div>
    </div>

    <a href="#/assistant" class="block text-center mt-5 text-sm text-brand-700 hover:underline">💬 Ask Saarthi about this decision →</a>
  `;
}

// ============================================================
// PAGE 2: /assistant — GenAI chat
// ============================================================
function renderAssistant() {
  return `
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col" style="height: 70vh">
        <div class="p-4 border-b border-slate-200 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold text-lg">सा</div>
          <div>
            <div class="font-semibold">Saarthi Assistant</div>
            <div class="text-xs text-slate-500">Hindi-English · trained on TVS Credit policies</div>
          </div>
          <div class="ml-auto text-xs text-slate-500">
            <span class="inline-flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-500"></span>${CHAT.applicant_id ? `Applicant: ${CHAT.applicant_id}` : "Demo applicant"}</span>
          </div>
        </div>
        <div id="chatLog" class="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin"></div>
        <form id="chatForm" class="p-3 border-t border-slate-200 flex gap-2">
          <input id="chatInput" type="text" placeholder="Ask: 'Will I get a tractor loan?' / 'EMI kitni hogi?' / 'Documents kya chahiye?'" class="flex-1 rounded-lg border-slate-300 focus:border-brand-500 focus:ring-brand-500" required />
          <button class="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold hover:bg-brand-700">Send</button>
        </form>
      </div>
    </div>

    <div class="lg:col-span-1 space-y-4">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
        <div class="text-xs uppercase tracking-widest text-slate-500 mb-2">Try a question</div>
        <div class="flex flex-col gap-2">
          ${["Will I get a tractor loan for ₹4.5L?","EMI kitni hogi monthly?","Documents kya chahiye?","Mera fraud score kya hai?","Interest rate kya hoga?"].map(q => `<button class="chip text-left text-sm px-3 py-2 rounded-lg bg-slate-50 hover:bg-brand-50 border border-slate-200">${q}</button>`).join("")}
        </div>
      </div>
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
        <div class="text-xs uppercase tracking-widest text-slate-500 mb-2">How Saarthi works</div>
        <ol class="text-sm text-slate-700 space-y-2 list-decimal list-inside">
          <li>Saarthi calls <span class="font-mono text-xs bg-slate-100 px-1 rounded">score_applicant()</span> with your profile.</li>
          <li>Pulls from credit, default, fraud models (live).</li>
          <li>Looks up relevant product docs (RAG).</li>
          <li>Composes a friendly, explainable reply.</li>
        </ol>
        <p class="text-[11px] text-slate-500 mt-3">${window.GEMINI_KEY ? "Using Gemini 1.5 Flash" : "Using built-in rule-based fallback (no Gemini key)"}</p>
      </div>
    </div>
  </div>
  `;
}

const CHAT = { history: [], applicant_id: "APP000011" };

function initAssistant() {
  // Load first message
  $("#chatLog").innerHTML = `
    <div class="flex gap-2">
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold flex-shrink-0">सा</div>
      <div class="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-md text-sm">
        Namaste! 🙏 Main Saarthi hoon, aapka AI loan assistant. Aapka application pehla review kar chuka hoon — kuch sawaal poochiye:
        <ul class="list-disc list-inside mt-2 space-y-1 text-xs">
          <li>Will I get a tractor loan for ₹4.5L?</li>
          <li>EMI kitni hogi monthly?</li>
          <li>Documents kya chahiye?</li>
          <li>Mera fraud score kya hai?</li>
        </ul>
      </div>
    </div>
  `;

  $$(".chip").forEach(c => c.addEventListener("click", () => {
    $("#chatInput").value = c.textContent.trim();
    $("#chatForm").dispatchEvent(new Event("submit", { cancelable: true }));
  }));

  $("#chatForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = $("#chatInput").value.trim();
    if (!msg) return;
    $("#chatInput").value = "";
    addChat("user", msg);
    addChat("assistant", "…", true);
    try {
      const r = await api("/chat", { method: "POST", body: {
        message: msg, applicant_id: CHAT.applicant_id, history: CHAT.history,
      }});
      // remove the "…" placeholder
      const log = $("#chatLog");
      log.lastElementChild.remove();
      addChat("assistant", r.reply);
      CHAT.history.push({ role: "user", content: msg });
      CHAT.history.push({ role: "assistant", content: r.reply });
      if (r.fallback) {
        addChatMeta(`⚙️ Used built-in fallback (no Gemini key) — score: ${r.tool_calls[0]?.result?.credit_score?.toFixed(0) || "?"}`);
      } else {
        addChatMeta("✨ Powered by Gemini 1.5 Flash + live ML");
      }
    } catch (err) {
      $("#chatLog").lastElementChild.remove();
      addChat("assistant", "Sorry, error: " + err.message);
    }
  });
}

function addChat(role, text, isPlaceholder = false) {
  const isUser = role === "user";
  const log = $("#chatLog");
  const wrap = document.createElement("div");
  wrap.className = `flex gap-2 ${isUser ? 'justify-end' : ''}`;
  wrap.innerHTML = isUser
    ? `<div class="bg-brand-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-md text-sm">${escapeHtml(text)}</div>`
    : `<div class="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white flex items-center justify-center font-bold flex-shrink-0">सा</div>
       <div class="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-md text-sm ${isPlaceholder ? 'opacity-60' : ''}">${escapeHtml(text)}</div>`;
  log.appendChild(wrap);
  log.scrollTop = log.scrollHeight;
}
function addChatMeta(text) {
  const log = $("#chatLog");
  const m = document.createElement("div");
  m.className = "text-[10px] text-slate-400 text-center";
  m.textContent = text;
  log.appendChild(m);
}
function escapeHtml(s) { return s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

// ============================================================
// PAGE 3: /dashboard — Underwriter view
// ============================================================
function renderDashboard() {
  return `
  <div class="space-y-6">
    <!-- KPI strip -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4" id="kpiStrip">
      ${["Total Applications","Approval Rate","Avg Credit Score","High Fraud","Avg Loan Amount"].map(label => `
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
          <div class="text-[10px] uppercase tracking-widest text-slate-500">${label}</div>
          <div class="text-2xl font-bold mt-1 text-slate-400">…</div>
        </div>
      `).join("")}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Map -->
      <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h3 class="font-bold text-ink-900">Risk by State</h3>
            <p class="text-xs text-slate-500">Avg default probability, last 30 days</p>
          </div>
          <div class="flex items-center gap-3 text-[11px] text-slate-500">
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-emerald-400"></span>Low (&lt;5%)</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-amber-400"></span>Med (5-15%)</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-rose-500"></span>High (&gt;15%)</span>
          </div>
        </div>
        <div id="map"></div>
      </div>

      <!-- Live feed -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 flex flex-col" style="max-height: 460px">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-bold text-ink-900">Live Applications</h3>
          <span class="flex items-center gap-1 text-xs text-emerald-600"><span class="w-2 h-2 rounded-full bg-emerald-500 live-dot"></span>Streaming</span>
        </div>
        <div id="liveFeed" class="space-y-2 overflow-y-auto scrollbar-thin flex-1"></div>
      </div>
    </div>

    <!-- All apps table -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-bold text-ink-900">Recent Applications (drill into any row)</h3>
        <button id="refreshTable" class="text-xs text-brand-600 hover:underline">↻ Refresh</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="text-[11px] text-slate-500 uppercase border-b border-slate-200">
            <tr>
              <th class="text-left py-2">ID</th>
              <th class="text-left">Name</th>
              <th class="text-left">State</th>
              <th class="text-left">Loan</th>
              <th class="text-right">Amount</th>
              <th class="text-right">Score</th>
              <th class="text-right">Default</th>
              <th class="text-right">Fraud</th>
              <th class="text-center">Decision</th>
            </tr>
          </thead>
          <tbody id="appsTable"></tbody>
        </table>
      </div>
    </div>
  </div>
  `;
}

async function initDashboard() {
  // KPIs
  try {
    const stats = await api("/portfolio/stats");
    const cells = [
      { v: stats.total_applicants.toLocaleString(), c: "ink" },
      { v: pct(stats.approval_rate), c: "emerald" },
      { v: stats.avg_credit_score, c: "ink" },
      { v: stats.high_fraud_count, c: "rose" },
      { v: fmtINR(stats.avg_loan_amount_inr), c: "ink" },
    ];
    $$("#kpiStrip > div").forEach((card, i) => {
      card.querySelector(".text-2xl").textContent = cells[i].v;
      card.querySelector(".text-2xl").classList.remove("text-slate-400");
      card.querySelector(".text-2xl").classList.add(`text-${cells[i].c}-600`);
    });
  } catch (e) { console.warn(e); }

  // Map
  try {
    const region = await api("/portfolio/region-risk");
    drawMap(region.states);
  } catch (e) { console.warn(e); }

  // Table
  await loadAppsTable();

  $("#refreshTable").addEventListener("click", loadAppsTable);

  // Live feed: random applicant every 3 seconds
  startLiveFeed();
}

let liveTimer = null;
function startLiveFeed() {
  if (liveTimer) clearInterval(liveTimer);
  const feed = $("#liveFeed");
  if (!feed) return;
  liveTimer = setInterval(async () => {
    try {
      const apps = await api("/applicants/random?n=1");
      const a = apps[0];
      addLiveApp(a);
    } catch {}
  }, 3000);
  // seed with a few immediately
  api("/applicants/random?n=4").then(apps => apps.forEach(addLiveApp));
}
function addLiveApp(a) {
  const feed = $("#liveFeed");
  if (!feed) return;
  const c = colorFor(a.outcome === 1 ? "approve" : a.outcome === 2 ? "refer" : "reject");
  const el = document.createElement("div");
  el.className = "border border-slate-200 rounded-lg p-2.5 bg-slate-50 fade-in";
  el.innerHTML = `
    <div class="flex items-center justify-between">
      <div>
        <div class="text-[11px] text-slate-500">${a.applicant_id} · ${a.district}, ${a.state}</div>
        <div class="text-sm font-semibold">${a.loan_type} · ${fmtINR(a.loan_amount_inr)}</div>
      </div>
      <div class="text-right">
        ${badge(a.outcome === 1 ? "approve" : a.outcome === 2 ? "refer" : "reject")}
        <div class="text-[10px] text-slate-500 mt-1">CIBIL ${a.cibil_score} · D ${pct(a.default_probability)}</div>
      </div>
    </div>`;
  feed.prepend(el);
  while (feed.children.length > 30) feed.lastElementChild.remove();
}

async function loadAppsTable() {
  const tbody = $("#appsTable");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="9" class="text-center text-slate-400 py-6">Loading…</td></tr>`;
  try {
    const apps = await api("/applicants/random?n=20");
    tbody.innerHTML = apps.map(a => {
      const dec = a.outcome === 1 ? "approve" : a.outcome === 2 ? "refer" : "reject";
      const c = colorFor(dec);
      return `<tr class="border-b border-slate-100 hover:bg-slate-50 cursor-pointer" data-id="${a.applicant_id}">
        <td class="py-2 font-mono text-xs text-slate-500">${a.applicant_id}</td>
        <td>${a.name}</td>
        <td>${a.state}</td>
        <td>${a.loan_type}</td>
        <td class="text-right">${fmtINR(a.loan_amount_inr)}</td>
        <td class="text-right font-mono">${a.cibil_score}</td>
        <td class="text-right font-mono ${a.default_probability > 0.20 ? 'text-rose-600 font-semibold' : a.default_probability > 0.10 ? 'text-amber-600' : 'text-emerald-600'}">${pct(a.default_probability)}</td>
        <td class="text-right font-mono ${a.fraud_score > 0.5 ? 'text-rose-600 font-semibold' : ''}">${a.fraud_score.toFixed(2)}</td>
        <td class="text-center">${badge(dec)}</td>
      </tr>`;
    }).join("");
    tbody.querySelectorAll("tr").forEach(row => {
      row.addEventListener("click", async () => {
        const id = row.dataset.id;
        CHAT.applicant_id = id;
        location.hash = "#/assistant";
        // give router time, then pre-seed a question
        setTimeout(() => {
          const inp = $("#chatInput");
          if (inp) { inp.value = `Review applicant ${id} — what are the key risks?`; }
        }, 100);
      });
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-rose-500 py-6">Error loading: ${e.message}</td></tr>`;
  }
}

function drawMap(states) {
  const map = L.map('map', { scrollWheelZoom: false }).setView([22.5, 80], 5);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap, © CartoDB',
    subdomains: 'abcd',
    maxZoom: 8,
  }).addTo(map);

  // Place a circle per state centroid (approx lat/lng per state)
  const centers = {
    "Tamil Nadu":[10.8,78.7], "Karnataka":[14.5,75.7], "Maharashtra":[19.5,76.0],
    "UP":[27.0,80.5], "Bihar":[25.8,85.5], "Rajasthan":[26.5,73.5],
    "Gujarat":[22.5,71.5], "MP":[23.5,77.0], "West Bengal":[24.0,88.0],
    "Andhra":[16.0,80.0], "Telangana":[17.5,79.0],
  };
  states.forEach(s => {
    const c = centers[s.state];
    if (!c) return;
    const d = s.avg_default_prob;
    const color = d > 0.15 ? "#e11d48" : d > 0.05 ? "#f59e0b" : "#10b981";
    const radius = Math.max(8, Math.min(40, s.applications / 20));
    L.circleMarker(c, {
      radius, color, fillColor: color, fillOpacity: 0.55, weight: 2,
    }).addTo(map)
      .bindPopup(`<div class="text-sm">
        <div class="font-bold">${s.state}</div>
        <div>Applications: <b>${s.applications}</b></div>
        <div>Avg CIBIL: <b>${s.avg_credit_score.toFixed(0)}</b></div>
        <div>Avg default: <b style="color:${color}">${pct(d)}</b></div>
        <div>High-risk count: <b>${s.high_risk}</b></div>
      </div>`);
  });
}

// -----------------------------------------------------------
// Initial route
// -----------------------------------------------------------
go();
