/**
 * ResolveCall API Client
 * Enterprise wrapper for all existing backend endpoints.
 * Never invents non-existent API routes.
 */

export const api = {
  /**
   * List all ingested operational incidents
   * GET /api/incidents
   */
  async getIncidents() {
    const res = await fetch("/api/incidents");
    if (!res.ok) throw new Error(`Failed to load incidents: ${res.statusText}`);
    return await res.json();
  },

  /**
   * Get full details of a specific incident
   * GET /api/incidents/{id}
   */
  async getIncident(incidentId) {
    const res = await fetch(`/api/incidents/${encodeURIComponent(incidentId)}`);
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error(`Failed to load incident ${incidentId}: ${res.statusText}`);
    }
    return await res.json();
  },

  /**
   * Ingest a new operational incident JSON payload
   * POST /api/incidents/ingest
   */
  async ingestIncident(payload) {
    const res = await fetch("/api/incidents/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.message || "Failed to ingest incident");
    return data;
  },

  /**
   * Trigger autonomous recovery for an incident
   * POST /api/incidents/{id}/recover
   * NOTE: Strictly only called when the operator explicitly clicks the recovery action.
   */
  async triggerRecovery(incidentId) {
    const res = await fetch(`/api/incidents/${encodeURIComponent(incidentId)}/recover`, {
      method: "POST"
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.message || "Failed to trigger recovery");
    return data;
  },

  /**
   * Retrieve immutable audit trail events
   * GET /api/audit?incident_id={id}
   */
  async getAuditTrail(incidentId = null) {
    const url = incidentId 
      ? `/api/audit?incident_id=${encodeURIComponent(incidentId)}`
      : "/api/audit";
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load audit trail: ${res.statusText}`);
    return await res.json();
  },

  /**
   * Backend system health check
   * GET /api/health
   */
  async getHealth() {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return await res.json();
  }
};
