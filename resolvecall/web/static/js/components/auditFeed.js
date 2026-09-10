/**
 * Append-Only Real-Time Operational Audit Feed Component
 * Renders immutable timeline of operational events, telephony actions, and policy decisions.
 */

import { formatTime } from "../store.js";

export function renderAuditFeed(events, options = {}) {
  const maxItems = options.limit || 50;
  const filtered = (events || []).slice(-maxItems).reverse();

  if (filtered.length === 0) {
    return `
      <div class="empty-state-box" style="padding:2rem 1rem;">
        <div class="empty-state-icon" style="width:36px;height:36px;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="empty-state-title" style="font-size:0.85rem;">AUDIT TRAIL EMPTY</div>
        <div class="empty-state-desc" style="font-size:0.75rem;">No operational events have been recorded yet.</div>
      </div>
    `;
  }

  return `
    <div style="display:flex; flex-direction:column; gap:0.65rem;">
      ${filtered.map(e => {
        const time = formatTime(e.timestamp);
        const type = e.event_type || "EVENT";
        const isTelephony = type.startsWith("CALL_") || type === "PLAN_GENERATED";
        const isPolicy = type === "INCIDENT_RECOVERED" || type === "DEADLINE_MISSED" || type === "SECURITY_REJECTED";

        let badgeClass = "badge-secondary";
        if (type === "INCIDENT_RECOVERED") badgeClass = "badge-recovered";
        else if (type === "DEADLINE_MISSED" || type === "SECURITY_REJECTED" || type === "CALL_FAILED") badgeClass = "badge-failed";
        else if (isTelephony) badgeClass = "badge-calling";

        return `
          <div style="background:var(--bg-panel); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:0.65rem 0.85rem; display:flex; flex-direction:column; gap:0.25rem;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
              <span class="badge ${badgeClass}" style="font-size:0.65rem;">${type}</span>
              <span class="cell-mono text-muted" style="font-size:0.7rem;">${time}</span>
            </div>
            <p style="font-size:0.8rem; color:var(--text-primary); margin-top:0.2rem;">${escapeHtml(e.description)}</p>
            ${e.data && Object.keys(e.data).length > 0 ? `
              <details style="margin-top:0.35rem;">
                <summary style="font-size:0.65rem; color:var(--text-muted); cursor:pointer; font-weight:600;">View Metadata</summary>
                <pre class="cell-mono" style="font-size:0.65rem; background:var(--bg-primary); padding:0.4rem; border-radius:var(--radius-sm); margin-top:0.35rem; overflow-x:auto; color:var(--color-cyan);">${escapeHtml(JSON.stringify(e.data, null, 2))}</pre>
              </details>
            ` : ''}
          </div>
        `;
      }).join("")}
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
