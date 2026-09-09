// JARVIS Sentinel - Real-Time Dashboard Client Controller

let activeIncidentId = null;
let lastReportMarkdown = null;

// Initialize and start polling
document.addEventListener("DOMContentLoaded", () => {
  fetchState();
  fetchTraces();
  fetchAudit();
  setInterval(refreshAll, 1500);

  document.getElementById("btn-scenario-a").addEventListener("click", triggerScenarioA);
  document.getElementById("btn-scenario-b").addEventListener("click", triggerScenarioB);
  document.getElementById("btn-reset").addEventListener("click", resetSimulation);
  document.getElementById("btn-modal-approve").addEventListener("click", approveIncident);
  document.getElementById("btn-modal-deny").addEventListener("click", denyIncident);
  document.getElementById("btn-close-report").addEventListener("click", closeReportModal);
});

async function refreshAll() {
  await Promise.all([fetchState(), fetchTraces(), fetchAudit()]);
}

// Fetch real-time backend state
async function fetchState() {
  try {
    const res = await fetch("/api/state");
    const data = await res.json();
    renderHosts(data.hosts);
    renderActiveIncidents(data.active_incidents, data.hitl_states);
  } catch (err) {
    console.error("Failed to fetch state:", err);
  }
}

// Fetch real execution traces
async function fetchTraces() {
  try {
    const res = await fetch("/api/traces");
    const data = await res.json();
    renderTraces(data.traces);
  } catch (err) {
    console.error("Failed to fetch traces:", err);
  }
}

// Fetch security audit trail
async function fetchAudit() {
  try {
    const res = await fetch("/api/audit");
    const data = await res.json();
    renderAudit(data.audit_log);
  } catch (err) {
    console.error("Failed to fetch audit log:", err);
  }
}

// Render Endpoint Fleet
function renderHosts(hosts) {
  const container = document.getElementById("endpoint-fleet");
  if (!container || !hosts) return;

  container.innerHTML = hosts.map(h => {
    const isIsolated = h.status === "ISOLATED";
    return `
      <div class="endpoint-item ${isIsolated ? 'isolated' : ''}">
        <div class="endpoint-header">
          <span class="endpoint-name">${h.host_id}</span>
          <span class="badge-status ${isIsolated ? 'isolated' : 'connected'}">
            ${h.status}
          </span>
        </div>
        <div class="endpoint-meta">
          <span>IP: ${h.ip} | ${h.os_type}</span>
          <span>User: ${h.owner}</span>
          <span>Active Processes: ${h.process_count}</span>
          ${h.canary_tripped ? '<span style="color: var(--red); font-weight: 700;">⚠ CANARY TRAP BREACHED</span>' : ''}
          ${isIsolated ? '<span style="color: var(--red); font-weight: 700;">🚫 NETWORK QUARANTINE ACTIVE</span>' : ''}
        </div>
      </div>
    `;
  }).join("");
}

// Render Active Incidents and check for HITL gate
function renderActiveIncidents(incidents, hitlStates) {
  const modal = document.getElementById("hitl-modal");
  
  for (const [incId, brief] of Object.entries(incidents || {})) {
    const state = hitlStates[incId] || brief.status;

    // Check if high/critical incident is awaiting analyst approval
    if (brief.requires_hitl && state === "AWAITING_APPROVAL") {
      activeIncidentId = incId;
      document.getElementById("modal-inc-id").innerText = `INCIDENT #${incId.replace('INC-', '')} — CRITICAL`;
      document.getElementById("modal-host").innerText = brief.affected_host;
      document.getElementById("modal-confidence").innerText = `${Math.round(brief.confidence * 100)}%`;
      document.getElementById("modal-evidence-count").innerText = `${brief.evidence_count} correlated events`;
      document.getElementById("modal-action").innerText = brief.recommended_action;
      document.getElementById("modal-impact").innerText = brief.potential_impact;
      document.getElementById("modal-behavior").innerText = brief.suspected_behavior;
      
      modal.classList.add("active");
      return;
    }
  }

  // If no incident is awaiting approval, close modal if it was open
  if (modal && (!activeIncidentId || hitlStates[activeIncidentId] !== "AWAITING_APPROVAL")) {
    modal.classList.remove("active");
  }
}

