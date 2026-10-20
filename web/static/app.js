// SlothDesk Frontend Logic

let currentCategoryFilter = null;

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  fetchStatus();
  fetchStats();
  fetchFiles();

  // Auto-refresh stats and files every 5 seconds (sloth pace)
  setInterval(() => {
    fetchStats();
    fetchFiles();
  }, 5000);

  setupDragAndDrop();
});

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const pill = document.getElementById("ai-provider-text");
    if (data.ai && data.ai.online) {
      pill.textContent = `Local Ollama: ${data.ai.active_model}`;
      pill.className = "text-emerald-400 font-semibold";
    } else {
      pill.textContent = "Embedded Open NLP (100% Offline)";
      pill.className = "text-amber-400 font-semibold";
    }
  } catch (err) {
    console.error("Error fetching status:", err);
  }
}

async function fetchStats() {
  try {
    const res = await fetch("/api/stats");
    const stats = await res.json();

    document.getElementById("metric-naps").textContent = stats.naps_earned.toFixed(1);
    document.getElementById("metric-minutes").textContent = `${stats.minutes_saved} m`;
    document.getElementById("metric-files").textContent = stats.total_files_processed;
    document.getElementById("metric-calories").textContent = `${stats.calories_saved} kcal`;
    document.getElementById("metric-dollars").textContent = `$${stats.dollars_saved_vs_cloud.toFixed(2)}`;
    document.getElementById("sloth-rank").textContent = stats.sloth_level;

    // Render activity log
    const logList = document.getElementById("activity-log-list");
    if (stats.recent_activities && stats.recent_activities.length > 0) {
      logList.innerHTML = stats.recent_activities.map(act => `
        <div class="py-2.5 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-emerald-400 font-mono text-[11px]">[${act.timestamp.split("T")[1].substring(0, 8)}]</span>
            <span class="text-[#c7d5cd]">${escapeHtml(act.description)}</span>
          </div>
          <span class="text-emerald-400/80 font-mono font-medium">+${act.minutes_saved}m effort spared</span>
        </div>
      `).join("");
    } else {
      logList.innerHTML = `<div class="py-3 text-[#6f8779] text-center">No clutter has arrived yet. The sloth is resting.</div>`;
    }
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchFiles() {
  try {
    const url = currentCategoryFilter ? `/api/files?category=${encodeURIComponent(currentCategoryFilter)}` : "/api/files";
    const res = await fetch(url);
    const files = await res.json();
    renderFiles(files);
  } catch (err) {
    console.error("Error fetching files:", err);
  }
}

function renderFiles(files) {
  const container = document.getElementById("files-list");
  if (!files || files.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 border border-dashed border-[#203628] rounded-2xl bg-[#0f1913]/50">
        <span class="text-4xl block mb-2">😴</span>
        <h4 class="font-bold text-white text-base">Your Sloth Den is totally clear!</h4>
        <p class="text-xs text-[#7c9787] mt-1 max-w-sm mx-auto">
          No pending files. Click "Drop Demo Chaos" above or drop receipts, code, and notes into the Drop Zone to watch SlothDesk work.
        </p>
      </div>
    `;
    return;
  }

  container.innerHTML = files.map(file => {
    const catClass = `badge-${file.category}`;
    const actionBadge = file.action_required ? `
      <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1">
        ⚠️ Action: ${escapeHtml(file.action_note || "Review Needed")}
      </span>
    ` : "";

    const tagPills = (file.tags || []).map(t => `
      <span class="px-2 py-0.5 rounded bg-[#182a20] text-[#86a392] text-[10px] font-mono">#${escapeHtml(t)}</span>
    `).join("");

    return `
      <div class="sloth-card p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1.5 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${catClass}">
              ${escapeHtml(file.category)}
            </span>
            <span class="font-mono text-sm font-bold text-white">${escapeHtml(file.current_name)}</span>
            ${actionBadge}
          </div>

          <!-- Original name breadcrumb -->
          <div class="text-[11px] text-[#6d8476] flex items-center gap-1">
            <span>Original:</span>
            <span class="font-mono text-[#8aa393]">${escapeHtml(file.original_name)}</span>
            <span>•</span>
            <span>${(file.file_size_bytes / 1024).toFixed(1)} KB</span>
            <span>•</span>
            <span>${file.processed_at.split("T")[0]}</span>
          </div>

          <!-- Sloth TL;DR -->
          <div class="p-2.5 rounded-lg bg-[#0e1712] border border-[#1d2f23] text-xs text-emerald-200/90 leading-relaxed">
            <span class="font-bold text-emerald-400 mr-1.5">🦥 Sloth TL;DR:</span>
            ${escapeHtml(file.summary)}
          </div>

          <!-- Tags -->
          <div class="flex flex-wrap gap-1 pt-1">
            ${tagPills}
          </div>
        </div>

        <!-- 1-Click Action Button -->
        <div class="flex items-center gap-2 self-end md:self-center">
          <button onclick="undoSingleFile(${file.id})" title="Undo move and restore original name" class="px-3 py-1.5 rounded-lg bg-[#142018] hover:bg-[#1a2c21] border border-[#233a2b] text-[#8aa393] hover:text-white text-xs font-medium transition cursor-pointer">
            ↩️ Undo
          </button>
        </div>
      </div>
    `;
  }).join("");

  lucide.createIcons();
}

function filterCategory(cat) {
  currentCategoryFilter = cat;
  document.querySelectorAll(".category-btn").forEach(btn => {
    btn.classList.remove("active", "bg-[#1e3326]", "text-emerald-300", "border", "border-[#2b4937]");
    btn.classList.add("bg-[#132018]", "text-[#8ea899]");
  });

  event.currentTarget.classList.add("active", "bg-[#1e3326]", "text-emerald-300", "border", "border-[#2b4937]");
  event.currentTarget.classList.remove("bg-[#132018]", "text-[#8ea899]");

  fetchFiles();
}

function switchTab(tab) {
  const tabs = ["feed", "ask", "drop"];
  tabs.forEach(t => {
    document.getElementById(`tab-${t}`).classList.add("hidden");
    const btn = document.getElementById(`tab-btn-${t}`);
    btn.className = "px-3.5 py-1.5 rounded-lg text-[#7c9787] hover:text-white transition";
  });

  document.getElementById(`tab-${tab}`).classList.remove("hidden");
  const activeBtn = document.getElementById(`tab-btn-${tab}`);
  activeBtn.className = "px-3.5 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
}

async function triggerTidy() {
  const btn = document.getElementById("btn-tidy");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span>💤 Tidying...</span>`;
  try {
    const res = await fetch("/api/tidy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    fetchStats();
    fetchFiles();
  } catch (err) {
    console.error("Tidy failed:", err);
  } finally {
    btn.innerHTML = origText;
    lucide.createIcons();
  }
}

async function populateDemoClutter() {
  const btn = document.getElementById("btn-demo");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span>Dropping chaos...</span>`;
  try {
    await fetch("/api/populate-demo", { method: "POST" });
    // Immediately tidy them
    await triggerTidy();
  } catch (err) {
    console.error("Populate demo failed:", err);
  } finally {
    btn.innerHTML = origText;
    lucide.createIcons();
  }
}

async function triggerUndo() {
  try {
    const res = await fetch("/api/undo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    fetchStats();
    fetchFiles();
  } catch (err) {
    console.error("Undo failed:", err);
  }
}

async function undoSingleFile(fileId) {
  try {
    const res = await fetch("/api/undo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: fileId })
    });
    fetchStats();
    fetchFiles();
  } catch (err) {
    console.error("Single undo failed:", err);
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
  btn.innerText = "Thinking...";

  const box = document.getElementById("ask-response-box");
  const answerEl = document.getElementById("rag-answer");
  const verdictEl = document.getElementById("rag-verdict");
  const sourcesEl = document.getElementById("rag-sources");

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();

    box.classList.remove("hidden");
    answerEl.textContent = data.answer;
    verdictEl.textContent = data.sloth_verdict || "Open weights on local device";

    if (data.matched_files && data.matched_files.length > 0) {
      sourcesEl.innerHTML = `
        <div class="font-bold text-[#9dbcb0] mb-1">Local Files Referenced:</div>
        ${data.matched_files.map(f => `
          <div class="flex items-center justify-between py-0.5">
            <span class="font-mono text-emerald-300">• ${escapeHtml(f.name || f.current_name)}</span>
            <span class="text-[#647c6e]">Category: ${f.category}</span>
          </div>
        `).join("")}
      `;
    } else {
      sourcesEl.innerHTML = "";
    }
  } catch (err) {
    console.error("Ask query failed:", err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="search" class="w-4 h-4"></i><span>Ask Sloth</span>`;
    lucide.createIcons();
  }
}

function setupDragAndDrop() {
  const dropArea = document.getElementById("drop-area");
  if (!dropArea) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
      e.preventDefault();
      dropArea.classList.add("border-emerald-400", "bg-[#183124]");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
      e.preventDefault();
      dropArea.classList.remove("border-emerald-400", "bg-[#183124]");
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
  const statusEl = document.getElementById("upload-status");
  statusEl.textContent = `Uploading & digesting ${files.length} file(s)...`;

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

  statusEl.textContent = "Done! All files processed and filed away.";
  setTimeout(() => { statusEl.textContent = ""; }, 3000);

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
