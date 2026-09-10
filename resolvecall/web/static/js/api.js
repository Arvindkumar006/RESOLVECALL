/**
 * ResolveCall API Client
 * Enterprise client for ResolveCall backend.
 * Uses HttpOnly secure session cookies as the sole authentication mechanism.
 * Uses credentials: "same-origin".
 * Strictly zero JWT tokens exposed to or persisted in browser JavaScript.
 */

async function request(url, options = {}) {
  const defaultOptions = {
    credentials: "same-origin",
    headers: {}
  };

  const merged = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {})
    }
  };

  const res = await fetch(url, merged);

  if (res.status === 401) {
    // Notify app of session expiration / unauthorized status
    window.dispatchEvent(new CustomEvent("resolvecall:unauthorized"));
  }

  return res;
}

export const api = {
  // Authentication Endpoints (Cookie-based session)
  auth: {
    async login(email, password) {
      const res = await request("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Invalid email or password");
      return data;
    },

    async register(name, email, password) {
      const res = await request("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      return data;
    },

    async getMe() {
      const res = await request("/api/auth/me");
      if (!res.ok) return null;
      return await res.json();
    },

    async logout() {
      const res = await request("/api/auth/logout", { method: "POST" });
      if (!res.ok) throw new Error("Logout failed");
      return await res.json();
    },

    async getProviders() {
      const res = await request("/api/auth/providers");
      if (!res.ok) return { providers: { google: false, github: false, linkedin: false } };
      return await res.json();
    }
  },

  /**
   * List all ingested operational incidents
   * GET /api/incidents
   */
  async getIncidents() {
    const res = await request("/api/incidents");
    if (!res.ok) throw new Error(`Failed to load incidents: ${res.statusText}`);
    return await res.json();
  },

  /**
   * Get full details of a specific incident
   * GET /api/incidents/{id}
   */
  async getIncident(incidentId) {
    const res = await request(`/api/incidents/${encodeURIComponent(incidentId)}`);
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
    const res = await request("/api/incidents/ingest", {
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
   */
  async triggerRecovery(incidentId) {
    const res = await request(`/api/incidents/${encodeURIComponent(incidentId)}/recover`, {
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
    const res = await request(url);
    if (!res.ok) throw new Error(`Failed to load audit trail: ${res.statusText}`);
    return await res.json();
  },

  /**
   * Backend system health check
   * GET /api/health
   */
  async getHealth() {
    const res = await request("/api/health");
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return await res.json();
  }
};