// Render real execution traces
function renderTraces(traces) {
  const container = document.getElementById("trace-terminal");
  if (!container || !traces) return;

  const atBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;

  container.innerHTML = traces.slice(-50).map(t => {
    const timeStr = t.timestamp.split("T")[1]?.slice(0, 8) || "";
    return `
      <div class="trace-line">
        <span class="trace-time">[${timeStr}]</span>
        <span class="trace-tag ${t.action_type}">${t.action_type}</span>
        <strong style="color: var(--cyan); font-size: 0.72rem;">[${t.agent_name}]</strong>
        <span class="trace-msg">${escapeHtml(t.message)}</span>
      </div>
    `;
  }).join("");

  if (atBottom) {
    container.scrollTop = container.scrollHeight;
  }
}

// Render Security Audit Log
function renderAudit(auditLog) {
  const tbody = document.getElementById("audit-tbody");
  if (!tbody || !auditLog) return;

  tbody.innerHTML = auditLog.slice(-20).reverse().map(a => {
    const timeStr = a.timestamp.split("T")[1]?.slice(0, 8) || "";
    return `
      <tr>
        <td>${timeStr}</td>
        <td style="font-weight: 700; color: ${a.action.includes('DENY') ? 'var(--amber)' : a.action.includes('ISOLATE') ? 'var(--red)' : 'var(--green)'};">${a.action}</td>
        <td>${a.target}</td>
        <td>${a.actor}</td>
        <td>${escapeHtml(a.details)}</td>
      </tr>
    `;
  }).join("");
}

// Triggers
async function triggerScenarioA() {
  const btn = document.getElementById("btn-scenario-a");
  btn.disabled = true;
  btn.innerText = "⏳ Ingesting & Analyzing...";
  try {
    const res = await fetch("/api/trigger/scenario-a", { method: "POST" });
    const data = await res.json();
    console.log("Scenario A completed:", data);
    await refreshAll();
  } catch (err) {
    alert("Error triggering Scenario A: " + err);
  } finally {
    btn.disabled = false;
    btn.innerText = "⚡ Ingest Scenario A (Routine Dev Alert)";
  }
}

async function triggerScenarioB() {
  const btn = document.getElementById("btn-scenario-b");
  btn.disabled = true;
  btn.innerText = "🚨 Detonating Simulation...";
  try {
    const res = await fetch("/api/trigger/scenario-b", { method: "POST" });
    const data = await res.json();
    console.log("Scenario B completed:", data);
    await refreshAll();
  } catch (err) {
    alert("Error triggering Scenario B: " + err);
  } finally {
    btn.disabled = false;
    btn.innerText = "🚨 Ingest Scenario B (Critical Ransomware Attack)";
  }
}

async function approveIncident() {
  if (!activeIncidentId) return;
  const btn = document.getElementById("btn-modal-approve");
  btn.disabled = true;
  btn.innerText = "Isolating...";
  
  try {
    const res = await fetch(`/api/incidents/${activeIncidentId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver: "Senior_Analyst_Alex" })
    });
    const data = await res.json();
    
    document.getElementById("hitl-modal").classList.remove("active");
    if (data.report_markdown) {
      showReportModal(data.report_markdown);
    }
    await refreshAll();
  } catch (err) {
    alert("Approval error: " + err);
  } finally {
    btn.disabled = false;
    btn.innerText = "🛡️ APPROVE ISOLATION";
  }
}

async function denyIncident() {
  if (!activeIncidentId) return;
  try {
    await fetch(`/api/incidents/${activeIncidentId}/deny`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver: "Senior_Analyst_Alex", reason: "Operator intentional override" })
    });
    document.getElementById("hitl-modal").classList.remove("active");
    await refreshAll();
  } catch (err) {
    alert("Denial error: " + err);
  }
}

async function resetSimulation() {
  try {
    await fetch("/api/reset", { method: "POST" });
    closeReportModal();
    document.getElementById("hitl-modal").classList.remove("active");
    await refreshAll();
  } catch (err) {
    console.error("Reset failed:", err);
  }
}

function showReportModal(markdown) {
  document.getElementById("report-content").innerText = markdown;
  document.getElementById("report-modal").classList.add("active");
}

function closeReportModal() {
  document.getElementById("report-modal").classList.remove("active");
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
