/**
 * Evidence Ledger Page
 * Structured verification evidence extracted from live CALL-E PSTN phone calls.
 */

import { formatDateTime } from "../store.js";

export function renderEvidencePage(incidents = []) {
  const evidenceIncidents = incidents.filter(i => Boolean(i.extracted_evidence));

  return `
    <div class="page-header">
      <div class="page-title-group">
        <h1>Extracted Recovery Evidence</h1>
        <p>Verifiable commitments and structured operational records parsed from conversation turns</p>
      </div>
      <span class="cell-mono text-muted" style="font-size:0.75rem;">Structured Extractor Engine</span>
    </div>

    <div class="table-panel">
      <div class="table-header-bar">
        <span class="table-header-title">Auditable Operational Commitments</span>
        <span class="cell-mono text-muted" style="font-size:0.75rem;">Tamper-Proof Audio Extraction</span>
      </div>

      ${evidenceIncidents.length === 0 ? `
        <div class="empty-state-box">
          <div class="empty-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <h3 class="empty-state-title">No recovery evidence has been extracted</h3>
          <p class="empty-state-desc">Evidence fields are populated automatically when an outbound call connects and negotiation turns occur.</p>
        </div>
      ` : `
        <table class="data-table">
          <thead>
            <tr>
              <th>Incident</th>
              <th>Confirmed Window</th>
              <th>Representative</th>
              <th>Clearance / Auth</th>
              <th>Policy Result</th>
              <th>Auditable Quotes</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${evidenceIncidents.map(inc => {
              const ev = inc.extracted_evidence || {};
              const policy = inc.policy_evaluation || {};
              const winStr = ev.agreed_window_start && ev.agreed_window_end 
                ? `${ev.agreed_window_start} – ${ev.agreed_window_end}`
                : (ev.agreed_window_end || "None");
              const quotesCount = (ev.raw_evidence_quotes || []).length;

              return `
                <tr onclick="window.router.navigate('/incidents/${encodeURIComponent(inc.incident_id)}')">
                  <td class="cell-mono" style="color:#fff; font-weight:700;">${inc.incident_id}</td>
                  <td class="cell-mono text-cyan">${winStr}</td>
                  <td>${ev.representative_name || "Unspecified"}</td>
                  <td class="cell-mono text-muted">${ev.authorization_code || "None"}</td>
                  <td>
                    <span class="badge ${policy.decision === 'VALID' ? 'badge-recovered' : 'badge-failed'}">
                      ${policy.decision || 'EVALUATED'}
                    </span>
                  </td>
                  <td style="font-size:0.75rem; color:var(--text-muted);">${quotesCount} verbatim quote${quotesCount === 1 ? '' : 's'}</td>
                  <td>
                    <a href="/incidents/${encodeURIComponent(inc.incident_id)}" data-route="/incidents/${encodeURIComponent(inc.incident_id)}" class="btn btn-secondary btn-sm" style="padding:0.25rem 0.6rem;">Inspect Proof</a>
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
