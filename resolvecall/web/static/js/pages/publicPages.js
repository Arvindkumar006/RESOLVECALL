/**
 * Public Showcase Pages:
 * How It Works, Architecture, and Security & Phone Whitelist Policy.
 */

export function renderHowItWorksPage() {
  return `
    <div class="public-page">
      <header class="public-nav">
        <a href="/" data-route="/" class="brand-link">
          <div class="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div class="brand-titles"><span class="brand-name">RESOLVECALL</span><span class="brand-tag">Autonomous Recovery</span></div>
        </a>
        <nav class="public-nav-links">
          <a href="/" data-route="/" class="public-nav-link">Home</a>
          <a href="/architecture" data-route="/architecture" class="public-nav-link">Architecture</a>
          <a href="/security" data-route="/security" class="public-nav-link">Security</a>
          <a href="/console" data-route="/console" class="btn btn-primary btn-sm">Mission Control</a>
        </nav>
      </header>

      <section class="hero-section" style="padding-bottom:1rem;">
        <div class="hero-tag"><span>OPERATIONAL RECOVERY WORKFLOW</span></div>
        <h1 class="hero-headline">How ResolveCall Works</h1>
        <p class="hero-subtitle">When APIs hit a physical brick wall, ResolveCall negotiates and recovers operational breakdowns across standard telecom lines.</p>
      </section>

      <div class="steps-grid" style="grid-template-columns:1fr; gap:1.5rem;">
        <div class="step-card">
          <span class="step-card-num">STAGE 1: INCIDENT INGESTION</span>
          <h3 class="step-card-title">Digital Failure Detection</h3>
          <p class="step-card-desc">An exception occurs in freight delivery, warehousing, or field infrastructure: gate access codes missing, driver dock refused, or security credential clearance expired. The incident is ingested via standard REST JSON payload or webhook.</p>
        </div>
        <div class="step-card">
          <span class="step-card-num">STAGE 2: DYNAMIC RECOVERY PLANNING</span>
          <h3 class="step-card-title">Objective Formulation & Anti-Phishing Guardrails</h3>
          <p class="step-card-desc">ResolveCall dynamically builds a negotiation objective with hard constraints. Sensitive credentials (gate PINs, dock tokens) are translated into logistics industry clearance terminology to prevent carrier AI voice filters from misinterpreting authentic coordination as credential phishing.</p>
        </div>
        <div class="step-card">
          <span class="step-card-num">STAGE 3: CALL-E TELEPHONY GATEWAY</span>
          <h3 class="step-card-title">Authorized E.164 Outbound PSTN Dialing</h3>
          <p class="step-card-desc">ResolveCall validates the target phone against strict organizational authorization policies. Upon clearance, it executes a dual-phase CALL-E session: generating a cryptographic confirmation token, then placing a live PSTN outbound phone call to the human dispatcher.</p>
        </div>
        <div class="step-card">
          <span class="step-card-num">STAGE 4: REAL-TIME CONVERSATIONAL NEGOTIATION</span>
          <h3 class="step-card-title">Spoken Negotiation & Exception Resolution</h3>
          <p class="step-card-desc">The autonomous voice agent handles human gatekeepers, IVR menu trees, hold music, and speaks with the dispatcher to agree on an emergency redelivery time slot before the operational cutoff.</p>
        </div>
        <div class="step-card">
          <span class="step-card-num">STAGE 5: STRUCTURED EVIDENCE EXTRACTION</span>
          <h3 class="step-card-title">Tamper-Proof Commitment Ledger</h3>
          <p class="step-card-desc">During and after the phone call, ResolveCall parses conversation turns and structured outcome payloads, extracting: (1) Agreed delivery window, (2) Representative name, (3) Confirmation reference, and (4) Verbatim auditable quotes.</p>
        </div>
        <div class="step-card">
          <span class="step-card-num">STAGE 6: DETERMINISTIC MATHEMATICAL POLICY ENGINE</span>
          <h3 class="step-card-title">Zero-Hallucination Compliance Proof (Δ ≥ 0)</h3>
          <p class="step-card-desc">LLMs are never trusted to make business or contractual decisions. ResolveCall's mathematical engine evaluates the exact temporal delta: Δ = Timestamp(Deadline) - Timestamp(Proposed_End). If Δ ≥ 0, the incident is proven valid. If Δ &lt; 0, it is marked DEADLINE_MISSED.</p>
        </div>
        <div class="step-card" style="border-color:var(--color-emerald-border); background:rgba(16, 185, 129, 0.04);">
          <span class="step-card-num" style="color:var(--color-emerald);">STAGE 7: OPERATIONAL RECOVERY & AUDIT LOGGING</span>
          <h3 class="step-card-title" style="color:#fff;">Incident Recovered</h3>
          <p class="step-card-desc">The incident status is transitioned to RECOVERED, the enterprise systems are notified, and every event, token, and quote is committed to the append-only operational audit trail.</p>
        </div>
      </div>
    </div>
  `;
}

