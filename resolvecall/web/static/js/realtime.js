/**
 * ResolveCall Realtime SSE Stream Manager
 * Manages EventSource subscription to /api/incidents/{id}/stream
 */

export class RealtimeStream {
  constructor(onUpdate, onInit, onStatusChange) {
    this.eventSource = null;
    this.activeIncidentId = null;
    this.onUpdate = onUpdate || (() => {});
    this.onInit = onInit || (() => {});
    this.onStatusChange = onStatusChange || (() => {});
  }

  connect(incidentId) {
    if (!incidentId) return;

    if (this.eventSource && this.activeIncidentId === incidentId) {
      return; // Already connected to this incident
    }

    this.disconnect();
    this.activeIncidentId = incidentId;
    this.onStatusChange("connecting");

    try {
      this.eventSource = new EventSource(`/api/incidents/${encodeURIComponent(incidentId)}/stream`);

      this.eventSource.onopen = () => {
        this.onStatusChange("connected");
      };

      this.eventSource.addEventListener("init", (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onInit(data);
        } catch (e) {
          console.error("Failed to parse SSE init event", e);
        }
      });

      this.eventSource.addEventListener("update", (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onUpdate(data);
        } catch (e) {
          console.error("Failed to parse SSE update event", e);
        }
      });

      this.eventSource.addEventListener("ping", () => {
        // Keep-alive heartbeat received
      });

      this.eventSource.onerror = (err) => {
        this.onStatusChange("reconnecting");
      };
    } catch (err) {
      console.error("SSE connection error", err);
      this.onStatusChange("error");
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.activeIncidentId = null;
    this.onStatusChange("disconnected");
  }
}
