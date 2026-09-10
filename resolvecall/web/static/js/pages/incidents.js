/**
 * Enterprise Incidents Page Component
 * Renders data table with telephony indicators, filters, search, and payload ingestion.
 */

import { maskPhoneNumber, formatDateTime } from "../store.js";

export function renderIncidentsPage(incidents = [], currentFilter = "ALL", searchQuery = "") {
  let filtered = incidents;

  if (currentFilter !== "ALL") {
    filtered = filtered.filter(i => {
      if (currentFilter === "ACTIVE") return ["OPEN", "PLANNING", "CALLING", "CONNECTED", "NEGOTIATING", "VALIDATING"].includes(i.status);
      if (currentFilter === "RECOVERED") return i.status === "RECOVERED";
      if (currentFilter === "DEADLINE_MISSED") return i.status === "DEADLINE_MISSED";
      if (currentFilter === "ESCALATED") return i.status === "ESCALATED";
      return true;
    });
  }

  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(i => 
      (i.incident_id || "").toLowerCase().includes(q) ||
      (i.vendor || "").toLowerCase().includes(q) ||
      (i.failure_code || "").toLowerCase().includes(q) ||
      (i.phone_number || "").toLowerCase().includes(q)
    );
  }

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Operational Incidents</h1>
        <p>Manage, inspect, and trigger autonomous telephony recovery across operational exceptions</p>
      </div>
      <button class="btn btn-primary" id="btn-open-ingest-page">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
        Ingest Real Incident
      </button>
    </div>

    <div class="table-panel">
      <!-- Table Header with Search and Filter Tabs -->
      <div class="table-header-bar">
        <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
          <button class="btn btn-sm ${currentFilter === 'ALL' ? 'btn-primary' : 'btn-secondary'}" data-filter="ALL">All (${incidents.length})</button>
          <button class="btn btn-sm ${currentFilter === 'ACTIVE' ? 'btn-primary' : 'btn-secondary'}" data-filter="ACTIVE">Active</button>
          <button class="btn btn-sm ${currentFilter === 'RECOVERED' ? 'btn-primary' : 'btn-secondary'}" data-filter="RECOVERED">Recovered</button>
          <button class="btn btn-sm ${currentFilter === 'DEADLINE_MISSED' ? 'btn-primary' : 'btn-secondary'}" data-filter="DEADLINE_MISSED">Deadline Missed</button>
          <button class="btn btn-sm ${currentFilter === 'ESCALATED' ? 'btn-primary' : 'btn-secondary'}" data-filter="ESCALATED">Escalated</button>
        </div>

        <div class="table-search-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="incidents-search-input" placeholder="Search by ID, carrier, code..." value="${escapeHtml(searchQuery)}" />
        </div>
      </div>

      ${filtered.length === 0 ? `
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
          </div>
          <h3 class="empty-state-title">No operational incidents match your filter</h3>
          <p class="empty-state-desc">Ingest an incident payload or clear search filters to view operational cases.</p>
        </div>
      ` : `
        <table class="data-table">
          <thead>
            <tr>
              <th>Incident</th>
              <th>Status</th>
              <th>Failure Code</th>
              <th>Carrier / Vendor</th>
              <th>Cutoff Limit</th>
              <th>Telephony Destination</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${filtered.map(inc => {
              const hasCall = Boolean(inc.calle_run_id || inc.calle_call_id || ["CALLING", "CONNECTED", "NEGOTIATING"].includes(inc.status));
              return `
                <tr onclick="window.router.navigate('/incidents/${encodeURIComponent(inc.incident_id)}')">
                  <td class="cell-mono">
                    ${hasCall ? `<span class="telephony-row-icon" title="Telephony Call Active/Logged">☎</span>` : ''}
                    <span style="color:#fff; font-weight:700;">${inc.incident_id}</span>
                  </td>
                  <td>
                    <span class="badge badge-${(inc.status || '').toLowerCase()}">${inc.status}</span>
                  </td>
                  <td class="cell-mono text-muted">${inc.failure_code}</td>
                  <td style="color:var(--text-primary); font-weight:500;">${inc.vendor}</td>
                  <td class="cell-mono" style="color:var(--color-amber);">${inc.recovery_deadline}</td>
                  <td class="cell-mono text-muted">${maskPhoneNumber(inc.phone_number)}</td>
                  <td style="font-size:0.75rem; color:var(--text-muted);">${formatDateTime(inc.created_at)}</td>
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

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
