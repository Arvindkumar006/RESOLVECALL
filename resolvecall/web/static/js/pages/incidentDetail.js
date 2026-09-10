/**
 * FLAGSHIP INCIDENT DETAIL PAGE
 * 3-Column Enterprise Operations Console:
 * Incident Specification | Telephony Terminal + Dialpad + Live Transcript | Recovery Verification & Policy Math
 */

import { renderLifecycleStepper } from "../components/lifecycleStepper.js";
import { renderPhoneConsole, bindPhoneConsoleEvents } from "../components/phoneConsole.js";
import { renderTranscript, scrollTranscriptToBottom } from "../components/transcript.js";
import { renderRecoveryPolicy } from "../components/recoveryPolicy.js";
import { renderAuditFeed } from "../components/auditFeed.js";
import { maskPhoneNumber } from "../store.js";
import { api } from "../api.js";

export function renderIncidentDetailPage(incident, auditEvents = []) {
  if (!incident) {
    return `
      <div class="empty-state-box" style="padding:4rem 2rem;">
        <div class="empty-state-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </div>
        <h2 class="empty-state-title">Incident Not Found</h2>
        <p class="empty-state-desc">The requested operational incident does not exist in the active runtime ledger.</p>
        <a href="/incidents" data-route="/incidents" class="btn btn-secondary btn-sm" style="margin-top:1rem;">Return to Incidents</a>
      </div>
    `;
  }

  const isRunning = ["PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(incident.status);
  const status = incident.status || "OPEN";
  const maskedPhone = maskPhoneNumber(incident.phone_number);
  const callRunId = incident.calle_run_id || incident.calle_call_id || "Unassigned";

  // Authorization details
  const authInfo = incident.authorization_info || {};
  const authKeys = Object.keys(authInfo);

  return `
    <div style="display:flex; flex-direction:column; gap:1.25rem;">
      <!-- Flagship Header -->
      <div class="page-header" style="margin-bottom:0.5rem;">
        <div class="page-title-group">
          <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.35rem;">
            <span class="cell-mono" style="font-size:1.1rem; font-weight:800; color:#fff;">${incident.incident_id}</span>
            <span class="badge badge-${status.toLowerCase()}">${status}</span>
            ${incident.shipment_id ? `<span class="cell-mono text-muted" style="font-size:0.75rem;">SHIPMENT: ${incident.shipment_id}</span>` : ''}
          </div>
          <h1>${escapeHtml(incident.failure_code)}</h1>
          <p>${escapeHtml(incident.failure_description)}</p>
        </div>

        <div style="display:flex; align-items:center; gap:0.75rem;">
          <div class="telephony-live-chip ${isRunning ? 'active' : ''}">
            <span class="status-dot ${isRunning ? 'pulsing' : ''}" style="background:${isRunning ? 'var(--color-cyan)' : 'var(--text-muted)'};"></span>
            <span class="cell-mono" style="font-size:0.75rem;">${callRunId}</span>
          </div>

          <button class="btn btn-primary" id="btn-trigger-call" ${isRunning ? 'disabled' : ''}>
            ${isRunning ? `
              <span class="status-dot pulsing" style="background:#fff;"></span>
              <span>Autonomous Call Active...</span>
            ` : `
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              <span>Trigger CALL-E Recovery</span>
            `}
          </button>
        </div>
      </div>

      <!-- Horizontal Lifecycle Stepper -->
      ${renderLifecycleStepper(incident.status)}

      <!-- Flagship 3-Column Main Area -->
      <div class="flagship-grid">
        <!-- COLUMN 1: INCIDENT SPECIFICATION -->
        <div class="col-incident">
          <div class="incident-spec-card">
            <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border-subtle); padding-bottom:0.75rem;">
              <span class="spec-label">OPERATIONAL PARAMETERS</span>
              <span class="badge badge-secondary" style="font-size:0.65rem;">Level 1 Priority</span>
            </div>

            <div class="spec-item">
              <span class="spec-label">Carrier / Vendor</span>
              <span class="spec-val" style="font-weight:700; color:#fff;">${escapeHtml(incident.vendor)}</span>
            </div>

            <div class="spec-item">
              <span class="spec-label">Operational Contact</span>
              <span class="spec-val">${escapeHtml(incident.contact_name || "Operations Dispatch")}</span>
            </div>

            <div class="spec-item">
              <span class="spec-label">Authorized Destination</span>
              <span class="spec-val cell-mono text-cyan">${maskedPhone}</span>
            </div>

            <div class="spec-item">
              <span class="spec-label">Recovery Deadline Cutoff</span>
              <span class="spec-val cell-mono" style="color:var(--color-amber); font-weight:700; font-size:1.1rem;">
                ${incident.recovery_deadline}
              </span>
            </div>

            <div class="spec-item">
              <span class="spec-label">Required Operational Action</span>
              <span class="spec-val" style="font-size:0.8rem; line-height:1.4;">${escapeHtml(incident.required_action)}</span>
            </div>

            ${incident.cargo_information ? `
              <div class="spec-item">
                <span class="spec-label">Cargo Specification</span>
                <span class="spec-val" style="font-size:0.8rem;">${escapeHtml(incident.cargo_information)}</span>
              </div>
            ` : ''}

            <!-- Authorization Constraints Block -->
            <div style="background:var(--bg-panel); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:0.75rem; margin-top:0.35rem;">
              <span class="spec-label" style="display:block; margin-bottom:0.35rem;">Authorization Credentials</span>
              ${authKeys.length > 0 ? authKeys.map(k => `
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:0.2rem;">
                  <span class="text-muted">${k}:</span>
                  <span class="cell-mono text-cyan">${escapeHtml(String(authInfo[k]))}</span>
                </div>
              `).join("") : `<span class="text-muted" style="font-size:0.75rem;">None provided</span>`}
            </div>
          </div>
        </div>

        <!-- COLUMN 2: PHONE CONSOLE + DIALPAD + LIVE TRANSCRIPT -->
        <div class="col-center-phone">
          <!-- Enterprise Phone Console -->
          <div id="flagship-phone-mount">
            ${renderPhoneConsole(incident, { showDialpad: false, isInteractive: true })}
          </div>

          <!-- Live Call Transcript -->
          <div id="flagship-transcript-mount">
            ${renderTranscript(incident.transcript, incident.status)}
          </div>
        </div>

        <!-- COLUMN 3: RECOVERY VERIFICATION & POLICY MATH -->
        <div class="col-verification">
          ${renderRecoveryPolicy(incident)}
        </div>
      </div>

      <!-- Real-Time Audit Trail for this Incident -->
      <div class="table-panel" style="margin-top:1rem;">
        <div class="table-header-bar">
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span class="table-header-title">Operational Audit Trail (${incident.incident_id})</span>
          </div>
          <span class="cell-mono text-muted" style="font-size:0.7rem;">Append-Only Cryptographic Log</span>
        </div>
        <div style="padding:1.25rem;">
          ${renderAuditFeed(auditEvents)}
        </div>
      </div>
    </div>
  `;
}

export function bindIncidentDetailEvents(container, incident, onRecoveryTriggered) {
  const phoneMount = container.querySelector("#flagship-phone-mount");
  if (phoneMount) {
    bindPhoneConsoleEvents(phoneMount, {
      onEndCall: () => {
        alert("Autonomous Call Policy: In-call telephony lifecycle is managed deterministically by the autonomous recovery orchestrator.");
      }
    });
  }

  const triggerBtn = container.querySelector("#btn-trigger-call");
  if (triggerBtn) {
    triggerBtn.addEventListener("click", async () => {
      try {
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = `
          <span class="status-dot pulsing" style="background:#fff;"></span>
          <span>Initiating CALL-E Pipeline...</span>
        `;
        const res = await api.triggerRecovery(incident.incident_id);
        if (onRecoveryTriggered) onRecoveryTriggered(res);
      } catch (err) {
        alert(`Recovery Trigger Failed: ${err.message}`);
        triggerBtn.disabled = false;
        triggerBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <span>Trigger CALL-E Recovery</span>
        `;
      }
    });
  }

  scrollTranscriptToBottom(container);
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
