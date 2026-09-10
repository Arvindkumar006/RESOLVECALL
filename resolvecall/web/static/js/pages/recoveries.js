/**
 * Recoveries Operations Page
 * Visualizes the complete operational recovery journey across all incidents:
 * PLAN → CALL → NEGOTIATE → EXTRACT → VERIFY → RECOVER
 */

import { formatDateTime } from "../store.js";

export function renderRecoveriesPage(incidents = []) {
  const recoveredList = incidents.filter(i => ["RECOVERED", "DEADLINE_MISSED", "ESCALATED"].includes(i.status));

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Operational Recoveries</h1>
        <p>End-to-end audit of negotiated commitments and deterministic policy verification</p>
      </div>
      <span class="badge badge-recovered">${recoveredList.length} Concluded Case${recoveredList.length === 1 ? '' : 's'}</span>
    </div>

    <!-- Recovery Pipeline Conceptual Banner -->
    <div style="background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:1.25rem 1.75rem; margin-bottom:1.5rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
      <div style="display:flex; align-items:center; gap:0.65rem; font-size:0.75rem; font-weight:700; color:var(--color-cyan); text-transform:uppercase; letter-spacing:0.08em; flex-wrap:wrap;">
        <span>1. Plan Formulation</span>
        <span class="text-muted">➔</span>
        <span>2. CALL-E Outbound</span>
        <span class="text-muted">➔</span>
        <span>3. Live Negotiation</span>
        <span class="text-muted">➔</span>
        <span>4. Evidence Extraction</span>
        <span class="text-muted">➔</span>
        <span>5. Mathematical Proof</span>
        <span class="text-muted">➔</span>
        <span style="color:var(--color-emerald);">6. Incident Recovered</span>
      </div>
    </div>

    <div class="table-panel">
      <div class="table-header-bar">
        <span class="table-header-title">Recovery Operations Outcomes</span>
        <span class="cell-mono text-muted" style="font-size:0.75rem;">Policy Math: Δ = T_cutoff - T_window</span>
      </div>

      ${recoveredList.length === 0 ? `
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <h3 class="empty-state-title">No recovery operations have completed yet</h3>
          <p class="empty-state-desc">Trigger recovery on an operational incident from the incidents queue to execute the pipeline.</p>
        </div>
      ` : `
        <table class="data-table">
          <thead>
            <tr>
              <th>Incident</th>
              <th>Status</th>
              <th>Carrier / Vendor</th>
              <th>Agreed Window</th>
              <th>Cutoff Limit</th>
              <th>Policy Decision</th>
              <th>Conclusion</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${recoveredList.map(inc => {
              const ev = inc.extracted_evidence;
              const policy = inc.policy_evaluation;
              const winStr = ev?.agreed_window_start && ev?.agreed_window_end 
                ? `${ev.agreed_window_start} – ${ev.agreed_window_end}`
                : (ev?.agreed_window_end || "None");
              return `
                <tr onclick="window.router.navigate('/incidents/${encodeURIComponent(inc.incident_id)}')">
                  <td class="cell-mono" style="color:#fff; font-weight:700;">${inc.incident_id}</td>
                  <td><span class="badge badge-${(inc.status || '').toLowerCase()}">${inc.status}</span></td>
                  <td>${inc.vendor}</td>
                  <td class="cell-mono text-cyan">${winStr}</td>
                  <td class="cell-mono" style="color:var(--color-amber);">${inc.recovery_deadline}</td>
                  <td>
                    <span class="badge ${policy?.decision === 'VALID' ? 'badge-recovered' : 'badge-failed'}">
                      ${policy?.decision || 'EVALUATED'}
                    </span>
                  </td>
                  <td style="font-size:0.8rem;">${inc.recovery_summary || (policy?.reason || 'Completed')}</td>
                  <td>
                    <a href="/incidents/${encodeURIComponent(inc.incident_id)}" data-route="/incidents/${encodeURIComponent(inc.incident_id)}" class="btn btn-secondary btn-sm" style="padding:0.25rem 0.6rem;">Review Proof</a>
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