export function renderArchitecturePage() {
  return `
    <div class="public-page">
      <header class="public-nav">
        <a href="/" data-route="/" class="brand-link">
          <div class="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div class="brand-titles"><span class="brand-name">RESOLVECALL</span><span class="brand-tag">Autonomous Recovery</span></div>
        </a>
        <nav class="public-nav-links">
          <a href="/" data-route="/" class="public-nav-link">Home</a>
          <a href="/how-it-works" data-route="/how-it-works" class="public-nav-link">How It Works</a>
          <a href="/security" data-route="/security" class="public-nav-link">Security</a>
          <a href="/console" data-route="/console" class="btn btn-primary btn-sm">Mission Control</a>
        </nav>
      </header>

      <section class="hero-section" style="padding-bottom:1rem;">
        <div class="hero-tag"><span>5-TIER ENTERPRISE ARCHITECTURE</span></div>
        <h1 class="hero-headline">System Architecture</h1>
        <p class="hero-subtitle">Bridging automated software triggers to real-world telephone networks through deterministic policy enforcement.</p>
      </section>

      <div style="background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:2rem; display:flex; flex-direction:column; gap:1.5rem;">
        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          <span class="cell-mono text-muted" style="font-size:0.75rem;">TIER 1: INGESTION</span>
          <h3 style="color:#fff; font-size:1.1rem;">Operational Ingestion & Normalization</h3>
          <p style="color:var(--text-secondary); font-size:0.85rem;">FastAPI ingestion tier accepting operational payloads via REST endpoint (POST /api/incidents/ingest) or CLI. Normalizes failure codes, vendor metadata, target phone number, and recovery deadlines.</p>
        </div>
        <hr style="border-color:var(--border-subtle);"/>

        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          <span class="cell-mono text-muted" style="font-size:0.75rem;">TIER 2: INTELLIGENCE & PLANNING</span>
          <h3 style="color:#fff; font-size:1.1rem;">Dynamic Recovery Planner & Anti-Phishing Guardrails</h3>
          <p style="color:var(--text-secondary); font-size:0.85rem;">Constructs strict goal-directed negotiation objectives. Sanitizes sensitive credentials into operational logistics clearance terms.</p>
        </div>
        <hr style="border-color:var(--border-subtle);"/>

        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          <span class="cell-mono text-muted" style="font-size:0.75rem;">TIER 3: TELEPHONY GATEWAY</span>
          <h3 style="color:#fff; font-size:1.1rem;">CALL-E Dual-Phase Execution & Polling Engine</h3>
          <p style="color:var(--text-secondary); font-size:0.85rem;">Interacts with the CALL-E telephony gateway. Dual-phase commitment: (1) plan_call generates plan ID and cryptographic confirmation token, (2) run_call dials the PSTN line. Real-time turn polling streams activities via Server-Sent Events (SSE).</p>
        </div>
        <hr style="border-color:var(--border-subtle);"/>

        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          <span class="cell-mono text-muted" style="font-size:0.75rem;">TIER 4: EVIDENCE EXTRACTION</span>
          <h3 style="color:#fff; font-size:1.1rem;">Structured Evidence Extractor</h3>
          <p style="color:var(--text-secondary); font-size:0.85rem;">Parses spoken turns and telephony activity payloads to extract the committed delivery window, representative identity, and authorization reference with verbatim quote attribution.</p>
        </div>
        <hr style="border-color:var(--border-subtle);"/>

        <div style="display:flex; flex-direction:column; gap:0.45rem;">
          <span class="cell-mono text-muted" style="font-size:0.75rem;">TIER 5: DETERMINISTIC ENGINE</span>
          <h3 style="color:#fff; font-size:1.1rem;">Pure Mathematical Policy Engine</h3>
          <p style="color:var(--text-secondary); font-size:0.85rem;">Executes deterministic temporal arithmetic: Δ = T_cutoff - T_proposed. If Δ ≥ 0, marks RECOVERED. If Δ &lt; 0, marks DEADLINE_MISSED. If call unconfirmed, flags for supervisor ESCALATION.</p>
        </div>
      </div>
    </div>
  `;
}

