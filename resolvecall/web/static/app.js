// ResolveCall Real-Time Mission Control Dashboard

let activeIncidentId = null;
let eventSource = null;
let allIncidents = [];

// Preset incident payloads
const PRESET_PHARMA = {
  incident_id: "INC-COLD-88219",
  shipment_id: "SHP-MED-9941",
  failure_code: "UNDELIVERABLE_GATE_CODE_MISSING",
  failure_description: "Carrier driver at Facility Gate 4 unable to enter due to missing keypad security gate code. Shipment held outside.",
  cargo_information: "$60,000 temperature-sensitive biologic medication (Cold-chain 2°C–8°C; spoilage risk if delayed)",
  facility: "Mercy Health Logistics Hub - Dock B",
  vendor: "Apex Express Freight",
  contact_name: "Dispatch Operations",
  phone_number: "+18005550199",
  recovery_deadline: "11:30",
  authorization_info: {
    gate_access_code: "#4920*",
    po_number: "PO-MED-98842",
    receiving_lead_phone: "+15550192834"
  },
  required_action: "Provide gate code #4920* to dispatch/driver and secure emergency redelivery before 11:30 AM cutoff today."
};

const PRESET_DOCK = {
  incident_id: "INC-DOCK-33012",
  shipment_id: "SHP-AERO-4412",
  failure_code: "DOCK_REFUSED_MISSING_MANIFEST",
  failure_description: "Receiving refused trailer because electronic customs manifest reference is missing from bill of lading.",
  cargo_information: "AOG Aircraft Replacement Actuator ($120,000 urgent turnaround)",
  facility: "Skyline Air Cargo Bay 12",
  vendor: "Global Logistics Direct",
  contact_name: "Trailer Line Dispatch",
  phone_number: "+18005550199",
  recovery_deadline: "14:00",
  authorization_info: {
    manifest_pin: "PIN-7721-CUST",
    customs_entry_num: "C-8812903"
  },
  required_action: "Provide manifest PIN-7721-CUST to dispatch to clear dock refusal for delivery before 14:00 today."
};

document.addEventListener("DOMContentLoaded", () => {
  initElements();
  loadIncidents();
});

