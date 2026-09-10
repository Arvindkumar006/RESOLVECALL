/**
 * Enterprise Audit Trail Page
 * Full system timeline of every event, telephony action, token, and policy delta.
 */

import { renderAuditFeed } from "../components/auditFeed.js";

export function renderAuditPage(auditEvents = [], currentFilter = "ALL") {
  let filtered = auditEvents;
  if (currentFilter !== "ALL") {
    filtered = filtered.filter(e => {
      if (currentFilter === "TELEPHONY") return (e.event_type || "").startsWith("CALL_");
      if (currentFilter === "POLICY") return ["INCIDENT_RECOVERED", "DEADLINE_MISSED", "SECURITY_REJECTED"].includes(e.event_type);
      if (currentFilter === "INGESTION") return e.event_type === "INCIDENT_RECEIVED";
      return true;
    });
  }

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Operational Audit Trail</h1>
        <p>Append-only immutable record of incidents, telephony signals, and mathematical policy checks</p>
      </div>
      <span class="cell-mono text-muted" style="font-size:0.75rem;">${auditEvents.length} Total Events Logged</span>
    </div>

    <div class="table-panel">
      <div class="table-header-bar">
        <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
          <button class="btn btn-sm ${currentFilter === 'ALL' ? 'btn-primary' : 'btn-secondary'}" data-audit-filter="ALL">All Events (${auditEvents.length})</button>
          <button class="btn btn-sm ${currentFilter === 'TELEPHONY' ? 'btn-primary' : 'btn-secondary'}" data-audit-filter="TELEPHONY">Telephony Sessions</button>
          <button class="btn btn-sm ${currentFilter === 'POLICY' ? 'btn-primary' : 'btn-secondary'}" data-audit-filter="POLICY">Policy Determinations</button>
          <button class="btn btn-sm ${currentFilter === 'INGESTION' ? 'btn-primary' : 'btn-secondary'}" data-audit-filter="INGESTION">Ingestion Triggers</button>
        </div>
      </div>

      <div style="padding:1.5rem;">
        ${renderAuditFeed(filtered, { limit: 100 })}
      </div>
    </div>
  `;
}
