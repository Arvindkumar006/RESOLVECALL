/**
 * Operations Console / Overview Page
 * Primary mission control view with Active Telephony widget, metrics, and incident pipeline.
 */

import { renderPhoneConsole, bindPhoneConsoleEvents } from "../components/phoneConsole.js";
import { maskPhoneNumber } from "../store.js";

export function renderConsolePage(incidents = []) {
  const activeIncidents = incidents.filter(i => ["OPEN", "PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(i.status));
  const activeCallInc = incidents.find(i => ["CALLING", "CONNECTED", "NEGOTIATING"].includes(i.status));
  const recoveredIncidents = incidents.filter(i => i.status === "RECOVERED");
  const pendingRecoveries = incidents.filter(i => ["OPEN", "PLANNING"].includes(i.status));

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Recovery Operations Console</h1>
        <p>Real-time autonomous telephony supervision and incident lifecycle monitoring</p>
      </div>
      <div style="display:flex; gap:0.5rem;">
        <button class="btn btn-secondary btn-sm" id="btn-refresh-console">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
          Refresh
        </button>
        <button class="btn btn-primary btn-sm" id="btn-open-ingest-top">
          + Ingest Incident
        </button>
      </div>
    </div>

    <!-- Metrics Row -->
    <div class="metrics-row">
      <div class="metric-box">
        <span class="metric-box-label">Active Incidents</span>
        <span class="metric-box-val">${activeIncidents.length}</span>
        <span class="metric-box-sub text-muted">Awaiting resolution</span>
      </div>

      <div class="metric-box">
        <span class="metric-box-label">Active PSTN Calls</span>
        <span class="metric-box-val" style="color:var(--color-cyan);">${activeCallInc ? '1' : '0'}</span>
        <span class="metric-box-sub">
          <span class="status-dot ${activeCallInc ? 'pulsing' : ''}" style="background:${activeCallInc ? 'var(--color-cyan)' : 'var(--text-muted)'};"></span>
          <span>${activeCallInc ? 'Line active' : 'Lines idle'}</span>
        </span>
      </div>

      <div class="metric-box">
        <span class="metric-box-label">Recovered</span>
        <span class="metric-box-val" style="color:var(--color-emerald);">${recoveredIncidents.length}</span>
        <span class="metric-box-sub text-muted">Policy verified on-time</span>
      </div>

      <div class="metric-box">
        <span class="metric-box-label">Pending Recovery</span>
        <span class="metric-box-val" style="color:var(--color-amber);">${pendingRecoveries.length}</span>
        <span class="metric-box-sub text-muted">Queued for action</span>
      </div>
    </div>

    <!-- Active Telephony Section -->
    <div style="margin-bottom:1.75rem;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem;">
        <span class="spec-label" style="font-size:0.75rem;">ACTIVE TELEPHONY</span>
        <span class="cell-mono text-muted" style="font-size:0.7rem;">PSTN Gateway: CALL-E</span>
      </div>

      ${activeCallInc ? `
        <div style="max-width:580px;">
          ${renderPhoneConsole(activeCallInc, { isInteractive: true })}
        </div>
      ` : `
        <div style="background:var(--bg-secondary); border:1px dashed var(--border-default); border-radius:var(--radius-xl); padding:2rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
          <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:44px; height:44px; border-radius:50%; background:var(--bg-panel); border:1px solid var(--border-subtle); display:flex; align-items:center; justify-content:center; color:var(--text-muted);">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            </div>
            <div>
              <h3 style="font-size:0.95rem; font-weight:700; color:#fff;">NO ACTIVE CALLS</h3>
              <p style="font-size:0.8rem; color:var(--text-secondary);">Telephony lines are currently idle. Outbound calls initiate strictly upon incident recovery trigger.</p>
            </div>
          </div>
          <a href="/incidents" data-route="/incidents" class="btn btn-secondary btn-sm">View Incidents Queue</a>
        </div>
      `}
    </div>

    <!-- Recent Incidents Table -->
    <div class="table-panel">
      <div class="table-header-bar">
        <span class="table-header-title">Operational Incidents Queue</span>
        <a href="/incidents" data-route="/incidents" class="btn btn-ghost btn-sm">View All Incidents ➔</a>
      </div>

      ${incidents.length === 0 ? `
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
          </div>
          <h3 class="empty-state-title">No operational incidents require recovery</h3>
          <p class="empty-state-desc">The operations queue is clear. Click "+ Ingest Incident" to ingest a real payload into the system.</p>
        </div>
      ` : `
        <table class="data-table">
          <thead>
            <tr>
              <th>Incident</th>
              <th>Status</th>
              <th>Vendor</th>
              <th>Destination</th>
              <th>Cutoff Deadline</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${incidents.slice(0, 5).map(inc => {
              const hasCall = Boolean(inc.calle_run_id || inc.calle_call_id || ["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status));
              return `
                <tr onclick="window.router.navigate('/incidents/${encodeURIComponent(inc.incident_id)}')">
                  <td class="cell-mono">
                    ${hasCall ? `<span class="telephony-row-icon" title="Telephony Call Associated">☎</span>` : ''}
                    ${inc.incident_id}
                  </td>
                  <td>
                    <span class="badge badge-${(inc.status || '').toLowerCase()}">${inc.status}</span>
                  </td>
                  <td style="color:#fff; font-weight:500;">${inc.vendor}</td>
                  <td class="cell-mono text-muted">${maskPhoneNumber(inc.phone_number)}</td>
                  <td class="cell-mono" style="color:var(--color-amber);">${inc.recovery_deadline}</td>
                  <td>
                    <a href="/incidents/${encodeURIComponent(inc.incident_id)}" data-route="/incidents/${encodeURIComponent(inc.incident_id)}" class="btn btn-secondary btn-sm" style="padding:0.25rem 0.6rem;">Open Console</a>
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

export function bindConsoleEvents(container) {
  const phoneConsole = container.querySelector("#phone-console-widget");
  if (phoneConsole) {
    bindPhoneConsoleEvents(phoneConsole);
  }
}
