/**
 * ResolveCall Main Application Controller
 * Orchestrates routing, SSE streaming, store updates, modals, and enterprise view rendering.
 */

import { api } from "./api.js";
import { store } from "./store.js";
import { RealtimeStream } from "./realtime.js";
import { Router } from "./router.js";

// Import Page Renderers
import { renderLandingPage } from "./pages/landing.js";
import {
  renderHowItWorksPage,
  renderArchitecturePage,
  renderSecurityPage,
  renderLoginPage,
  renderSignupPage,
  renderOnboardingPage,
  bindLoginEvents,
  bindSignupEvents,
  bindOnboardingEvents
} from "./pages/publicPages.js";
import { renderConsolePage, bindConsoleEvents } from "./pages/console.js";
import { renderIncidentsPage } from "./pages/incidents.js";
import { renderIncidentDetailPage, bindIncidentDetailEvents } from "./pages/incidentDetail.js";
import { renderCallsPage, renderCallDetailPage, bindCallDetailEvents } from "./pages/calls.js";
import { renderRecoveriesPage } from "./pages/recoveries.js";
import { renderPlansPage } from "./pages/plans.js";
import { renderEvidencePage } from "./pages/evidence.js";
import { renderAuditPage } from "./pages/audit.js";
import { renderSettingsPage } from "./pages/settings.js";

// Global Ingest Payload Template
const DEFAULT_INGEST_PAYLOAD = {
  incident_id: "INC-202609-001",
  failure_code: "DELIVERY_ACCESS_BLOCKED",
  failure_description: "Driver unable to complete dropoff due to security checkpoint restriction.",
  vendor: "Regional Freight Lines",
  contact_name: "Dispatch Operations",
  phone_number: "+18005550199",
  recovery_deadline: "16:00",
  required_action: "Provide delivery clearance reference to dispatch and confirm redelivery before 16:00 cutoff today.",
  authorization_info: {
    clearance_reference: "REF-9821",
    facility_access_code: "5501"
  }
};

class Application {
  constructor() {
    this.router = null;
    this.stream = null;
    this.currentFilter = "ALL";
    this.searchQuery = "";
    this.auditFilter = "ALL";
    this.currentIncident = null;
  }

  async init() {
    this.setupSSE();
    this.setupModal();
    this.setupSidebar();
    this.setupRouter();

    // Initial Data Fetch
    await this.refreshData();

    // Start Router
    this.router.init();
    window.router = this.router;
  }

  setupSSE() {
    this.stream = new RealtimeStream(
      (update) => this.handleSSEUpdate(update),
      (initialData) => this.handleSSEInit(initialData),
      (status) => this.handleSSEStatus(status)
    );
  }

  handleSSEUpdate(data) {
    if (data.type === "audit_event") {
      this.showToast(`Telephony Event: ${data.event.event_type}`, "success");
      
      // Update incident if matching
      if (data.incident) {
        const idx = store.incidents.findIndex(i => i.incident_id === data.incident.incident_id);
        if (idx >= 0) {
          store.incidents[idx] = data.incident;
        } else {
          store.incidents.push(data.incident);
        }
        store.setIncidents([...store.incidents]);

        if (this.currentIncident && this.currentIncident.incident_id === data.incident.incident_id) {
          this.currentIncident = data.incident;
          this.reRenderCurrentView();
        }
      }

      // Refresh audit trail
      if (this.currentIncident) {
        api.getAuditTrail(this.currentIncident.incident_id).then(events => {
          store.setAuditLog(events);
          this.reRenderCurrentView();
        });
      }
    }
  }

  handleSSEInit(incidentData) {
    if (incidentData && this.currentIncident && this.currentIncident.incident_id === incidentData.incident_id) {
      this.currentIncident = incidentData;
      this.reRenderCurrentView();
    }
  }

  handleSSEStatus(status) {
    const statusChip = document.getElementById("nav-sse-status");
    if (statusChip) {
      if (status === "connected") {
        statusChip.className = "telephony-live-chip active";
        statusChip.innerHTML = `<span class="status-dot"></span><span>CALL-E Connected</span>`;
      } else if (status === "reconnecting") {
        statusChip.className = "telephony-live-chip";
        statusChip.innerHTML = `<span class="status-dot amber pulsing"></span><span>Connecting...</span>`;
      } else {
        statusChip.className = "telephony-live-chip";
        statusChip.innerHTML = `<span class="status-dot" style="background:var(--text-muted);"></span><span>PSTN Gateway Ready</span>`;
      }
    }
  }

