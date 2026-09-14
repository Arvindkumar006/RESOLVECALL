// ==========================================================================
// RESOLVECALL — MISSION CONTROL CLIENT ENGINE
// Phone-First Autonomous Operations • Zero Fake Data • Pure API Consumer
// ==========================================================================

// Global Application State
let activeIncidentId = null;
let eventSource = null;
let allIncidents = [];
let allAuditEvents = [];
let healthState = { status: "unknown" };
let callTimerInterval = null;
let callStartTime = null;

// Default Ingest Schema Template (Preserved)
const DEFAULT_SCHEMA_TEMPLATE = {
  incident_id: "INC-" + Math.floor(10000 + Math.random() * 90000),
  failure_code: "OPERATIONAL_FAILURE",
  failure_description: "Driver unable to access loading dock; access gate closed",
  vendor: "Responsible Carrier / Service Provider",
  contact_name: "Operations Dispatch",
  phone_number: "+18005550100",
  recovery_deadline: "19:00",
  required_action: "Negotiate emergency dock access window today before cutoff",
  authorization_info: {
    authorization_code: "AUTH-1234"
  }
};

// Stage Explanations for Hero Interactive Breakdown (Product Education Only)
const HERO_STAGES_INFO = [
  {
    num: "STAGE 01 / 08",
    title: "INCIDENT DETECTED",
    desc: "An operational dependency (carrier, warehouse, facility, supplier) reports a failure. The incident contains strict cutoff deadlines and an authorized telephone contact.",
    rec: "Immutable incident payload, failure code, authorized contact number, cutoff deadline."
  },
  {
    num: "STAGE 02 / 08",
    title: "RECOVERY PLAN GENERATED",
    desc: "The autonomous planner synthesizes constraints, determines negotiation strategy, sets the deadline ceiling, and prepares required evidence fields before dialing.",
    rec: "Generated prompt, operational target, strict validation boundaries, required evidence tokens."
  },
  {
    num: "STAGE 03 / 08",
    title: "CALL-E TELEPHONY DIALS",
    desc: "The telephony engine initiates a physical outbound PSTN phone call through carrier infrastructure to the authorized destination number.",
    rec: "PSTN telephony task creation, CALL-E Run ID, dialing timestamp, carrier network status."
  },
  {
    num: "STAGE 04 / 08",
    title: "OPERATIONAL CONTACT ANSWERS",
    desc: "The physical human dispatcher, warehouse manager, or driver answers the phone call. Full-duplex audio stream establishes.",
    rec: "PSTN ring time, call connect timestamp, initial voice latency verification."
  },
  {
    num: "STAGE 05 / 08",
    title: "AUTONOMOUS NEGOTIATION",
    desc: "The voice agent articulates the emergency, provides authorization codes, challenges unviable time windows, and negotiates an expedited resolution slot.",
    rec: "Full chronological transcript with tagged speaker roles and verbatim utterances."
  },
  {
    num: "STAGE 06 / 08",
    title: "EVIDENCE EXTRACTION",
    desc: "The extraction engine isolates human recipient turns only. Extracts confirmed delivery window, representative name, and dispatch reference number.",
    rec: "Structured delivery window, dispatcher name, authorization code, verbatim speech quotes."
  },
  {
    num: "STAGE 07 / 08",
    title: "DETERMINISTIC POLICY VERIFIED",
    desc: "Mathematical policy evaluation computes whether the negotiated window satisfies the operational deadline cutoff with minute-level precision.",
    rec: "Deterministic verdict (VALID / INVALID / AMBIGUOUS), deadline evaluated, minute safety margin."
  },
  {
    num: "STAGE 08 / 08",
    title: "RECOVERY RECORDED",
    desc: "Incident state is locked to RECOVERED or RECOVERY_UNCONFIRMED based solely on verified policy outcome. Downstream systems notified.",
    rec: "Final state transition locked in append-only audit trail; mission completed."
  }
];

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener("DOMContentLoaded", async () => {
  initRouter();
  initHeroInteractivity();
  initDialpad();
  initModals();
  initRecoveryTriggerButton();
  initSettings();
  initAuth();

  // Load initial backend telemetry
  await checkHealth();
  await loadIncidents();
  await loadGlobalAudit();

  // Handle route
  handleCurrentRoute();

  // Start subtle periodic polling for background synchronization
  setInterval(async () => {
    await checkHealth();
    await loadIncidents();
  }, 8000);
});

// ==========================================================================
// CLIENT-SIDE ROUTER
// ==========================================================================

function initRouter() {
  // Intercept all internal navigation clicks
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a[data-route], a[href^='/']");
    if (!link) return;

    const href = link.getAttribute("data-route") || link.getAttribute("href");
    if (!href || href.startsWith("http") || href.startsWith("//") || href.startsWith("mailto:")) return;

    e.preventDefault();
    navigateTo(href);
  });

  // Listen for browser forward/back
  window.addEventListener("popstate", () => {
    handleCurrentRoute();
  });
}

function navigateTo(path) {
  window.history.pushState({}, "", path);
  handleCurrentRoute();
}

