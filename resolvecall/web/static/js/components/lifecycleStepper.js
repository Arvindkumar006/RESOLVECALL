/**
 * Horizontal Lifecycle Stepper Component
 * RECEIVED → PLANNED → CALLED → NEGOTIATED → VERIFIED → RECOVERED
 * Strictly bound to runtime backend status.
 */

const STAGES = [
  { key: "RECEIVED", label: "Received" },
  { key: "PLANNED", label: "Planned" },
  { key: "CALLED", label: "Calling" },
  { key: "NEGOTIATED", label: "Negotiating" },
  { key: "VERIFIED", label: "Verified" },
  { key: "RECOVERED", label: "Recovered" }
];

export function renderLifecycleStepper(status) {
  const currentStatus = status || "OPEN";

  // Map backend status to stage index
  let activeIndex = 0;
  let isTerminalSuccess = false;
  let isTerminalFailure = false;

  if (currentStatus === "OPEN") {
    activeIndex = 0;
  } else if (currentStatus === "PLANNING") {
    activeIndex = 1;
  } else if (currentStatus === "CALLING") {
    activeIndex = 2;
  } else if (currentStatus === "CONNECTED" || currentStatus === "NEGOTIATING") {
    activeIndex = 3;
  } else if (currentStatus === "VALIDATING") {
    activeIndex = 4;
  } else if (currentStatus === "RECOVERED") {
    activeIndex = 5;
    isTerminalSuccess = true;
  } else if (currentStatus === "DEADLINE_MISSED" || currentStatus === "ESCALATED" || currentStatus === "FAILED") {
    activeIndex = 5;
    isTerminalFailure = true;
  }

  return `
    <div class="lifecycle-stepper" role="region" aria-label="Incident Lifecycle Progress">
      ${STAGES.map((s, idx) => {
        const isCompleted = idx < activeIndex || (idx === 5 && isTerminalSuccess);
        const isActive = idx === activeIndex && !isTerminalSuccess && !isTerminalFailure;
        const isTerminalNode = idx === 5;
        
        let label = s.label;
        if (isTerminalNode) {
          if (currentStatus === "DEADLINE_MISSED") label = "Cutoff Missed";
          else if (currentStatus === "ESCALATED") label = "Escalated";
          else if (currentStatus === "FAILED") label = "Failed";
          else if (currentStatus === "RECOVERED") label = "Recovered";
        }

        const nodeClass = isCompleted ? "completed" : (isActive ? "active" : "");
        const connectorClass = idx < activeIndex ? "completed" : "";

        return `
          <div class="step-node ${nodeClass}">
            <div class="step-num">${isCompleted ? '✓' : (idx + 1)}</div>
            <div class="step-name">${label}</div>
          </div>
          ${idx < STAGES.length - 1 ? `<div class="step-connector ${connectorClass}"></div>` : ''}
        `;
      }).join("")}
    </div>
  `;
}