  async refreshData() {
    try {
      const [incidents, health, audit] = await Promise.all([
        api.getIncidents().catch(() => []),
        api.getHealth().catch(() => null),
        api.getAuditTrail().catch(() => [])
      ]);
      store.setIncidents(incidents);
      store.setHealth(health);
      store.setAuditLog(audit);
      this.updateSidebarBadges();
    } catch (err) {
      console.error("Data refresh failed", err);
    }
  }

  updateSidebarBadges() {
    const incBadge = document.getElementById("sidebar-inc-badge");
    if (incBadge) {
      incBadge.textContent = String(store.incidents.length);
    }
    const callsBadge = document.getElementById("sidebar-calls-badge");
    if (callsBadge) {
      const activeCalls = store.incidents.filter(i => ["CALLING", "CONNECTED", "NEGOTIATING"].includes(i.status));
      callsBadge.textContent = String(activeCalls.length);
    }
  }

  updateUserProfileInSidebar() {
    const profileContainer = document.querySelector(".sidebar-footer .org-profile");
    if (profileContainer && store.currentUser) {
      const initials = (store.currentUser.name || "RC").slice(0, 2).toUpperCase();
      const providerLabel = store.currentUser.provider ? `${store.currentUser.provider.toUpperCase()}` : "SSO";
      profileContainer.innerHTML = `
        <div class="org-avatar" title="${store.currentUser.name}">${initials}</div>
        <div class="org-info" style="flex:1; overflow:hidden;">
          <span class="org-name" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${store.currentUser.name}</span>
          <span class="org-env" style="font-size:0.65rem; color:var(--color-cyan);">${providerLabel} Verified</span>
        </div>
        <button class="btn btn-ghost btn-sm" id="btn-sign-out" title="Sign Out" style="padding:0.25rem 0.4rem; color:var(--text-muted); margin-left:auto;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
        </button>
      `;
      const signoutBtn = profileContainer.querySelector("#btn-sign-out");
      if (signoutBtn) {
        signoutBtn.addEventListener("click", () => {
          store.logoutUser();
          this.showToast("Signed out of recovery console", "info");
          this.router.navigate("/login");
        });
      }
    }
  }

  setupRouter() {
    const routes = [
      { pattern: "/", name: "landing", isPublic: true },
      { pattern: "/how-it-works", name: "how-it-works", isPublic: true },
      { pattern: "/architecture", name: "architecture", isPublic: true },
      { pattern: "/security", name: "security", isPublic: true },
      { pattern: "/login", name: "login", isPublic: true },
      { pattern: "/signup", name: "signup", isPublic: true },
      { pattern: "/onboarding", name: "onboarding", isPublic: true },
      { pattern: "/console", name: "console", isPublic: false },
      { pattern: "/incidents", name: "incidents", isPublic: false },
      { pattern: "/incidents/:id", name: "incident-detail", isPublic: false },
      { pattern: "/calls", name: "calls", isPublic: false },
      { pattern: "/calls/:id", name: "call-detail", isPublic: false },
      { pattern: "/recoveries", name: "recoveries", isPublic: false },
      { pattern: "/plans", name: "plans", isPublic: false },
      { pattern: "/evidence", name: "evidence", isPublic: false },
      { pattern: "/audit", name: "audit", isPublic: false },
      { pattern: "/security-settings", name: "security-settings", isPublic: false },
      { pattern: "/settings", name: "settings", isPublic: false }
    ];

    this.router = new Router(routes, (route, params, path) => {
      this.handleRouteChanged(route, params, path);
    });
  }

