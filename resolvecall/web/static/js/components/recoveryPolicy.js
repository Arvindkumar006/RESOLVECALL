/**
 * Deterministic Recovery Policy & Verification Component
 * Visualizes extracted structured evidence, the temporal delta buffer math
 * (Δ = Deadline - Proposed), and deterministic compliance criteria.
 */

export function renderRecoveryPolicy(incident) {
  const ev = incident?.extracted_evidence;
  const policy = incident?.policy_evaluation;
  const deadline = incident?.recovery_deadline || "Not available";
  const status = incident?.status || "OPEN";

  const winStart = ev?.agreed_window_start;
  const winEnd = ev?.agreed_window_end;
  const windowStr = winStart && winEnd ? `${winStart} → ${winEnd}` : (winEnd || "Not available");
  const repName = ev?.representative_name || "Not available";
  const authCode = ev?.authorization_code || (incident?.authorization_info?.clearance_reference || "Not available");

  // Determine policy decision
  const decision = policy?.decision; // "VALID", "INVALID", "AMBIGUOUS", or undefined
  const reason = policy?.reason || "Awaiting call completion and policy validation";

  // Compute Delta Buffer if available
  let bufferMinutes = null;
  let bufferDisplay = "Pending Evaluation";
  let bufferClass = "invalid";

  if (decision === "VALID") {
    bufferClass = "valid";
    bufferDisplay = "POLICY SATISFIED (On-Time)";
  } else if (decision === "INVALID") {
    bufferClass = "invalid";
    bufferDisplay = "CUTOFF EXCEEDED";
  } else if (decision === "AMBIGUOUS") {
    bufferClass = "invalid";
    bufferDisplay = "UNCONFIRMED";
  }

  // Outcome status badge & semantics
  let outcomeBadge = "";
  if (status === "RECOVERED") {
    outcomeBadge = `<span class="badge badge-recovered">✓ RECOVERED</span>`;
  } else if (status === "DEADLINE_MISSED") {
    outcomeBadge = `<span class="badge badge-failed">DEADLINE MISSED</span>`;
  } else if (status === "ESCALATED") {
    outcomeBadge = `<span class="badge badge-escalated">ESCALATED</span>`;
  } else if (status === "CALLING" || status === "NEGOTIATING") {
    outcomeBadge = `<span class="badge badge-calling">NEGOTIATION IN PROGRESS</span>`;
  } else if (status === "PLANNING") {
    outcomeBadge = `<span class="badge badge-planning">PLANNING RECOVERY</span>`;
  } else {
    outcomeBadge = `<span class="badge" style="background:var(--bg-panel);color:var(--text-muted);">AWAITING RECOVERY</span>`;
  }

  return `
    <div class="verification-card">
      <div class="verification-header">
        <div class="verification-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span>RECOVERY VERIFICATION</span>
        </div>
        ${outcomeBadge}
      </div>

      <!-- Mathematical Buffer Box -->
      <div class="math-buffer-box">
        <div class="math-title">Deterministic Temporal Policy Engine</div>
        <div class="math-timeline-row">
          <div class="math-point">
            <span class="point-label">Agreed Window</span>
            <span class="point-val">${winEnd || "--:--"}</span>
          </div>
          <span class="math-arrow">➔</span>
          <div class="math-point">
            <span class="point-label">Deadline Cutoff</span>
            <span class="point-val">${deadline}</span>
          </div>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; margin-top:0.25rem;">
          <span class="margin-pill ${bufferClass}">
            ${decision === "VALID" ? "✓" : "!"} ${bufferDisplay}
          </span>
          <span class="cell-mono text-muted" style="font-size:0.7rem;">Δ = T_cutoff - T_window</span>
        </div>
      </div>

      <!-- Deterministic Policy Checklist -->
      <div class="policy-checklist">
        <div class="checklist-item">
          <span class="check-icon ${winEnd ? 'valid' : (decision ? 'invalid' : 'pending')}">
            ${winEnd ? '✓' : (decision ? '✕' : '○')}
          </span>
          <span>Delivery Window Confirmed</span>
        </div>
        <div class="checklist-item">
          <span class="check-icon ${ev?.resolution_status === 'CONFIRMED' || status === 'RECOVERED' ? 'valid' : (decision ? 'invalid' : 'pending')}">
            ${ev?.resolution_status === 'CONFIRMED' || status === 'RECOVERED' ? '✓' : (decision ? '✕' : '○')}
          </span>
          <span>Required Action Committed</span>
        </div>
        <div class="checklist-item">
          <span class="check-icon ${authCode !== 'Not available' ? 'valid' : 'pending'}">
            ${authCode !== 'Not available' ? '✓' : '○'}
          </span>
          <span>Authorization Clearance Transmitted</span>
        </div>
        <div class="checklist-item">
          <span class="check-icon ${decision === 'VALID' ? 'valid' : (decision ? 'invalid' : 'pending')}">
            ${decision === 'VALID' ? '✓' : (decision ? '✕' : '○')}
          </span>
          <span>Deadline Boundary Satisfied</span>
        </div>
      </div>

      <!-- Extracted Evidence Attributes -->
      <div class="evidence-attributes-grid">
        <div class="ev-attr-card">
          <span class="ev-attr-label">Delivery Window</span>
          <span class="ev-attr-val cell-mono">${windowStr}</span>
        </div>
        <div class="ev-attr-card">
          <span class="ev-attr-label">Representative</span>
          <span class="ev-attr-val">${repName}</span>
        </div>
        <div class="ev-attr-card">
          <span class="ev-attr-label">Auth / Clearance</span>
          <span class="ev-attr-val cell-mono">${authCode}</span>
        </div>
        <div class="ev-attr-card">
          <span class="ev-attr-label">Policy Status</span>
          <span class="ev-attr-val ${decision === 'VALID' ? 'text-emerald' : (decision === 'INVALID' ? 'text-rose' : '')}">
            ${decision || "Awaiting Call"}
          </span>
        </div>
      </div>

      <!-- Policy Engine Reason Note -->
      <div style="background:var(--bg-panel); border:1px solid var(--border-subtle); border-radius:var(--radius-md); padding:0.75rem; font-size:0.775rem;">
        <span class="spec-label">Policy Engine Determination:</span>
        <p style="color:var(--text-secondary); margin-top:0.25rem;">${reason}</p>
      </div>

      <!-- Auditable Spoken Quotes -->
      <div class="auditable-quotes-block">
        <span class="spec-label">Auditable Spoken Quotes</span>
        ${ev?.raw_evidence_quotes && ev.raw_evidence_quotes.length > 0
          ? ev.raw_evidence_quotes.map(q => `<div class="quote-item">"${escapeHtml(q)}"</div>`).join("")
          : `<div class="text-muted" style="font-size:0.75rem;">No verbatim evidence quotes extracted yet.</div>`
        }
      </div>
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