function handleCurrentRoute() {
  const fullPath = window.location.pathname || "/";

  // Match routes
  if (fullPath === "/" || fullPath === "") {
    showView("view-landing", "Product");
  } else if (fullPath === "/how-it-works") {
    showView("view-how-it-works", "How It Works");
  } else if (fullPath === "/architecture") {
    showView("view-architecture", "Architecture");
  } else if (fullPath === "/security") {
    showView("view-security", "Security");
  } else if (fullPath.startsWith("/incidents/")) {
    const incId = fullPath.replace("/incidents/", "").trim();
    showView("view-console-workspace", "Incident Workspace");
    showConsoleSubview("subview-incident-detail", `Incident ${incId}`);
    if (incId && incId !== activeIncidentId) {
      selectIncident(incId);
    }
  } else if (fullPath === "/incidents") {
    showView("view-console-workspace", "Incidents Queue");
    showConsoleSubview("subview-incidents-list", "Operational Incidents");
  } else if (fullPath.startsWith("/calls")) {
    showView("view-console-workspace", "Call Operations");
    showConsoleSubview("subview-calls", "Call Operations");
  } else if (fullPath === "/recoveries") {
    showView("view-console-workspace", "Recoveries");
    showConsoleSubview("subview-recoveries", "Operational Recoveries");
  } else if (fullPath === "/plans") {
    showView("view-console-workspace", "Recovery Plans");
    showConsoleSubview("subview-plans", "Recovery Plans");
  } else if (fullPath === "/evidence") {
    showView("view-console-workspace", "Evidence Ledger");
    showConsoleSubview("subview-evidence", "Evidence Ledger");
  } else if (fullPath === "/audit") {
    showView("view-console-workspace", "Audit Trail");
    showConsoleSubview("subview-audit", "Operational Audit Trail");
  } else if (fullPath === "/settings") {
    showView("view-console-workspace", "Settings");
    showConsoleSubview("subview-settings", "Preferences");
  } else {
    // Default to /console
    showView("view-console-workspace", "Command Center");
    showConsoleSubview("subview-console-overview", "Command Center");
  }

  // Update public navbar link active styles
  document.querySelectorAll(".public-nav-links .nav-link").forEach(l => {
    const r = l.getAttribute("data-route");
    l.classList.toggle("active", r === fullPath);
  });
}

function showView(viewId, title) {
  document.querySelectorAll(".view-page").forEach(vp => vp.classList.remove("active"));
  const target = document.getElementById(viewId);
  if (target) {
    target.classList.add("active");
  }
  window.scrollTo(0, 0);
}

function showConsoleSubview(subviewId, title) {
  document.querySelectorAll(".subview-panel").forEach(sp => sp.classList.remove("active"));
  const target = document.getElementById(subviewId);
  if (target) {
    target.classList.add("active");
  }

  const titleEl = document.getElementById("current-view-title");
  if (titleEl && title) {
    titleEl.textContent = title;
  }

  // Update sidebar active link
  document.querySelectorAll(".sidebar-link").forEach(sl => {
    const r = sl.getAttribute("data-route");
    const p = window.location.pathname;
    sl.classList.toggle("active", (p === r) || (p.startsWith("/incidents") && r === "/incidents") || (p.startsWith("/calls") && r === "/calls"));
  });

  // Re-render subview specific data
  if (subviewId === "subview-calls") renderCallsTable();
  if (subviewId === "subview-recoveries") renderRecoveriesTable("ALL");
  if (subviewId === "subview-plans") renderPlansGrid();
  if (subviewId === "subview-evidence") renderEvidenceTable();
  if (subviewId === "subview-audit") renderFullAuditFeed();
}

// ==========================================================================
// HERO INTERACTIVITY (8 Stages Breakdown)
// ==========================================================================

function initHeroInteractivity() {
  const stageBtns = document.querySelectorAll(".stage-btn");
  stageBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      stageBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const idx = parseInt(btn.getAttribute("data-stage-idx"), 10) || 0;
      const info = HERO_STAGES_INFO[idx];
      if (!info) return;

      document.getElementById("stage-detail-num").textContent = info.num;
      document.getElementById("stage-detail-title").textContent = info.title;
      document.getElementById("stage-detail-text").textContent = info.desc;
      document.getElementById("stage-detail-rec-val").textContent = info.rec;
    });
  });
}

// ==========================================================================
// INTERACTIVE TELEPHONY DIALPAD
// ==========================================================================

function initDialpad() {
  const keys = document.querySelectorAll(".dial-key");
  keys.forEach(key => {
    key.addEventListener("click", () => {
      const k = key.getAttribute("data-key");
      // Visual tactile feedback
      key.classList.add("active");
      setTimeout(() => key.classList.remove("active"), 150);

      // Flash status notice
      const notice = document.querySelector(".dialpad-guard-notice");
      if (notice) {
        notice.style.borderColor = "var(--accent-amber)";
        notice.style.color = "var(--accent-amber)";
        setTimeout(() => {
          notice.style.borderColor = "var(--surface-border)";
          notice.style.color = "#94a3b8";
        }, 1200);
      }
    });
  });
}

// ==========================================================================
// MODALS & INGESTION
// ==========================================================================