  async handleRouteChanged(route, params, path) {
    const appContainer = document.getElementById("app-root");
    const sidebar = document.getElementById("app-sidebar");
    const topbar = document.getElementById("app-topbar");
    const viewport = document.getElementById("app-viewport");
    const breadcrumb = document.getElementById("topbar-page-breadcrumb");

    // Close mobile drawer if open
    sidebar.classList.remove("open");

    // Active navigation highlight
    document.querySelectorAll(".nav-item").forEach(item => {
      item.classList.remove("active");
      if (item.getAttribute("data-route") === path || item.getAttribute("href") === path) {
        item.classList.add("active");
      }
    });

    // Hackathon submission mode: Order is directly Landing Page -> Console
    // No login/signup barrier for hackathon judges/evaluators
    if (route.name === "login" || route.name === "signup" || route.name === "onboarding") {
      this.router.navigate("/console");
      return;
    }

    if (route.isPublic) {
      sidebar.style.display = "none";
      topbar.style.display = "none";
      viewport.style.padding = "0";
      viewport.style.maxWidth = "100%";

      if (route.name === "landing") {
        viewport.innerHTML = renderLandingPage();
      } else if (route.name === "how-it-works") {
        viewport.innerHTML = renderHowItWorksPage();
      } else if (route.name === "architecture") {
        viewport.innerHTML = renderArchitecturePage();
      } else if (route.name === "security") {
        viewport.innerHTML = renderSecurityPage();
      }
      
      this.stream.disconnect();
      return;
    }

    // Authenticated Shell
    sidebar.style.display = "flex";
    topbar.style.display = "flex";
    viewport.style.padding = "1.75rem";
    viewport.style.maxWidth = "1600px";
    this.updateUserProfileInSidebar();

    if (breadcrumb) {
      const titles = {
        "console": "Operations Console",
        "incidents": "Incidents Queue",
        "incident-detail": `Incident ${params.id || ''}`,
        "calls": "Telephony Operations",
        "call-detail": `Call Console (${params.id || ''})`,
        "recoveries": "Operational Recoveries",
        "plans": "Recovery Plans",
        "evidence": "Evidence Ledger",
        "audit": "Audit Trail",
        "security-settings": "Telephony Authorization",
        "settings": "Settings"
      };
      breadcrumb.textContent = titles[route.name] || "Console";
    }

    // Route dispatch
    if (route.name === "console") {
      this.stream.disconnect();
      viewport.innerHTML = renderConsolePage(store.incidents);
      bindConsoleEvents(viewport);
    } else if (route.name === "incidents") {
      this.stream.disconnect();
      viewport.innerHTML = renderIncidentsPage(store.incidents, this.currentFilter, this.searchQuery);
      this.bindIncidentsEvents(viewport);
    } else if (route.name === "incident-detail") {
      await this.loadAndRenderIncidentDetail(params.id, viewport);
    } else if (route.name === "calls") {
      this.stream.disconnect();
      viewport.innerHTML = renderCallsPage(store.incidents);
    } else if (route.name === "call-detail") {
      const inc = store.incidents.find(i => i.incident_id === params.id) || await api.getIncident(params.id);
      this.stream.connect(params.id);
      viewport.innerHTML = renderCallDetailPage(inc);
      bindCallDetailEvents(viewport);
    } else if (route.name === "recoveries") {
      this.stream.disconnect();
      viewport.innerHTML = renderRecoveriesPage(store.incidents);
    } else if (route.name === "plans") {
      this.stream.disconnect();
      viewport.innerHTML = renderPlansPage(store.incidents);
    } else if (route.name === "evidence") {
      this.stream.disconnect();
      viewport.innerHTML = renderEvidencePage(store.incidents);
    } else if (route.name === "audit") {
      this.stream.disconnect();
      viewport.innerHTML = renderAuditPage(store.auditLog, this.auditFilter);
      this.bindAuditEvents(viewport);
    } else if (route.name === "security-settings" || route.name === "settings") {
      this.stream.disconnect();
      viewport.innerHTML = renderSettingsPage(store.health);
    }

    this.bindDynamicTriggers(viewport);
  }

  async loadAndRenderIncidentDetail(incidentId, viewport) {
    let incident = store.incidents.find(i => i.incident_id === incidentId);
    if (!incident) {
      incident = await api.getIncident(incidentId);
    }
    this.currentIncident = incident;

    const auditEvents = await api.getAuditTrail(incidentId).catch(() => []);
    viewport.innerHTML = renderIncidentDetailPage(incident, auditEvents);

    // Connect SSE stream for live updates
    this.stream.connect(incidentId);

    bindIncidentDetailEvents(viewport, incident, (result) => {
      this.showToast("Autonomous recovery initiated via CALL-E gateway", "success");
      this.refreshData();
    });
  }

