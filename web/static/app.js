// SlothDesk Cybernetic Editorial Frontend Controller
// Built with Stitch Design System

let currentCategoryFilter = null;
let currentSearchQuery = "";
let allCachedFiles = [];

document.addEventListener("DOMContentLoaded", () => {
  fetchStatus();
  fetchStats();
  fetchFiles();

  // Polling loop every 4 seconds
  setInterval(() => {
    fetchStats();
    fetchFiles();
  }, 4000);

  setupDragAndDrop();
});

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const pill = document.getElementById("ai-provider-text");
    const badge = document.getElementById("model-badge");
    if (data.ai && data.ai.online) {
      const model = data.ai.active_model || "Ollama";
      if (pill) pill.textContent = `LOCAL: ${model.toUpperCase()}`;
      if (badge) badge.textContent = `ON-DEVICE LLM: ${model.toUpperCase()} (LOCAL)`;
    } else {
      if (pill) pill.textContent = "EMBEDDED OPEN NLP";
      if (badge) badge.textContent = "ON-DEVICE OPEN NLP (AIRGAP VERIFIED)";
    }
  } catch (err) {
    console.error("Status fetch error:", err);
  }
}

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const stats = await res.json();

    const napsEl = document.getElementById("metric-naps");
    const minEl = document.getElementById("metric-minutes");
    const calEl = document.getElementById("metric-calories");
    const dolEl = document.getElementById("metric-dollars");
    const rankEl = document.getElementById("sloth-rank");
    const recordCountEl = document.getElementById("telemetry-record-count");

    if (napsEl) napsEl.textContent = stats.naps_earned.toFixed(1);
    if (minEl) minEl.textContent = `${stats.minutes_saved} m`;
    if (calEl) calEl.textContent = `${stats.calories_saved} kcal`;
    if (dolEl) dolEl.textContent = `$${stats.dollars_saved_vs_cloud.toFixed(2)}`;
    if (rankEl) rankEl.textContent = stats.sloth_level;
    if (recordCountEl) recordCountEl.textContent = `${stats.total_files_processed} records indexed`;

    // Visual Bar Updates
    const barNaps = document.getElementById("bar-naps");
    const barMin = document.getElementById("bar-minutes");
    const barCal = document.getElementById("bar-calories");
    const barDol = document.getElementById("bar-dollars");

    if (barNaps) barNaps.style.width = `${Math.min(stats.naps_earned * 20, 100)}%`;
    if (barMin) barMin.style.width = `${Math.min(stats.minutes_saved * 1.5, 100)}%`;
    if (barCal) barCal.style.width = `${Math.min(stats.calories_saved * 1.0, 100)}%`;
    if (barDol) barDol.style.width = `${Math.min(stats.dollars_saved_vs_cloud * 150, 100)}%`;

  } catch (err) {
    console.error("Stats fetch error:", err);
  }
}

async function fetchFiles() {
  try {
    const url = currentCategoryFilter ? `/api/files?category=${encodeURIComponent(currentCategoryFilter)}` : "/api/files";
    const res = await fetch(url);
    const files = await res.json();
    allCachedFiles = files;
    applyFiltersAndRender();
  } catch (err) {
    console.error("Files fetch error:", err);
  }
}

function handleQuickFilter(val) {
  currentSearchQuery = val.toLowerCase().trim();
  applyFiltersAndRender();
}

function applyFiltersAndRender() {
  let filtered = allCachedFiles;
  if (currentCategoryFilter) {
    filtered = filtered.filter(f => f.category === currentCategoryFilter);
  }
  if (currentSearchQuery) {
    filtered = filtered.filter(f => {
      const haystack = `${f.current_name} ${f.original_name} ${f.category} ${f.summary} ${(f.tags || []).join(' ')}`.toLowerCase();
      return haystack.includes(currentSearchQuery);
    });
  }

  const countBadge = document.getElementById("active-files-count");
  if (countBadge) countBadge.textContent = `${filtered.length} FILES`;

  renderFiles(filtered);
}

