/**
 * Recovery Plans Intelligence Page
 * Visualizes dynamic recovery strategies, operational constraints, and anti-phishing sanitized credentials.
 */

export function renderPlansPage(incidents = []) {
  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Autonomous Recovery Plans</h1>
        <p>Structured operational negotiation objectives and anti-phishing credential guardrails</p>
      </div>
      <span class="cell-mono text-muted" style="font-size:0.75rem;">AI Recovery Planner Engine</span>
    </div>

    ${incidents.length === 0 ? `
      <div class="table-panel">
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <h3 class="empty-state-title">No recovery plans generated</h3>
          <p class="empty-state-desc">Plans are dynamically formulated when operational incidents are ingested and evaluated.</p>
        </div>
      </div>
    ` : `
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:1.25rem;">
        ${incidents.map(inc => {
          const authInfo = inc.authorization_info || {};
          return `
            <div class="incident-spec-card">
              <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-subtle); padding-bottom:0.75rem;">
                <span class="cell-mono" style="color:#fff; font-weight:700;">${inc.incident_id}</span>
                <span class="badge badge-secondary">${inc.failure_code}</span>
              </div>

              <div class="spec-item">
                <span class="spec-label">Target Carrier</span>
                <span class="spec-val" style="color:#fff; font-weight:600;">${inc.vendor}</span>
              </div>

              <div class="spec-item">
                <span class="spec-label">Operational Cutoff Limit</span>
                <span class="spec-val cell-mono" style="color:var(--color-amber);">${inc.recovery_deadline}</span>
              </div>

              <div class="spec-item">
                <span class="spec-label">Negotiation Directive</span>
                <span class="spec-val" style="font-size:0.8rem; line-height:1.4;">${inc.required_action}</span>
              </div>

              <div style="background:var(--bg-panel); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:0.75rem;">
                <span class="spec-label" style="display:block; margin-bottom:0.35rem;">Sanitized Credentials (Anti-Phishing Guardrail)</span>
                ${Object.keys(authInfo).length > 0 ? Object.keys(authInfo).map(k => `
                  <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:0.2rem;">
                    <span class="text-muted">${k}:</span>
                    <span class="cell-mono text-cyan">${escapeHtml(String(authInfo[k]))}</span>
                  </div>
                `).join("") : `<span class="text-muted" style="font-size:0.75rem;">Standard operational clearance</span>`}
              </div>

              <div style="margin-top:0.5rem; display:flex; justify-content:flex-end;">
                <a href="/incidents/${encodeURIComponent(inc.incident_id)}" data-route="/incidents/${encodeURIComponent(inc.incident_id)}" class="btn btn-secondary btn-sm">Inspect Execution</a>
              </div>
            </div>
          `;
        }).join("")}
      </div>
    `}
  `;
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