export function renderSecurityPage() {
  return `
    <div class="public-page">
      <header class="public-nav">
        <a href="/" data-route="/" class="brand-link">
          <div class="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div class="brand-titles"><span class="brand-name">RESOLVECALL</span><span class="brand-tag">Autonomous Recovery</span></div>
        </a>
        <nav class="public-nav-links">
          <a href="/" data-route="/" class="public-nav-link">Home</a>
          <a href="/how-it-works" data-route="/how-it-works" class="public-nav-link">How It Works</a>
          <a href="/architecture" data-route="/architecture" class="public-nav-link">Architecture</a>
          <a href="/console" data-route="/console" class="btn btn-primary btn-sm">Mission Control</a>
        </nav>
      </header>

      <section class="hero-section" style="padding-bottom:1rem;">
        <div class="hero-tag"><span class="status-dot"></span><span>TELEPHONY GOVERNANCE & SAFETY</span></div>
        <h1 class="hero-headline">Security & Phone Whitelist Policy</h1>
        <p class="hero-subtitle">ResolveCall does not freely dial arbitrary telephone numbers. Every outbound call must satisfy strict cryptographic authorization checks.</p>
      </section>

      <!-- Authorization Visual Flow -->
      <div style="background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:2rem; text-align:center;">
        <h3 style="color:#fff; font-size:1.15rem; margin-bottom:1.5rem;">Outbound Telephony Authorization Chain</h3>
        <div style="display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:1rem; font-family:var(--font-mono); font-size:0.85rem;">
          <span style="background:var(--bg-panel); padding:0.5rem 1rem; border-radius:var(--radius-md); border:1px solid var(--border-default);">ResolveCall Agent</span>
          <span style="color:var(--color-cyan);">➔</span>
          <span style="background:var(--color-cyan-bg); color:var(--color-cyan); padding:0.5rem 1rem; border-radius:var(--radius-md); border:1px solid var(--color-cyan-border);">E.164 Whitelist Policy</span>
          <span style="color:var(--color-cyan);">➔</span>
          <span style="background:var(--bg-panel); padding:0.5rem 1rem; border-radius:var(--radius-md); border:1px solid var(--border-default);">Dual-Phase Token Verification</span>
          <span style="color:var(--color-cyan);">➔</span>
          <span style="background:var(--bg-panel); padding:0.5rem 1rem; border-radius:var(--radius-md); border:1px solid var(--border-default);">CALL-E Gateway</span>
          <span style="color:var(--color-cyan);">➔</span>
          <span style="background:var(--color-emerald-bg); color:var(--color-emerald); padding:0.5rem 1rem; border-radius:var(--radius-md); border:1px solid var(--color-emerald-border);">PSTN Carrier Line</span>
        </div>
      </div>

      <div class="steps-grid" style="grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:1.25rem;">
        <div class="step-card">
          <h3 class="step-card-title">E.164 Destination Whitelisting</h3>
          <p class="step-card-desc">The backend strictly rejects any outbound call attempt whose destination is not registered in the authorized whitelist policy (AUTHORIZED_PHONE_WHITELIST).</p>
        </div>
        <div class="step-card">
          <h3 class="step-card-title">Zero Secret Exposure</h3>
          <p class="step-card-desc">CALL-E API tokens, carrier credentials, and secret environment keys are isolated in backend memory and never exposed over frontend endpoints or HTML source.</p>
        </div>
      </div>
    </div>
  `;
}