function renderFiles(files) {
  const container = document.getElementById("files-list");
  if (!container) return;

  if (!files || files.length === 0) {
    container.innerHTML = `
      <div class="text-center py-16 p-6 rounded-lg border border-dashed border-white/10 bg-[#070a10]">
        <span class="material-symbols-outlined text-[36px] text-outline block mb-2">hotel</span>
        <h4 class="font-headline font-semibold text-white text-sm">Clutter Vault Clear // Daemon Standby</h4>
        <p class="text-xs font-mono text-outline mt-1 max-w-sm mx-auto">
          No files pending in this category. Click "Demo Chaos" above or drop files into the ingestion zone.
        </p>
      </div>
    `;
    return;
  }

  const categoryStyles = {
    finance: { border: "border-amber-400/30", bg: "bg-amber-400/10", text: "text-amber-400", icon: "receipt_long" },
    work: { border: "border-cyan-400/30", bg: "bg-cyan-400/10", text: "text-cyan-400", icon: "slideshow" },
    personal: { border: "border-purple-400/30", bg: "bg-purple-400/10", text: "text-purple-400", icon: "medical_services" },
    code: { border: "border-indigo-400/30", bg: "bg-indigo-400/10", text: "text-indigo-400", icon: "code" },
    reading: { border: "border-teal-400/30", bg: "bg-teal-400/10", text: "text-teal-400", icon: "menu_book" },
    media: { border: "border-orange-400/30", bg: "bg-orange-400/10", text: "text-orange-400", icon: "image" }
  };

  container.innerHTML = files.map(file => {
    const cat = categoryStyles[file.category] || { border: "border-white/20", bg: "bg-white/5", text: "text-white", icon: "description" };
    
    const actionBadge = file.action_required ? `
      <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
        <span class="material-symbols-outlined text-[12px]">warning</span>
        ${escapeHtml(file.action_note || "ACTION REQUIRED")}
      </span>
    ` : "";

    const tagChips = (file.tags || []).map(t => `
      <span class="px-1.5 py-0.2 rounded bg-white/4 text-outline text-[9px] font-mono border border-white/6">#${escapeHtml(t)}</span>
    `).join("");

    return `
      <div class="glass-plate p-3.5 sm:p-4 rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 group">
        <div class="flex items-start gap-3 flex-1">
          <div class="w-8 h-8 rounded bg-[#101422] border border-white/10 flex items-center justify-center ${cat.text} shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-[18px]">${cat.icon}</span>
          </div>

          <div class="space-y-1 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono text-xs font-semibold text-white group-hover:text-primary transition-colors tracking-tight">
                ${escapeHtml(file.current_name)}
              </span>
              <span class="text-[10px] font-mono text-outline">
                ${(file.file_size_bytes / 1024).toFixed(1)} KB
              </span>
              <span class="px-2 py-0.2 rounded ${cat.bg} ${cat.text} border ${cat.border} text-[9px] font-mono uppercase tracking-wider font-semibold">
                ${escapeHtml(file.category)}
              </span>
              ${actionBadge}
            </div>

            <!-- Sloth TL;DR Box -->
            <p class="text-xs text-on-surface-variant leading-relaxed">
              <span class="text-primary font-mono text-[10px] font-semibold uppercase">Sloth TL;DR:</span>
              "${escapeHtml(file.summary)}"
            </p>

            <!-- Tags & Original Name Breadcrumb -->
            <div class="flex flex-wrap items-center gap-2 pt-0.5">
              <span class="text-[9px] font-mono text-outline">Orig: <code class="text-white/60">${escapeHtml(file.original_name)}</code></span>
              ${tagChips}
            </div>
          </div>
        </div>

        <!-- Trailing Actions -->
        <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
          <button onclick="undoSingleFile(${file.id})" title="Undo move" class="px-2.5 py-1 rounded bg-[#0b0e16] hover:bg-[#121724] border border-white/10 hover:border-white/20 text-on-surface-variant hover:text-white text-[11px] font-mono transition-all flex items-center gap-1 cursor-pointer">
            <span class="material-symbols-outlined text-[13px]">undo</span>
            <span>Undo</span>
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function filterCategory(cat) {
  currentCategoryFilter = cat;
  document.querySelectorAll(".category-btn").forEach(btn => {
    btn.classList.remove("active", "bg-primary", "text-white");
    btn.classList.add("bg-[#0e121c]", "text-on-surface-variant");
  });

  const target = event.currentTarget;
  target.classList.add("active", "bg-primary", "text-white");
  target.classList.remove("bg-[#0e121c]", "text-on-surface-variant");

  applyFiltersAndRender();
}

function switchTab(tab) {
  const tabs = ["feed", "ask", "drop"];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) el.classList.add("hidden");

    const navBtn = document.getElementById(`nav-btn-${t}`);
    if (navBtn) {
      navBtn.className = "text-on-surface-variant hover:text-white transition-colors";
    }

    const sideBtn = document.getElementById(`side-nav-${t}`);
    if (sideBtn) {
      sideBtn.className = "w-full flex items-center gap-2.5 px-3 py-2 text-on-surface-variant hover:text-white hover:bg-white/4 rounded text-left transition-colors cursor-pointer";
    }
  });

  const activeTabEl = document.getElementById(`tab-${tab}`);
  if (activeTabEl) activeTabEl.classList.remove("hidden");

  const activeNav = document.getElementById(`nav-btn-${tab}`);
  if (activeNav) {
    activeNav.className = "text-secondary border-b-2 border-secondary pb-0.5 font-semibold transition-colors";
  }

  const activeSide = document.getElementById(`side-nav-${tab}`);
  if (activeSide) {
    activeSide.className = "w-full flex items-center gap-2.5 px-3 py-2 text-primary bg-[#101524] border-l-2 border-primary rounded-r text-left transition-colors cursor-pointer";
  }
}

async function triggerTidy() {
  const btn = document.getElementById("btn-tidy");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined text-[15px] animate-spin">refresh</span><span>Tidying...</span>`;
  try {
    const res = await fetch("/api/tidy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    await res.json();
    await fetchStats();
    await fetchFiles();
  } catch (err) {
    console.error("Tidy failed:", err);
  } finally {
    btn.innerHTML = origText;
  }
}

async function populateDemoClutter() {
  const btn = document.getElementById("btn-demo");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined text-[14px] animate-spin">refresh</span><span>Dropping...</span>`;
  try {
    await fetch("/api/populate-demo", { method: "POST" });
    await triggerTidy();
  } catch (err) {
    console.error("Demo failed:", err);
  } finally {
    btn.innerHTML = origText;
  }
}

async function triggerUndo() {
  try {
    await fetch("/api/undo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    fetchStats();
    fetchFiles();
  } catch (err) {
    console.error("Undo error:", err);
  }
}

async function undoSingleFile(fileId) {
  try {
    await fetch("/api/undo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: fileId })
    });
    fetchStats();
    fetchFiles();
  } catch (err) {
    console.error("Single undo error:", err);
  }
}

function setQuery(text) {
  document.getElementById("ask-input").value = text;
  handleAsk(new Event("submit"));
}

async function handleAsk(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("ask-input");
  const query = input.value.trim();
  if (!query) return;

  const btn = document.getElementById("ask-btn");
  btn.disabled = true;
  btn.textContent = "Querying...";

  const box = document.getElementById("ask-response-box");
  const answerEl = document.getElementById("rag-answer");
  const verdictEl = document.getElementById("rag-verdict");
  const sourcesEl = document.getElementById("rag-sources");

  try {
    const t0 = performance.now();
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const t1 = performance.now();
    const data = await res.json();

    box.classList.remove("hidden");
    answerEl.textContent = data.answer;
    verdictEl.textContent = `${Math.round(t1 - t0)}ms • Local Neural`;

    if (data.matched_files && data.matched_files.length > 0) {
      sourcesEl.innerHTML = `
        <div class="font-bold text-white/70 mb-0.5">REFERENCED VECTORS:</div>
        ${data.matched_files.map(f => `
          <div class="flex items-center justify-between text-outline">
            <span class="text-tertiary">→ ${escapeHtml(f.name || f.current_name)}</span>
            <span>[${f.category}]</span>
          </div>
        `).join("")}
      `;
    } else {
      sourcesEl.innerHTML = "";
    }
  } catch (err) {
    console.error("RAG Query failed:", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Query";
  }
}

function setupDragAndDrop() {
  const dropArea = document.getElementById("drop-area");
  if (!dropArea) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
      e.preventDefault();
      dropArea.classList.add("border-primary", "bg-[#111726]");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
      e.preventDefault();
      dropArea.classList.remove("border-primary", "bg-[#111726]");
    });
  });

  dropArea.addEventListener("drop", e => {
    const dt = e.dataTransfer;
    const files = dt.files;
    uploadFiles(files);
  });
}

function handleFileUpload(e) {
  const files = e.target.files;
  uploadFiles(files);
}

async function uploadFiles(files) {
  for (let i = 0; i < files.length; i++) {
    const formData = new FormData();
    formData.append("file", files[i]);
    try {
      await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
    } catch (err) {
      console.error("Upload error:", err);
    }
  }

  fetchStats();
  fetchFiles();
  switchTab("feed");
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
