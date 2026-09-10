/**
 * Telephony Operations Center: Calls List & Call Detail Page
 * Focuses purely on telephony sessions, PSTN gateway states, and call outcomes.
 */

import { renderPhoneConsole, bindPhoneConsoleEvents } from "../components/phoneConsole.js";
import { renderTranscript } from "../components/transcript.js";
import { maskPhoneNumber, formatDateTime } from "../store.js";

export function renderCallsPage(incidents = []) {
  // Extract calls from incidents that have a calle_call_id or status beyond OPEN
  const callRecords = incidents.filter(i => 
    Boolean(i.calle_run_id || i.calle_call_id || ["CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING", "RECOVERED", "DEADLINE_MISSED", "ESCALATED", "FAILED"].includes(i.status))
  );

  const activeCalls = callRecords.filter(c => ["CALLING", "CONNECTED", "NEGOTIATING"].includes(c.status));
  const completedCalls = callRecords.filter(c => c.status === "RECOVERED");
  const failedOrMissed = callRecords.filter(c => ["DEADLINE_MISSED", "FAILED"].includes(c.status));
  const escalatedCalls = callRecords.filter(c => c.status === "ESCALATED");

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Telephony Call Operations</h1>
        <p>Monitor outbound PSTN telephone sessions executed via CALL-E gateway</p>
      </div>
      <div class="telephony-live-chip ${activeCalls.length > 0 ? 'active' : ''}">
        <span class="status-dot ${activeCalls.length > 0 ? 'pulsing' : ''}" style="background:${activeCalls.length > 0 ? 'var(--color-cyan)' : 'var(--text-muted)'};"></span>
        <span>${activeCalls.length} Active Telecom Channel${activeCalls.length === 1 ? '' : 's'}</span>
      </div>
    </div>

    <!-- Call Stats -->
    <div class="metrics-row">
      <div class="metric-box">
        <span class="metric-box-label">Active Sessions</span>
        <span class="metric-box-val" style="color:var(--color-cyan);">${activeCalls.length}</span>
        <span class="metric-box-sub text-muted">Currently on PSTN lines</span>
      </div>
      <div class="metric-box">
        <span class="metric-box-label">Successful Recoveries</span>
        <span class="metric-box-val" style="color:var(--color-emerald);">${completedCalls.length}</span>
        <span class="metric-box-sub text-muted">Negotiation confirmed</span>
      </div>
      <div class="metric-box">
        <span class="metric-box-label">Cutoff Exceeded / Failed</span>
        <span class="metric-box-val" style="color:var(--color-rose);">${failedOrMissed.length}</span>
        <span class="metric-box-sub text-muted">Rejected or missed</span>
      </div>
      <div class="metric-box">
        <span class="metric-box-label">Supervisor Escalations</span>
        <span class="metric-box-val" style="color:var(--color-purple);">${escalatedCalls.length}</span>
        <span class="metric-box-sub text-muted">Human follow-up required</span>
      </div>
    </div>

    <!-- Calls Data Table -->
    <div class="table-panel">
      <div class="table-header-bar">
        <span class="table-header-title">CALL-E PSTN Session Ledger</span>
        <span class="cell-mono text-muted" style="font-size:0.75rem;">E.164 Carrier Gateway</span>
      </div>

      ${callRecords.length === 0 ? `
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <h3 class="empty-state-title">No telephony sessions recorded</h3>
          <p class="empty-state-desc">Outbound telephone calls will appear here when an operator initiates recovery for an incident.</p>
        </div>
      ` : `
        <table class="data-table">
          <thead>
            <tr>
              <th>Call ID / Run ID</th>
              <th>Incident</th>
              <th>Destination</th>
              <th>Carrier / Dispatch</th>
              <th>Call Status</th>
              <th>Started</th>
              <th>Outcome</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${callRecords.map(inc => {
              const runId = inc.calle_run_id || inc.calle_call_id || "Unassigned";
              const isCallActive = ["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status);
              return `
                <tr onclick="window.router.navigate('/calls/${encodeURIComponent(inc.incident_id)}')">
                  <td class="cell-mono">
                    <span class="telephony-row-icon">☎</span>
                    <span style="color:#fff; font-weight:600;">${runId}</span>
                  </td>
                  <td class="cell-mono text-cyan">${inc.incident_id}</td>
                  <td class="cell-mono text-muted">${maskPhoneNumber(inc.phone_number)}</td>
                  <td>${inc.vendor}</td>
                  <td>
                    <span class="badge badge-${(inc.status || '').toLowerCase()}">
                      ${isCallActive ? '● ACTIVE' : inc.status}
                    </span>
                  </td>
                  <td style="font-size:0.75rem; color:var(--text-muted);">${formatDateTime(inc.updated_at || inc.created_at)}</td>
                  <td style="font-size:0.8rem;">
                    ${inc.recovery_summary ? escapeHtml(inc.recovery_summary) : (isCallActive ? 'Negotiating delivery window' : 'Completed')}
                  </td>
                  <td>
                    <a href="/calls/${encodeURIComponent(inc.incident_id)}" data-route="/calls/${encodeURIComponent(inc.incident_id)}" class="btn btn-secondary btn-sm" style="padding:0.25rem 0.6rem;">Inspect Session</a>
                  </td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      `}
    </div>
  `;
}

export function renderCallDetailPage(incident) {
  if (!incident) {
    return `
      <div class="empty-state-box">
        <h3 class="empty-state-title">Call Record Not Found</h3>
        <a href="/calls" data-route="/calls" class="btn btn-secondary btn-sm" style="margin-top:1rem;">Back to Calls</a>
      </div>
    `;
  }

  return `
    <div style="max-width:960px; margin:0 auto; display:flex; flex-direction:column; gap:1.5rem;">
      <div class="page-header" style="margin-bottom:0;">
        <div class="page-title-group">
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
            <a href="/calls" data-route="/calls" class="btn btn-ghost btn-sm">← Back to Calls</a>
            <span class="cell-mono text-muted">/</span>
            <span class="cell-mono" style="color:#fff; font-weight:700;">${incident.calle_run_id || incident.calle_call_id || incident.incident_id}</span>
          </div>
          <h1>Telephony Session Console</h1>
          <p>Linked Incident: <strong>${incident.incident_id}</strong> (${incident.vendor})</p>
        </div>
        <a href="/incidents/${encodeURIComponent(incident.incident_id)}" data-route="/incidents/${encodeURIComponent(incident.incident_id)}" class="btn btn-secondary btn-sm">Open Incident Details</a>
      </div>

      <!-- Centered Phone Console -->
      <div id="call-detail-phone-mount">
        ${renderPhoneConsole(incident, { showDialpad: true, isInteractive: true })}
      </div>

      <!-- Transcript & Extracted Summary -->
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.25rem;">
        <div>
          ${renderTranscript(incident.transcript, incident.status)}
        </div>

        <div style="display:flex; flex-direction:column; gap:1rem;">
          <div class="incident-spec-card">
            <span class="spec-label">SESSION TELEMETRY</span>
            <div class="spec-item">
              <span class="spec-label">CALL-E Run ID</span>
              <span class="spec-val cell-mono text-cyan">${incident.calle_run_id || "Unassigned"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">CALL-E Plan ID</span>
              <span class="spec-val cell-mono">${incident.calle_call_id || "Unassigned"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">Target Phone Destination</span>
              <span class="spec-val cell-mono">${maskPhoneNumber(incident.phone_number)}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">Session Outcome</span>
              <span class="spec-val" style="font-weight:600; color:#fff;">
                ${incident.recovery_summary || (incident.status === 'RECOVERED' ? 'Successfully Recovered' : 'Awaiting Completion')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function bindCallDetailEvents(container) {
  const phoneMount = container.querySelector("#call-detail-phone-mount");
  if (phoneMount) {
    bindPhoneConsoleEvents(phoneMount);
  }
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