function initModals() {
  const modal = document.getElementById("modal-ingest");
  const btnOpen = document.getElementById("btn-open-ingest");
  const btnClose = document.getElementById("btn-close-modal");
  const btnCancel = document.getElementById("btn-cancel-modal");
  const btnSubmit = document.getElementById("btn-submit-incident");
  const jsonInput = document.getElementById("incident-json-input");
  const ingestKeyInput = document.getElementById("modal-ingest-api-key");

  const openModal = () => {
    if (!jsonInput.value.trim()) {
      jsonInput.value = JSON.stringify(DEFAULT_SCHEMA_TEMPLATE, null, 2);
    }
    updateAuthUI();
    modal.style.display = "flex";
  };

  const closeModal = () => {
    modal.style.display = "none";
  };

  if (btnOpen) btnOpen.addEventListener("click", openModal);
  if (btnClose) btnClose.addEventListener("click", closeModal);
  if (btnCancel) btnCancel.addEventListener("click", closeModal);

  // Ingest Form Submit
  if (btnSubmit) {
    btnSubmit.addEventListener("click", async () => {
      try {
        btnSubmit.disabled = true;
        btnSubmit.textContent = "Registering...";

        // If user entered a key directly in the modal, store in sessionStorage
        if (ingestKeyInput && ingestKeyInput.value.trim()) {
          setApiKey(ingestKeyInput.value.trim());
          ingestKeyInput.value = "";
        }

        const payload = JSON.parse(jsonInput.value);

        const res = await apiFetch("/api/incidents/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Ingest failed");
        }

        closeModal();
        await loadIncidents();
        navigateTo(`/incidents/${data.incident.incident_id}`);
      } catch (err) {
        alert("Error ingesting incident: " + err.message);
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Ingest & Register Incident";
      }
    });
  }

  // Quick incident selector dropdown
  const selector = document.getElementById("select-active-incident");
  if (selector) {
    selector.addEventListener("change", (e) => {
      const id = e.target.value;
      if (id) {
        navigateTo(`/incidents/${id}`);
      }
    });
  }

  // Refresh buttons
  const btnRefreshInc = document.getElementById("btn-refresh-incidents");
  if (btnRefreshInc) btnRefreshInc.addEventListener("click", () => loadIncidents());

  const btnRefreshAud = document.getElementById("btn-refresh-audit");
  if (btnRefreshAud) btnRefreshAud.addEventListener("click", () => loadGlobalAudit());
}

// ==========================================================================
// RECOVERY TRIGGER (Rule 37: EXPLICIT USER CLICK ONLY!)
// ==========================================================================