function initElements() {
  const modal = document.getElementById("modal-ingest");
  const btnOpenModal = document.getElementById("btn-open-ingest");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnCancelModal = document.getElementById("btn-cancel-modal");
  const btnSubmit = document.getElementById("btn-submit-incident");
  const btnTrigger = document.getElementById("btn-trigger-recovery");
  const jsonInput = document.getElementById("incident-json-input");

  // Presets
  document.getElementById("btn-preset-pharma").addEventListener("click", () => {
    jsonInput.value = JSON.stringify(PRESET_PHARMA, null, 2);
  });
  document.getElementById("btn-preset-dock").addEventListener("click", () => {
    jsonInput.value = JSON.stringify(PRESET_DOCK, null, 2);
  });

  // Modal open / close
  btnOpenModal.addEventListener("click", () => {
    if (!jsonInput.value) {
      jsonInput.value = JSON.stringify(PRESET_PHARMA, null, 2);
    }
    modal.style.display = "flex";
  });
  btnCloseModal.addEventListener("click", () => modal.style.display = "none");
  btnCancelModal.addEventListener("click", () => modal.style.display = "none");

  // Ingest Submit
  btnSubmit.addEventListener("click", async () => {
    try {
      const payload = JSON.parse(jsonInput.value);
      const res = await fetch("/api/incidents/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ingest failed");

      modal.style.display = "none";
      await loadIncidents();
      selectIncident(data.incident.incident_id);
    } catch (err) {
      alert("Error ingesting incident: " + err.message);
    }
  });

  // Trigger Recovery
  btnTrigger.addEventListener("click", async () => {
    if (!activeIncidentId) return;
    try {
      btnTrigger.disabled = true;
      const res = await fetch(`/api/incidents/${activeIncidentId}/recover`, {
        method: "POST"
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to trigger");
    } catch (err) {
      alert("Trigger failed: " + err.message);
      btnTrigger.disabled = false;
    }
  });
}

async function loadIncidents() {
  try {
    const res = await fetch("/api/incidents");
    allIncidents = await res.json();
    renderIncidentList(allIncidents);
    
    // Auto-select first if none selected
    if (!activeIncidentId && allIncidents.length > 0) {
      selectIncident(allIncidents[0].incident_id);
    }
  } catch (err) {
    console.error("Failed to load incidents", err);
  }
}

function renderIncidentList(incidents) {
  const container = document.getElementById("incident-list");
  const countBadge = document.getElementById("incident-count-badge");
  countBadge.textContent = `${incidents.length} Ingested`;

  if (incidents.length === 0) {
    container.innerHTML = `<div class="empty-state">No incidents ingested yet.<br>Click "+ Ingest Real Incident" above.</div>`;
    return;
  }

  container.innerHTML = incidents.map(inc => `
    <div class="incident-card ${inc.incident_id === activeIncidentId ? 'active' : ''}" onclick="selectIncident('${inc.incident_id}')">
      <div class="inc-card-top">
        <span class="inc-id">${inc.incident_id}</span>
        <span class="incident-badge-status ${inc.status}">${inc.status}</span>
      </div>
      <div class="inc-vendor">${inc.vendor}</div>
      <div class="inc-failure">${inc.failure_code}</div>
      <div class="inc-footer">
        <span>Deadline: ${inc.recovery_deadline}</span>
        <span>${inc.phone_number}</span>
      </div>
    </div>
  `).join("");
}

async function selectIncident(incidentId) {
  activeIncidentId = incidentId;
  renderIncidentList(allIncidents);

  // Fetch full details
  try {
    const res = await fetch(`/api/incidents/${incidentId}`);
    const incident = await res.json();
    updateDashboardView(incident);
    connectSSE(incidentId);
    loadAuditTrail(incidentId);
  } catch (err) {
    console.error("Failed to fetch incident", err);
  }
}

function updateDashboardView(inc) {
  if (!inc) return;

  // Header & Tags
  document.getElementById("active-status-badge").className = `incident-badge-status ${inc.status}`;
  document.getElementById("active-status-badge").textContent = inc.status;
  document.getElementById("active-id-tag").textContent = inc.incident_id;
  document.getElementById("active-shipment-tag").textContent = inc.shipment_id || "NO-SHIPMENT-ID";
  document.getElementById("active-failure-title").textContent = `${inc.failure_code}: ${inc.failure_description}`;
  document.getElementById("active-cargo-desc").textContent = inc.cargo_information ? `Cargo Priority: ${inc.cargo_information}` : "";

  // Enable/disable trigger button
  const btnTrigger = document.getElementById("btn-trigger-recovery");
  const isRunning = ["PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(inc.status);
  btnTrigger.disabled = isRunning;
  if (isRunning) {
    btnTrigger.innerHTML = `
      <span class="status-dot" style="background:#06b6d4;box-shadow:0 0 8px #06b6d4;"></span>
      <span>Autonomous Recovery Running...</span>
    `;
  } else {
    btnTrigger.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      <span>Trigger CALL-E Recovery</span>
    `;
  }

  // Stepper
  updateStepper(inc.status);

  // Metrics
  document.getElementById("metric-vendor").textContent = inc.vendor;
  document.getElementById("metric-phone").textContent = inc.phone_number;
  document.getElementById("metric-deadline").textContent = inc.recovery_deadline;
  document.getElementById("metric-call-id").textContent = inc.calle_run_id || inc.calle_call_id || "Unassigned";
  
  if (inc.policy_evaluation) {
    const dec = inc.policy_evaluation.decision;
    const decEl = document.getElementById("metric-policy-status");
    decEl.textContent = dec;
    decEl.style.color = dec === "VALID" ? "var(--accent-emerald)" : (dec === "INVALID" ? "var(--accent-rose)" : "var(--accent-amber)");
    document.getElementById("metric-policy-reason").textContent = inc.policy_evaluation.reason || "";
  } else {
    document.getElementById("metric-policy-status").textContent = "Pending Call";
    document.getElementById("metric-policy-status").style.color = "var(--text-muted)";
    document.getElementById("metric-policy-reason").textContent = "Awaiting call result";
  }

  // Audio waveform & pill
  const wave = document.getElementById("call-wave-indicator");
  const audioPill = document.getElementById("live-audio-pill");
  if (["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status)) {
    wave.classList.add("active");
    audioPill.className = "live-pill active";
    audioPill.textContent = inc.status === "CALLING" ? "RINGING" : "LIVE CALL";
  } else {
    wave.classList.remove("active");
    audioPill.className = "live-pill";
    audioPill.textContent = inc.status;
  }

  // Transcript
  renderTranscript(inc.transcript);

  // Evidence
  if (inc.extracted_evidence) {
    const ev = inc.extracted_evidence;
    const winStr = ev.agreed_window_start && ev.agreed_window_end 
      ? `${ev.agreed_window_start} – ${ev.agreed_window_end}`
      : (ev.agreed_window_end || "None");
    document.getElementById("ev-window").textContent = winStr;
    document.getElementById("ev-dispatcher").textContent = ev.representative_name || "Unspecified";
    document.getElementById("ev-auth").textContent = ev.authorization_code || "None";
    document.getElementById("ev-summary").textContent = inc.recovery_summary || ev.notes || "--";

    document.getElementById("evidence-badge").textContent = ev.resolution_status || "VERIFIED";
    document.getElementById("evidence-badge").className = `badge ${ev.resolution_status === 'CONFIRMED' ? 'badge-recovered' : ''}`;

    const quotesEl = document.getElementById("ev-quotes");
    if (ev.raw_evidence_quotes && ev.raw_evidence_quotes.length > 0) {
      quotesEl.innerHTML = ev.raw_evidence_quotes.map(q => `<div>• "${q}"</div>`).join("");
    } else {
      quotesEl.innerHTML = `<span class="text-muted">No explicit quotes captured.</span>`;
    }
  } else {
    document.getElementById("ev-window").textContent = "--";
    document.getElementById("ev-dispatcher").textContent = "--";
    document.getElementById("ev-auth").textContent = "--";
    document.getElementById("ev-summary").textContent = "--";
    document.getElementById("evidence-badge").textContent = "Awaiting Call";
    document.getElementById("ev-quotes").innerHTML = `<span class="text-muted">Evidence quotes will be extracted live from transcript.</span>`;
  }
}

function updateStepper(status) {
  const stages = ["OPEN", "PLANNING", "CALLING", "NEGOTIATING", "VALIDATING", "RECOVERED"];
  const stageIndex = stages.indexOf(status);
  const nodes = document.querySelectorAll(".step-node");

  nodes.forEach((node, i) => {
    node.classList.remove("active", "done");
    if (status === "RECOVERED" || status === "DEADLINE_MISSED" || status === "ESCALATED") {
      if (i < 5) node.classList.add("done");
      if (i === 5) {
        node.classList.add("done");
        node.querySelector(".step-label").textContent = status;
      }
    } else if (i < stageIndex) {
      node.classList.add("done");
    } else if (i === stageIndex) {
      node.classList.add("active");
    }
  });
}

function renderTranscript(turns) {
  const container = document.getElementById("transcript-feed");
  if (!turns || turns.length === 0) {
    container.innerHTML = `<div class="empty-state">No active call session. Trigger recovery to start CALL-E dialer.</div>`;
    return;
  }

  container.innerHTML = turns.map(t => {
    const role = (t.role || "speaker").toLowerCase();
    const isAgent = role.includes("agent") || role.includes("assistant") || role.includes("caller");
    const roleLabel = isAgent ? "CALL-E Recovery Agent" : "Carrier Representative";
    return `
      <div class="chat-turn ${isAgent ? 'agent' : 'human'}">
        <span class="speaker-tag">${roleLabel}</span>
        <div class="turn-text">${t.text}</div>
      </div>
    `;
  }).join("");

  container.scrollTop = container.scrollHeight;
}

async function loadAuditTrail(incidentId) {
  try {
    const res = await fetch(`/api/audit?incident_id=${incidentId}`);
    const events = await res.json();
    renderAuditTrail(events);
  } catch (err) {
    console.error("Failed to load audit trail", err);
  }
}

function renderAuditTrail(events) {
  const feed = document.getElementById("audit-feed");
  if (!events || events.length === 0) {
    feed.innerHTML = `<div class="text-muted" style="font-size:0.75rem;padding:0.4rem;">No events logged yet.</div>`;
    return;
  }

  feed.innerHTML = events.slice().reverse().map(e => {
    const t = new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    return `
      <div class="audit-item">
        <span class="audit-time">[${t}]</span>
        <span class="audit-desc"><strong>${e.event_type}</strong>: ${e.description}</span>
      </div>
    `;
  }).join("");
}

function connectSSE(incidentId) {
  if (eventSource) {
    eventSource.close();
  }

  eventSource = new EventSource(`/api/incidents/${incidentId}/stream`);

  eventSource.addEventListener("init", e => {
    try {
      const inc = JSON.parse(e.data);
      updateDashboardView(inc);
    } catch (err) {}
  });

  eventSource.addEventListener("update", e => {
    try {
      const payload = JSON.parse(e.data);
      if (payload.incident && payload.incident.incident_id === activeIncidentId) {
        updateDashboardView(payload.incident);
      }
      if (payload.event && payload.event.incident_id === activeIncidentId) {
        loadAuditTrail(activeIncidentId);
      }
      // Refresh list status
      loadIncidents();
    } catch (err) {}
  });

  eventSource.onerror = () => {
    document.getElementById("connection-status").className = "status-chip";
    document.querySelector("#connection-status .status-text").textContent = "Reconnecting...";
  };

  eventSource.onopen = () => {
    document.getElementById("connection-status").className = "status-chip";
    document.querySelector("#connection-status .status-text").textContent = "CALL-E Connected";
  };
}
