/**
 * Enterprise Live Call Transcript Component
 * Renders distinct speaker roles: RESOLVECALL AGENT vs OPERATIONS CONTACT.
 * Never invents fake speech or hardcodes fabricated turns.
 */

export function renderTranscript(turns, callStatus) {
  const isLive = ["CALLING", "CONNECTED", "NEGOTIATING"].includes(callStatus);
  const statusLabel = isLive ? "● LIVE" : (turns && turns.length > 0 ? "ENDED" : "IDLE");
  const statusClass = isLive ? "badge-calling" : "badge-secondary";

  let bodyContent = "";

  if (!turns || turns.length === 0) {
    bodyContent = `
      <div class="empty-state-box" style="padding:2.5rem 1rem;">
        <div class="empty-state-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div class="empty-state-title" style="font-size:0.9rem;">TRANSCRIPT NOT AVAILABLE</div>
        <div class="empty-state-desc" style="font-size:0.75rem;">
          ${isLive ? "Line connected. Awaiting initial speech packets..." : "No conversation has been recorded for this operational incident."}
        </div>
      </div>
    `;
  } else {
    bodyContent = turns.map((t, idx) => {
      const rawRole = (t.role || "").toLowerCase();
      const isAgent = rawRole.includes("agent") || rawRole.includes("assistant") || rawRole.includes("caller");
      const roleLabel = isAgent ? "RESOLVECALL AGENT" : "OPERATIONS CONTACT";
      const bubbleClass = isAgent ? "agent" : "contact";
      const timeStr = t.timestamp || `Turn ${idx + 1}`;

      return `
        <div class="chat-bubble-row ${bubbleClass}">
          <div class="speaker-pill">
            <span>${roleLabel}</span>
            <span class="chat-time">${timeStr}</span>
          </div>
          <div class="chat-bubble">
            ${escapeHtml(t.text || "")}
          </div>
        </div>
      `;
    }).join("");
  }

  return `
    <div class="transcript-card" id="transcript-card-container">
      <div class="transcript-header">
        <div class="transcript-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span>LIVE CALL TRANSCRIPT</span>
        </div>
        <span class="badge ${statusClass}">${statusLabel}</span>
      </div>
      <div class="transcript-body" id="transcript-body-scroll">
        ${bodyContent}
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function scrollTranscriptToBottom(container) {
  const scrollEl = container.querySelector("#transcript-body-scroll");
  if (scrollEl) {
    scrollEl.scrollTop = scrollEl.scrollHeight;
  }
}