function initRecoveryTriggerButton() {
  const btn = document.getElementById("btn-trigger-recovery");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    if (!activeIncidentId) {
      alert("No active incident selected.");
      return;
    }

    try {
      btn.disabled = true;
      btn.innerHTML = `
        <span class="pulse-dot"></span>
        <span>Calling via CALL-E...</span>
      `;

      const res = await apiFetch(`/api/incidents/${activeIncidentId}/recover`, {
        method: "POST"
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || data.detail || "Failed to trigger recovery");
      }
    } catch (err) {
      alert("Recovery Trigger Error: " + err.message);
      btn.disabled = false;
      btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        <span>Trigger CALL-E Recovery</span>
      `;
    }
  });
}

// ==========================================================================
// CLIENT AUTHENTICATION & SECURE SESSION STORAGE
// ==========================================================================

const SESSION_AUTH_KEY = "resolvecall_session_api_key";

function getApiKey() {
  try {
    return sessionStorage.getItem(SESSION_AUTH_KEY) || "";
  } catch (err) {
    return "";
  }
}

function setApiKey(key) {
  const trimmed = (key || "").trim();
  try {
    if (trimmed) {
      sessionStorage.setItem(SESSION_AUTH_KEY, trimmed);
    } else {
      sessionStorage.removeItem(SESSION_AUTH_KEY);
    }
  } catch (err) {}

  updateAuthUI();

  if (trimmed) {
    loadIncidents();
    loadGlobalAudit();
  }
}

function clearApiKey() {
  try {
    sessionStorage.removeItem(SESSION_AUTH_KEY);
  } catch (err) {}
  updateAuthUI();
}

function hasApiKey() {
  return Boolean(getApiKey());
}

async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = { ...(opts.headers || {}) };

  const key = getApiKey();
  if (key) {
    opts.headers["X-API-Key"] = key;
  }

  const res = await fetch(url, opts);
  if (res.status === 401) {
    updateAuthUI(true);
  }
  return res;
}

function updateAuthUI(isAuthError = false) {
  const isConfigured = hasApiKey();

  // Topbar badge
  const topbarBadge = document.getElementById("btn-open-auth-modal");
  const topbarLabel = document.getElementById("topbar-auth-label");
  if (topbarBadge) {
    topbarBadge.classList.remove("configured", "unconfigured");
    if (isAuthError) {
      topbarBadge.classList.add("unconfigured");
      if (topbarLabel) topbarLabel.textContent = "Auth 401 (Set Key)";
    } else if (isConfigured) {
      topbarBadge.classList.add("configured");
      if (topbarLabel) topbarLabel.textContent = "API Key Active";
    } else {
      topbarBadge.classList.add("unconfigured");
      if (topbarLabel) topbarLabel.textContent = "Set API Key";
    }
  }

  // Auth Dialog Status & Inputs
  const authInput = document.getElementById("auth-input-key");
  const authDialogStatus = document.getElementById("auth-modal-status");
  if (authInput) {
    authInput.value = "";
    authInput.placeholder = isConfigured ? "•••••••• (Session Key Set)" : "Enter API secret...";
  }
  if (authDialogStatus) {
    if (isAuthError) {
      authDialogStatus.innerHTML = `<span style="color:#ef4444;font-weight:600;">⚠ 401 Unauthorized: Supplied key rejected by backend.</span>`;
    } else if (isConfigured) {
      authDialogStatus.innerHTML = `<span style="color:#10b981;font-weight:600;">● Active in sessionStorage. Sent via X-API-Key.</span>`;
    } else {
      authDialogStatus.innerHTML = `<span style="color:var(--text-muted);">○ No key in session. Protected calls will return 401.</span>`;
    }
  }

  // Ingest Modal Input
  const ingestKeyInput = document.getElementById("modal-ingest-api-key");
  const ingestKeyStatus = document.getElementById("modal-ingest-key-status");
  if (ingestKeyInput) {
    ingestKeyInput.value = "";
    ingestKeyInput.placeholder = isConfigured ? "•••••••• (Session Key Set)" : "Enter RESOLVECALL_API_KEY for session...";
  }
  if (ingestKeyStatus) {
    if (isAuthError) {
      ingestKeyStatus.innerHTML = `<span style="color:#ef4444;">⚠ Authentication error: Please re-enter a valid API key.</span>`;
    } else if (isConfigured) {
      ingestKeyStatus.innerHTML = `<span style="color:#10b981;">● Session key configured. Protected endpoints will authenticate.</span>`;
    } else {
      ingestKeyStatus.innerHTML = `Stored only in sessionStorage for local development. Never exposed or logged.`;
    }
  }

  // Settings Subview Input
  const settingsKeyInput = document.getElementById("settings-api-key-input");
  const settingsKeyStatus = document.getElementById("settings-api-key-status");
  if (settingsKeyInput) {
    settingsKeyInput.value = "";
    settingsKeyInput.placeholder = isConfigured ? "•••••••• (Session Key Set)" : "Enter RESOLVECALL_API_KEY...";
  }
  if (settingsKeyStatus) {
    if (isAuthError) {
      settingsKeyStatus.innerHTML = `<span style="color:#ef4444;">⚠ Status: Authentication failed (401). Check server API key.</span>`;
    } else if (isConfigured) {
      settingsKeyStatus.innerHTML = `<span style="color:#10b981;">● Status: Key active in sessionStorage.</span>`;
    } else {
      settingsKeyStatus.innerHTML = `Status: No key configured in sessionStorage.`;
    }
  }
}

function initAuth() {
  const modalAuth = document.getElementById("modal-auth");
  const btnOpen = document.getElementById("btn-open-auth-modal");
  const btnClose = document.getElementById("btn-close-auth-modal");
  const btnSave = document.getElementById("btn-save-auth-modal");
  const btnClear = document.getElementById("btn-clear-auth-modal");
  const authInput = document.getElementById("auth-input-key");

  if (btnOpen && modalAuth) {
    btnOpen.addEventListener("click", () => {
      updateAuthUI();
      modalAuth.style.display = "flex";
      if (authInput) authInput.focus();
    });
  }

  if (btnClose && modalAuth) {
    btnClose.addEventListener("click", () => {
      modalAuth.style.display = "none";
    });
  }

  if (btnSave && authInput && modalAuth) {
    btnSave.addEventListener("click", () => {
      if (authInput.value.trim()) {
        setApiKey(authInput.value.trim());
      }
      modalAuth.style.display = "none";
    });

    authInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        if (authInput.value.trim()) {
          setApiKey(authInput.value.trim());
        }
        modalAuth.style.display = "none";
      }
    });
  }

  if (btnClear && modalAuth) {
    btnClear.addEventListener("click", () => {
      clearApiKey();
    });
  }

  // Ingest modal save button
  const btnSaveIngest = document.getElementById("btn-save-ingest-key");
  const ingestKeyInput = document.getElementById("modal-ingest-api-key");
  if (btnSaveIngest && ingestKeyInput) {
    btnSaveIngest.addEventListener("click", () => {
      if (ingestKeyInput.value.trim()) {
        setApiKey(ingestKeyInput.value.trim());
      }
    });

    ingestKeyInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (ingestKeyInput.value.trim()) {
          setApiKey(ingestKeyInput.value.trim());
        }
      }
    });
  }

  // Settings subview save/clear buttons
  const btnSettingsSave = document.getElementById("btn-settings-save-key");
  const btnSettingsClear = document.getElementById("btn-settings-clear-key");
  const settingsInput = document.getElementById("settings-api-key-input");
  if (btnSettingsSave && settingsInput) {
    btnSettingsSave.addEventListener("click", () => {
      if (settingsInput.value.trim()) {
        setApiKey(settingsInput.value.trim());
      }
    });

    settingsInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (settingsInput.value.trim()) {
          setApiKey(settingsInput.value.trim());
        }
      }
    });
  }
  if (btnSettingsClear) {
    btnSettingsClear.addEventListener("click", () => {
      clearApiKey();
    });
  }

  updateAuthUI();
}

// ==========================================================================
// BACKEND API CONSUMPTION
// ==========================================================================

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      healthState = await res.json();
      updateHealthUI(true);
    } else {
      updateHealthUI(false);
    }
  } catch (err) {
    updateHealthUI(false);
  }
}

function updateHealthUI(isHealthy) {
  const gText = document.getElementById("global-calle-text");
  const tText = document.getElementById("topbar-calle-text");

  const label = isHealthy ? "CALL-E Connected" : "CALL-E Offline";
  if (gText) gText.textContent = label;
  if (tText) tText.textContent = label;
}

async function loadIncidents() {
  try {
    const res = await apiFetch("/api/incidents");
    if (!res.ok) return;
    allIncidents = await res.json();

    // Update KPI strip & counters
    updateKPIs();
    renderQuickSelector();
    renderOverviewTable();
    renderIncidentsGrid();

    // If active incident is selected, refresh its view
    if (activeIncidentId) {
      const found = allIncidents.find(i => i.incident_id === activeIncidentId);
      if (found) {
        updateFlagshipWorkspace(found);
      }
    } else if (allIncidents.length > 0) {
      // If none active, default select first
      activeIncidentId = allIncidents[0].incident_id;
      updateFlagshipWorkspace(allIncidents[0]);
    }
  } catch (err) {
    console.error("Failed to load incidents:", err);
  }
}

async function loadGlobalAudit() {
  try {
    const res = await apiFetch("/api/audit");
    if (!res.ok) return;
    allAuditEvents = await res.json();
    renderFullAuditFeed();
  } catch (err) {
    console.error("Failed to load audit trail:", err);
  }
}

// ==========================================================================
// INCIDENT SELECTION & SSE STREAMING
// ==========================================================================

async function selectIncident(incidentId) {
  activeIncidentId = incidentId;

  // Clear workspace DOM elements to prevent cross-incident bleeding
  clearWorkspaceFields();

  // Find in local array or fetch directly
  let inc = allIncidents.find(i => i.incident_id === incidentId);
  if (!inc) {
    try {
      const res = await apiFetch(`/api/incidents/${incidentId}`);
      if (res.ok) inc = await res.json();
    } catch (err) {
      console.error(err);
    }
  }

  if (inc) {
    updateFlagshipWorkspace(inc);
    updateTelephonyScreen(inc);
  }

  // Connect SSE for this incident
  connectIncidentSSE(incidentId);

  // Load audit trail for this incident
  loadIncidentAudit(incidentId);
}

function clearWorkspaceFields() {
  document.getElementById("ev-window").textContent = "--";
  document.getElementById("ev-dispatcher").textContent = "Not confirmed";
  document.getElementById("ev-auth").textContent = "Not available";
  document.getElementById("ev-quotes").innerHTML = `<span class="text-muted">Evidence quotes will be extracted live from transcript.</span>`;
  document.getElementById("detail-policy-status").textContent = "Pending Call";
  document.getElementById("detail-policy-status").style.color = "var(--text-muted)";
  document.getElementById("detail-policy-reason").textContent = "Awaiting call result";
  document.getElementById("detail-transcript-feed").innerHTML = `<div class="empty-state">Loading incident session...</div>`;
}

function connectIncidentSSE(incidentId) {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }

  eventSource = new EventSource(`/api/incidents/${incidentId}/stream`);

  eventSource.addEventListener("init", (e) => {
    try {
      const inc = JSON.parse(e.data);
      updateFlagshipWorkspace(inc);
      updateTelephonyScreen(inc);
    } catch (err) {}
  });

  eventSource.addEventListener("update", (e) => {
    try {
      const payload = JSON.parse(e.data);
      if (payload.incident) {
        updateFlagshipWorkspace(payload.incident);
        updateTelephonyScreen(payload.incident);
      }
      if (payload.event) {
        appendAuditEvent(payload.event);
      }
    } catch (err) {}
  });

  eventSource.onerror = () => {
    // SSE reconnects automatically
  };
}

async function loadIncidentAudit(incidentId) {
  try {
    const res = await apiFetch(`/api/audit?incident_id=${incidentId}`);
    if (!res.ok) return;
    const events = await res.json();
    const feed = document.getElementById("audit-feed");
    if (!feed) return;

    if (!events || events.length === 0) {
      feed.innerHTML = `<div class="text-muted" style="padding:0.4rem;">No audit events recorded yet.</div>`;
      return;
    }

    feed.innerHTML = events.slice(-10).map(ev => `
      <div style="margin-bottom:0.45rem;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:0.3rem;">
        <span style="color:var(--accent-cyan);font-weight:700;">${ev.event_type}</span>
        <span style="color:var(--text-muted);font-size:0.65rem;margin-left:0.4rem;">${(ev.timestamp || "").substring(11, 19)}</span>
        <div style="color:var(--text-body);font-size:0.75rem;">${ev.description}</div>
      </div>
    `).join("");
    feed.scrollTop = feed.scrollHeight;
  } catch (err) {}
}

function appendAuditEvent(ev) {
  const feed = document.getElementById("audit-feed");
  if (!feed) return;
  const row = document.createElement("div");
  row.style.cssText = "margin-bottom:0.45rem;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:0.3rem;";
  row.innerHTML = `
    <span style="color:var(--accent-cyan);font-weight:700;">${ev.event_type}</span>
    <span style="color:var(--text-muted);font-size:0.65rem;margin-left:0.4rem;">${(ev.timestamp || "").substring(11, 19)}</span>
    <div style="color:var(--text-body);font-size:0.75rem;">${ev.description}</div>
  `;
  feed.appendChild(row);
  feed.scrollTop = feed.scrollHeight;
}

// ==========================================================================
// RENDERING WORKSPACES & DATA
// ==========================================================================

function updateKPIs() {
  const total = allIncidents.length;
  const activeCalls = allIncidents.filter(i => ["CALLING", "CONNECTED", "NEGOTIATING"].includes(i.status)).length;
  const recovered = allIncidents.filter(i => i.status === "RECOVERED").length;
  const unconfirmed = allIncidents.filter(i => i.status === "RECOVERY_UNCONFIRMED").length;

  document.getElementById("kpi-active-incidents").textContent = total;
  document.getElementById("kpi-active-calls").textContent = activeCalls;
  document.getElementById("kpi-recovered").textContent = recovered;
  document.getElementById("kpi-unconfirmed").textContent = unconfirmed;

  const countBadge = document.getElementById("side-inc-count");
  if (countBadge) countBadge.textContent = total;

  const feedLabel = document.getElementById("feed-count-label");
  if (feedLabel) feedLabel.textContent = `${total} Ingested`;
}

function renderQuickSelector() {
  const selector = document.getElementById("select-active-incident");
  if (!selector) return;

  const curVal = selector.value || activeIncidentId;
  selector.innerHTML = `<option value="">Select Incident...</option>` + 
    allIncidents.map(i => `<option value="${i.incident_id}">${i.incident_id} (${i.status})</option>`).join("");

  if (curVal) selector.value = curVal;
}

function renderOverviewTable() {
  const tbody = document.getElementById("overview-incident-tbody");
  if (!tbody) return;

  if (allIncidents.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state-cell">No incidents ingested yet. Click "Ingest Incident" above.</td></tr>`;
    return;
  }

  tbody.innerHTML = allIncidents.map(inc => `
    <tr>
      <td class="code-font"><a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" style="color:var(--accent-cyan);font-weight:600;">${inc.incident_id}</a></td>
      <td>${inc.failure_code}</td>
      <td>${inc.vendor || "--"}</td>
      <td class="code-font highlight-deadline">${inc.recovery_deadline || "--"}</td>
      <td><span class="incident-badge-status ${inc.status}">${inc.status}</span></td>
      <td>
        <a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" class="btn btn-secondary btn-sm">Inspect</a>
      </td>
    </tr>
  `).join("");
}