  reRenderCurrentView() {
    if (this.router && this.router.currentRoute?.name === "incident-detail" && this.currentIncident) {
      const viewport = document.getElementById("app-viewport");
      if (viewport) {
        api.getAuditTrail(this.currentIncident.incident_id).then(events => {
          viewport.innerHTML = renderIncidentDetailPage(this.currentIncident, events);
          bindIncidentDetailEvents(viewport, this.currentIncident, () => this.refreshData());
        });
      }
    }
  }

  bindIncidentsEvents(container) {
    // Filter tabs
    container.querySelectorAll("[data-filter]").forEach(btn => {
      btn.addEventListener("click", () => {
        this.currentFilter = btn.getAttribute("data-filter");
        container.innerHTML = renderIncidentsPage(store.incidents, this.currentFilter, this.searchQuery);
        this.bindIncidentsEvents(container);
      });
    });

    // Search input
    const searchInput = container.querySelector("#incidents-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.searchQuery = e.target.value;
        container.innerHTML = renderIncidentsPage(store.incidents, this.currentFilter, this.searchQuery);
        this.bindIncidentsEvents(container);
      });
    }

    const openIngestBtn = container.querySelector("#btn-open-ingest-page");
    if (openIngestBtn) {
      openIngestBtn.addEventListener("click", () => this.openIngestModal());
    }
  }

  bindAuditEvents(container) {
    container.querySelectorAll("[data-audit-filter]").forEach(btn => {
      btn.addEventListener("click", () => {
        this.auditFilter = btn.getAttribute("data-audit-filter");
        container.innerHTML = renderAuditPage(store.auditLog, this.auditFilter);
        this.bindAuditEvents(container);
      });
    });
  }

  bindDynamicTriggers(container) {
    const refreshBtn = container.querySelector("#btn-refresh-console");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", async () => {
        await this.refreshData();
        container.innerHTML = renderConsolePage(store.incidents);
        bindConsoleEvents(container);
        this.showToast("Console state refreshed", "success");
      });
    }

    const ingestTopBtn = container.querySelector("#btn-open-ingest-top");
    if (ingestTopBtn) {
      ingestTopBtn.addEventListener("click", () => this.openIngestModal());
    }
  }

  setupSidebar() {
    const menuBtn = document.getElementById("btn-mobile-menu");
    const sidebar = document.getElementById("app-sidebar");
    if (menuBtn && sidebar) {
      menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("open");
      });
    }

    const openIngestNav = document.getElementById("btn-nav-ingest");
    if (openIngestNav) {
      openIngestNav.addEventListener("click", () => this.openIngestModal());
    }
  }

  setupModal() {
    const modal = document.getElementById("modal-ingest");
    const closeBtn = document.getElementById("btn-modal-close");
    const cancelBtn = document.getElementById("btn-modal-cancel");
    const submitBtn = document.getElementById("btn-modal-submit");
    const jsonInput = document.getElementById("input-incident-json");

    const closeModal = () => {
      if (modal) modal.style.display = "none";
    };

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

    if (submitBtn && jsonInput) {
      submitBtn.addEventListener("click", async () => {
        try {
          const payload = JSON.parse(jsonInput.value);
          submitBtn.disabled = true;
          submitBtn.textContent = "Registering...";

          const res = await api.ingestIncident(payload);
          closeModal();
          this.showToast(`Incident ${res.incident.incident_id} registered`, "success");
          await this.refreshData();
          this.router.navigate(`/incidents/${encodeURIComponent(res.incident.incident_id)}`);
        } catch (err) {
          alert(`Payload Ingestion Error: ${err.message}`);
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = "Ingest & Register Incident";
        }
      });
    }
  }

  openIngestModal() {
    const modal = document.getElementById("modal-ingest");
    const jsonInput = document.getElementById("input-incident-json");
    if (modal && jsonInput) {
      if (!jsonInput.value.trim()) {
        jsonInput.value = JSON.stringify(DEFAULT_INGEST_PAYLOAD, null, 2);
      }
      modal.style.display = "flex";
    }
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="status-dot ${type === 'success' ? '' : 'amber'}"></span>
      <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new Application();
  app.init();
});