function renderIncidentsGrid() {
  const container = document.getElementById("all-incidents-cards");
  if (!container) return;

  if (allIncidents.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">No operational incidents. Ingest an incident to begin.</div>`;
    return;
  }

  container.innerHTML = allIncidents.map(inc => `
    <div class="feature-card" style="display:flex;flex-direction:column;gap:0.75rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span class="code-font" style="font-weight:700;color:var(--accent-cyan);">${inc.incident_id}</span>
        <span class="incident-badge-status ${inc.status}">${inc.status}</span>
      </div>
      <h4 style="font-family:var(--font-display);font-size:1.1rem;color:var(--text-white);">${inc.failure_code}</h4>
      <p style="font-size:0.85rem;color:var(--text-body);flex-grow:1;">${inc.failure_description}</p>
      <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);border-top:1px solid var(--surface-border);padding-top:0.6rem;">
        <span>Deadline: <strong class="code-font" style="color:var(--text-white);">${inc.recovery_deadline}</strong></span>
        <span>Vendor: ${inc.vendor}</span>
      </div>
      <a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" class="btn btn-secondary btn-sm" style="width:100%;margin-top:0.4rem;">Open Live Workspace →</a>
    </div>
  `).join("");
}

function updateFlagshipWorkspace(inc) {
  if (!inc) return;

  // Header tags
  const badge = document.getElementById("flagship-status-badge");
  badge.className = `incident-badge-status ${inc.status}`;
  badge.textContent = inc.status;

  document.getElementById("flagship-id-tag").textContent = inc.incident_id;
  document.getElementById("flagship-shipment-tag").textContent = inc.shipment_id || "NO-SHIPMENT-ID";
  document.getElementById("flagship-failure-title").textContent = `${inc.failure_code}: ${inc.failure_description}`;
  document.getElementById("flagship-cargo-desc").textContent = inc.cargo_information ? `Cargo: ${inc.cargo_information}` : `Vendor: ${inc.vendor}`;

  // Button disabled state
  const btn = document.getElementById("btn-trigger-recovery");
  const isRunning = ["PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(inc.status);
  btn.disabled = isRunning;
  if (isRunning) {
    btn.innerHTML = `<span class="pulse-dot"></span><span>Autonomous Call Active...</span>`;
  } else {
    btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      <span>Trigger CALL-E Recovery</span>
    `;
  }

  // Stepper
  updateLifecycleStepper(inc.status);

  // Column 1: Incident metadata
  document.getElementById("detail-vendor").textContent = inc.vendor || "--";
  document.getElementById("detail-phone").textContent = inc.phone_number || "--";
  document.getElementById("detail-contact").textContent = inc.contact_name || "--";
  document.getElementById("detail-deadline").textContent = inc.recovery_deadline || "--";
  document.getElementById("detail-action").textContent = inc.required_action || "--";

  let authStr = "--";
  if (inc.authorization_info) {
    authStr = Object.entries(inc.authorization_info).map(([k, v]) => `${k}: ${v}`).join(", ");
  }
  document.getElementById("detail-auth-info").textContent = authStr;

  // Column 2: Live Call
  document.getElementById("detail-run-id").textContent = inc.calle_run_id || inc.calle_call_id || "Awaiting Call";
  const pill = document.getElementById("detail-audio-pill");
  const wave = document.getElementById("detail-call-wave");
  if (isRunning) {
    pill.className = "live-pill active";
    pill.textContent = inc.status;
    wave.classList.add("active");
  } else {
    pill.className = "live-pill";
    pill.textContent = inc.status === "OPEN" ? "IDLE" : inc.status;
    wave.classList.remove("active");
  }

  // Render Transcript
  renderTranscriptTurns(inc.transcript || []);

  // Column 3: Evidence & Policy
  if (inc.extracted_evidence) {
    const ev = inc.extracted_evidence;
    const winStr = ev.agreed_window_start && ev.agreed_window_end
      ? `${ev.agreed_window_start} – ${ev.agreed_window_end}`
      : (ev.agreed_window_end || "None");

    document.getElementById("ev-window").textContent = winStr;
    document.getElementById("ev-dispatcher").textContent = ev.representative_name || "Not confirmed";
    document.getElementById("ev-auth").textContent = ev.authorization_code || "Not available";

    const quotesEl = document.getElementById("ev-quotes");
    if (ev.raw_evidence_quotes && ev.raw_evidence_quotes.length > 0) {
      quotesEl.innerHTML = ev.raw_evidence_quotes.map(q => `<div>• "${q}"</div>`).join("");
    } else {
      quotesEl.innerHTML = `<span class="text-muted">No explicit quotes captured.</span>`;
    }
  } else {
    document.getElementById("ev-window").textContent = "--";
    document.getElementById("ev-dispatcher").textContent = "Not confirmed";
    document.getElementById("ev-auth").textContent = "Not available";
    document.getElementById("ev-quotes").innerHTML = `<span class="text-muted">Evidence quotes will be extracted live from transcript.</span>`;
  }

  if (inc.policy_evaluation) {
    const dec = inc.policy_evaluation.decision;
    const decEl = document.getElementById("detail-policy-status");
    decEl.textContent = dec;
    decEl.style.color = dec === "VALID" ? "var(--accent-emerald)" : (dec === "INVALID" ? "var(--accent-rose)" : "var(--accent-amber)");
    document.getElementById("detail-policy-reason").textContent = inc.policy_evaluation.reason || "";
  } else {
    const decEl = document.getElementById("detail-policy-status");
    decEl.textContent = "Pending Call";
    decEl.style.color = "var(--text-muted)";
    document.getElementById("detail-policy-reason").textContent = "Awaiting call result";
  }
}

function updateTelephonyScreen(inc) {
  if (!inc) return;
  const runId = document.getElementById("telephony-run-id");
  const phone = document.getElementById("telephony-dest-phone");
  const state = document.getElementById("telephony-call-state");
  const wave = document.getElementById("telephony-live-wave");
  const statusPill = document.getElementById("telephony-status-pill");

  if (runId) runId.textContent = inc.calle_run_id || "--";
  if (phone) phone.textContent = inc.phone_number || "Authorized Contact";
  if (state) {
    state.textContent = inc.status;
    state.className = `screen-state ${["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status) ? 'highlight-cyan' : (inc.status === 'RECOVERED' ? 'highlight-green' : '')}`;
  }
  if (statusPill) {
    statusPill.textContent = ["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status) ? "PSTN CALL ACTIVE" : "VOICE CHANNEL READY";
  }
  if (wave) {
    if (["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status)) {
      wave.classList.add("active");
    } else {
      wave.classList.remove("active");
    }
  }
}

function updateLifecycleStepper(status) {
  const stages = ["OPEN", "PLANNING", "CALLING", "NEGOTIATING", "VALIDATING", "RECOVERED"];
  const stageIndex = stages.indexOf(status);
  const nodes = document.querySelectorAll(".stage-stepper .step-node");

  nodes.forEach((node, i) => {
    node.classList.remove("active", "done");
    if (status === "RECOVERED" || status === "RECOVERY_UNCONFIRMED" || status === "DEADLINE_MISSED" || status === "FAILED") {
      if (i < 5) node.classList.add("done");
      if (i === 5) {
        node.classList.add("done");
        node.querySelector(".step-label").textContent = status === "RECOVERED" ? "Recovered" : "Outcome";
      }
    } else if (i < stageIndex) {
      node.classList.add("done");
    } else if (i === stageIndex) {
      node.classList.add("active");
    }
  });
}

function renderTranscriptTurns(turns) {
  const container = document.getElementById("detail-transcript-feed");
  if (!container) return;

  if (!turns || turns.length === 0) {
    container.innerHTML = `<div class="empty-state">No active call session. Trigger recovery to start CALL-E dialer.</div>`;
    return;
  }

  container.innerHTML = turns.map(t => {
    const role = (t.role || "SYSTEM EVENT").toUpperCase();
    const isAgent = role === "RESOLVECALL AGENT";
    const isSystem = role === "SYSTEM EVENT";
    const roleLabel = isAgent ? "RESOLVECALL AGENT" : (isSystem ? "SYSTEM EVENT" : "OPERATIONS CONTACT");
    const cssClass = isAgent ? "agent" : (isSystem ? "system" : "human");
    return `
      <div class="chat-turn ${cssClass}">
        <span class="speaker-tag">${roleLabel}</span>
        <div class="turn-text">${t.text}</div>
      </div>
    `;
  }).join("");

  container.scrollTop = container.scrollHeight;
}

// ==========================================================================
// SUBVIEWS: CALLS, RECOVERIES, PLANS, EVIDENCE, AUDIT, SETTINGS
// ==========================================================================

function renderCallsTable() {
  const tbody = document.getElementById("calls-table-body");
  if (!tbody) return;

  if (allIncidents.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state-cell">No telephony calls recorded.</td></tr>`;
    return;
  }

  tbody.innerHTML = allIncidents.map(inc => `
    <tr>
      <td class="code-font"><a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" style="color:var(--accent-cyan);">${inc.incident_id}</a></td>
      <td class="code-font">${inc.calle_run_id || inc.calle_call_id || "Not assigned"}</td>
      <td>${inc.vendor || "--"}</td>
      <td class="code-font">${inc.phone_number || "--"}</td>
      <td><span class="incident-badge-status ${inc.status}">${inc.status}</span></td>
      <td>
        <a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" class="btn btn-secondary btn-sm">Inspect</a>
      </td>
    </tr>
  `).join("");
}

function renderRecoveriesTable(filter = "ALL") {
  const tbody = document.getElementById("recoveries-table-body");
  if (!tbody) return;

  let filtered = allIncidents;
  if (filter === "ACTIVE") {
    filtered = allIncidents.filter(i => ["PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(i.status));
  } else if (filter === "RECOVERED") {
    filtered = allIncidents.filter(i => i.status === "RECOVERED");
  } else if (filter === "UNCONFIRMED") {
    filtered = allIncidents.filter(i => i.status === "RECOVERY_UNCONFIRMED");
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state-cell">No recoveries matching filter "${filter}".</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(inc => {
    const ev = inc.extracted_evidence || {};
    const winStr = ev.agreed_window_start && ev.agreed_window_end ? `${ev.agreed_window_start} - ${ev.agreed_window_end}` : (ev.agreed_window_end || "None");
    const repStr = ev.representative_name || "Not confirmed";
    const polStr = inc.policy_evaluation ? inc.policy_evaluation.decision : "Pending";

    return `
      <tr>
        <td class="code-font"><a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" style="color:var(--accent-cyan);">${inc.incident_id}</a></td>
        <td><span class="incident-badge-status ${inc.status}">${inc.status}</span></td>
        <td class="code-font">${winStr}</td>
        <td>${repStr}</td>
        <td><strong style="color:${polStr === 'VALID' ? 'var(--accent-emerald)' : 'var(--text-muted)'}">${polStr}</strong></td>
        <td>
          <a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" class="btn btn-secondary btn-sm">Workspace</a>
        </td>
      </tr>
    `;
  }).join("");

  // Attach filter pill listeners
  document.querySelectorAll(".filter-pill").forEach(pill => {
    pill.onclick = () => {
      document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      renderRecoveriesTable(pill.getAttribute("data-filter"));
    };
  });
}

function renderPlansGrid() {
  const container = document.getElementById("plans-card-grid");
  if (!container) return;

  if (allIncidents.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">No active plans. Ingest an incident to generate a plan.</div>`;
    return;
  }

  container.innerHTML = allIncidents.map(inc => `
    <div class="plan-card">
      <div class="plan-header">
        <span class="plan-id">PLAN: ${inc.incident_id}</span>
        <span class="code-font" style="font-size:0.75rem;color:var(--accent-cyan);">${inc.recovery_deadline} CUTOFF</span>
      </div>
      <div class="plan-obj">
        <strong>Objective:</strong> ${inc.required_action}
      </div>
      <div style="display:flex;flex-direction:column;gap:0.25rem;font-size:0.8rem;color:var(--text-muted);border-top:1px solid var(--surface-border);padding-top:0.6rem;">
        <div><strong>Destination:</strong> <span class="code-font">${inc.phone_number}</span></div>
        <div><strong>Vendor:</strong> ${inc.vendor}</div>
        <div><strong>Failure:</strong> ${inc.failure_code}</div>
      </div>
      <a href="/incidents/${inc.incident_id}" data-route="/incidents/${inc.incident_id}" class="btn btn-secondary btn-sm" style="margin-top:auto;">Open Call Workspace</a>
    </div>
  `).join("");
}

function renderEvidenceTable() {
  const tbody = document.getElementById("evidence-table-body");
  if (!tbody) return;

  const rows = [];
  allIncidents.forEach(inc => {
    const ev = inc.extracted_evidence;
    if (!ev) {
      rows.push(`
        <tr>
          <td class="code-font">${inc.incident_id}</td>
          <td>Delivery Window</td>
          <td><span class="text-muted">Awaiting call</span></td>
          <td>Operational Dialogue</td>
          <td><span class="incident-badge-status OPEN">PENDING</span></td>
        </tr>
      `);
    } else {
      const win = ev.agreed_window_start && ev.agreed_window_end ? `${ev.agreed_window_start} - ${ev.agreed_window_end}` : (ev.agreed_window_end || "None");
      rows.push(`
        <tr>
          <td class="code-font">${inc.incident_id}</td>
          <td>Delivery Window</td>
          <td class="code-font highlight-win">${win}</td>
          <td>Operational Dialogue</td>
          <td><span class="incident-badge-status ${ev.resolution_status === 'CONFIRMED' ? 'RECOVERED' : 'OPEN'}">${ev.resolution_status || 'VERIFIED'}</span></td>
        </tr>
        <tr>
          <td class="code-font">${inc.incident_id}</td>
          <td>Representative Name</td>
          <td>${ev.representative_name || '<span class="text-muted">Not confirmed</span>'}</td>
          <td>Spoken Dialogue</td>
          <td><span class="incident-badge-status ${ev.representative_name ? 'RECOVERED' : 'OPEN'}">${ev.representative_name ? 'CONFIRMED' : 'MISSING'}</span></td>
        </tr>
        <tr>
          <td class="code-font">${inc.incident_id}</td>
          <td>Authorization Code</td>
          <td class="code-font">${ev.authorization_code || '<span class="text-muted">Not available</span>'}</td>
          <td>Dispatcher Commitment</td>
          <td><span class="incident-badge-status ${ev.authorization_code ? 'RECOVERED' : 'OPEN'}">${ev.authorization_code ? 'RECORDED' : 'MISSING'}</span></td>
        </tr>
      `);
    }
  });

  tbody.innerHTML = rows.length > 0 ? rows.join("") : `<tr><td colspan="5" class="empty-state-cell">No evidence captured yet.</td></tr>`;
}

function renderFullAuditFeed() {
  const container = document.getElementById("audit-full-feed");
  if (!container) return;

  if (allAuditEvents.length === 0) {
    container.innerHTML = `<div class="empty-state">No audit log events available.</div>`;
    return;
  }

  container.innerHTML = allAuditEvents.slice().reverse().map(ev => `
    <div class="feature-card" style="padding:1rem 1.2rem;margin-bottom:0.75rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
        <span class="code-font" style="font-weight:700;color:var(--accent-cyan);font-size:0.85rem;">${ev.event_type}</span>
        <span class="code-font" style="font-size:0.7rem;color:var(--text-muted);">${ev.timestamp}</span>
      </div>
      <div style="font-size:0.88rem;color:var(--text-white);margin-bottom:0.35rem;">${ev.description}</div>
      <div style="font-size:0.75rem;color:var(--text-muted);font-family:var(--font-mono);">Incident ID: ${ev.incident_id || '--'} • Event ID: ${ev.event_id}</div>
    </div>
  `).join("");
}

function initSettings() {
  const theme = document.getElementById("pref-theme");
  const reduced = document.getElementById("pref-reduced-motion");

  if (theme) {
    theme.value = localStorage.getItem("rc_theme") || "dark";
    theme.addEventListener("change", (e) => {
      localStorage.setItem("rc_theme", e.target.value);
    });
  }

  if (reduced) {
    reduced.checked = localStorage.getItem("rc_reduced_motion") === "true";
    reduced.addEventListener("change", (e) => {
      localStorage.setItem("rc_reduced_motion", e.target.checked);
    });
  }
}
