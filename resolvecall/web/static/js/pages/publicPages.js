/**
 * Public Supporting & Auth Pages:
 * How It Works, Architecture, Security, Login, Signup, and Onboarding.
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
          <p class="step-card-desc">LLMs are never trusted to make business or contractual decisions. ResolveCall's mathematical engine evaluates the exact temporal delta: Δ = Timestamp(Deadline) - Timestamp(Proposed_End). If Δ ≥ 0, the incident is proven valid. If Δ < 0, it is marked DEADLINE_MISSED.</p>
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
          <p style="color:var(--text-secondary); font-size:0.85rem;">Executes deterministic temporal arithmetic: Δ = T_cutoff - T_proposed. If Δ ≥ 0, marks RECOVERED. If Δ < 0, marks DEADLINE_MISSED. If call unconfirmed, flags for supervisor ESCALATION.</p>
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
          <h3 class="step-card-title">Authentication vs. Authorization</h3>
          <p class="step-card-desc">Authentication verifies operator identity ('Who are you?'). Authorization determines telephony capability ('Which phone destinations is ResolveCall permitted to dial?').</p>
        </div>
        <div class="step-card">
      </div>
    </div>
  `;
}

export function renderLoginPage(providers = {}, errorMsg = null) {
  const errorMap = {
    OAUTH_STATE_INVALID: "Security validation failed: OAuth state mismatch or replay attempt. Please try again.",
    OAUTH_CONFIGURATION_MISSING: "OAuth provider credentials are not configured in .env.",
    OAUTH_PROVIDER_ERROR: "Third-party identity provider returned an authentication error.",
    OAUTH_INVALID_CALLBACK: "Invalid OAuth callback response from provider.",
    OAUTH_UNVERIFIED_EMAIL: "The email address associated with your OAuth provider is unverified.",
    USER_INACTIVE: "This account has been deactivated. Please contact an administrator.",
    INVALID_CREDENTIALS: "Invalid email or password. Please verify your credentials."
  };

  const displayError = errorMsg ? (errorMap[errorMsg] || errorMsg) : null;

  const isGoogleConfigured = Boolean(providers && providers.google);
  const isGithubConfigured = Boolean(providers && providers.github);
  const isLinkedinConfigured = Boolean(providers && providers.linkedin);

  return `
    <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; padding:1.5rem; background:var(--bg-app);">
      <div style="width:100%; max-width:440px; background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:2.25rem 2rem; box-shadow:var(--shadow-lg);">
        <div style="text-align:center; margin-bottom:1.5rem;">
          <a href="/" data-route="/" class="brand-mark" style="margin:0 auto 0.75rem auto; text-decoration:none;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </a>
          <h2 style="font-size:1.35rem; font-weight:800; color:#fff; letter-spacing:-0.01em;">Sign in to Recovery Operations</h2>
          <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.35rem;">Authenticate to access autonomous telephony console</p>
        </div>

        <div id="login-error-container">
          ${displayError ? `
            <div style="background:rgba(239, 68, 68, 0.12); border:1px solid var(--color-rose); border-radius:var(--radius-md); padding:0.65rem 0.85rem; margin-bottom:1rem; font-size:0.8rem; color:var(--color-rose); display:flex; align-items:center; gap:0.5rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              <span>${escapeHtml(displayError)}</span>
            </div>
          ` : ''}
        </div>

        <!-- OAuth Social Sign In Providers -->
        <div class="oauth-providers-grid">
          <!-- Google -->
          <button type="button" class="btn-oauth google" data-oauth="google" data-configured="${isGoogleConfigured}">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
            </svg>
            <span>Continue with Google</span>
            ${!isGoogleConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>

          <!-- GitHub -->
          <button type="button" class="btn-oauth github" data-oauth="github" data-configured="${isGithubConfigured}">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
            <span>Continue with GitHub</span>
            ${!isGithubConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>

          <!-- LinkedIn -->
          <button type="button" class="btn-oauth linkedin" data-oauth="linkedin" data-configured="${isLinkedinConfigured}">
            <svg viewBox="0 0 24 24" fill="#0A66C2">
              <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.27a1.62 1.62 0 1 0 0 3.24 1.62 1.62 0 0 0 0-3.24z"/>
            </svg>
            <span>Continue with LinkedIn</span>
            ${!isLinkedinConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>
        </div>

        <div class="auth-divider">
          <span>Or continue with work email</span>
        </div>

        <form id="form-login">
          <div class="form-group" style="margin-bottom:1rem;">
            <label class="form-label" for="login-email">Work Email</label>
            <input class="form-input" type="email" id="login-email" placeholder="operations@enterprise.corp" required autocomplete="username" />
          </div>
          <div class="form-group" style="margin-bottom:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label class="form-label" for="login-password">Password</label>
            </div>
            <input class="form-input" type="password" id="login-password" placeholder="Enter password" required autocomplete="current-password" />
          </div>
          <button type="submit" id="btn-login-submit" class="btn btn-primary" style="width:100%; padding:0.65rem;">Sign In</button>
        </form>

        <div style="margin-top:1.25rem; text-align:center; font-size:0.8rem; color:var(--text-muted);">
          Don't have an enterprise workspace? <a href="/signup" data-route="/signup" style="color:var(--color-cyan); font-weight:600;">Sign up</a>
        </div>
      </div>
    </div>
  `;
}

export function bindLoginEvents(container, api, onLoginSuccess) {
  const form = container.querySelector("#form-login");
  const errBox = container.querySelector("#login-error-container");
  const submitBtn = container.querySelector("#btn-login-submit");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = container.querySelector("#login-email")?.value?.trim();
      const password = container.querySelector("#login-password")?.value;

      if (!email || !password) return;

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Authenticating...";
      }

      try {
        const res = await api.auth.login(email, password);
        if (res && res.user) {
          if (onLoginSuccess) onLoginSuccess(res.user);
        }
      } catch (err) {
        if (errBox) {
          errBox.innerHTML = `
            <div style="background:rgba(239, 68, 68, 0.12); border:1px solid var(--color-rose); border-radius:var(--radius-md); padding:0.65rem 0.85rem; margin-bottom:1rem; font-size:0.8rem; color:var(--color-rose); display:flex; align-items:center; gap:0.5rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              <span>${escapeHtml(err.message || "Invalid credentials")}</span>
            </div>
          `;
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Sign In";
        }
      }
    });
  }

  // OAuth button clicks
  container.querySelectorAll("[data-oauth]").forEach(btn => {
    btn.addEventListener("click", () => {
      const provider = btn.getAttribute("data-oauth");
      const isConfigured = btn.getAttribute("data-configured") === "true";

      if (isConfigured) {
        // Direct browser navigation to backend OAuth authorize endpoint
        window.location.href = `/api/auth/oauth/${encodeURIComponent(provider)}/authorize`;
      } else {
        const envKey = `${provider.toUpperCase()}_CLIENT_ID`;
        const envSecret = `${provider.toUpperCase()}_CLIENT_SECRET`;
        alert(`${provider.toUpperCase()} OAuth requires configuration in your .env file:\n\n1. Add ${envKey}=<your-client-id>\n2. Add ${envSecret}=<your-client-secret>\n\nOnce configured, restart the server to authenticate directly via ${provider}.`);
      }
    });
  });
}

export function renderSignupPage(providers = {}, errorMsg = null) {
  const isGoogleConfigured = Boolean(providers && providers.google);
  const isGithubConfigured = Boolean(providers && providers.github);
  const isLinkedinConfigured = Boolean(providers && providers.linkedin);

  return `
    <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; padding:1.5rem; background:var(--bg-app);">
      <div style="width:100%; max-width:440px; background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:2.25rem 2rem; box-shadow:var(--shadow-lg);">
        <div style="text-align:center; margin-bottom:1.5rem;">
          <a href="/" data-route="/" class="brand-mark" style="margin:0 auto 0.75rem auto; text-decoration:none;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </a>
          <h2 style="font-size:1.35rem; font-weight:800; color:#fff; letter-spacing:-0.01em;">Create Operator Account</h2>
          <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.35rem;">Deploy autonomous incident recovery credentials</p>
        </div>

        <div id="signup-error-container">
          ${errorMsg ? `
            <div style="background:rgba(239, 68, 68, 0.12); border:1px solid var(--color-rose); border-radius:var(--radius-md); padding:0.65rem 0.85rem; margin-bottom:1rem; font-size:0.8rem; color:var(--color-rose);">
              ${escapeHtml(errorMsg)}
            </div>
          ` : ''}
        </div>

        <!-- OAuth Providers for Signup -->
        <div class="oauth-providers-grid">
          <button type="button" class="btn-oauth google" data-oauth="google" data-configured="${isGoogleConfigured}">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
            </svg>
            <span>Sign up with Google</span>
            ${!isGoogleConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>
          <button type="button" class="btn-oauth github" data-oauth="github" data-configured="${isGithubConfigured}">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
            <span>Sign up with GitHub</span>
            ${!isGithubConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>
          <button type="button" class="btn-oauth linkedin" data-oauth="linkedin" data-configured="${isLinkedinConfigured}">
            <svg viewBox="0 0 24 24" fill="#0A66C2">
              <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.27a1.62 1.62 0 1 0 0 3.24 1.62 1.62 0 0 0 0-3.24z"/>
            </svg>
            <span>Sign up with LinkedIn</span>
            ${!isLinkedinConfigured ? '<span class="badge" style="font-size:0.65rem; background:rgba(255,255,255,0.08); color:var(--text-muted); margin-left:auto;">Setup in .env</span>' : ''}
          </button>
        </div>

        <div class="auth-divider">
          <span>Or register with email</span>
        </div>

        <form id="form-signup">
          <div class="form-group" style="margin-bottom:0.85rem;">
            <label class="form-label" for="signup-name">Full Name</label>
            <input class="form-input" type="text" id="signup-name" placeholder="Alex Morgan" required autocomplete="name" />
          </div>
          <div class="form-group" style="margin-bottom:0.85rem;">
            <label class="form-label" for="signup-email">Work Email</label>
            <input class="form-input" type="email" id="signup-email" placeholder="alex@logistics.corp" required autocomplete="email" />
          </div>
          <div class="form-group" style="margin-bottom:0.85rem;">
            <label class="form-label" for="signup-password">Password</label>
            <input class="form-input" type="password" id="signup-password" placeholder="At least 8 chars (letter + number)" required autocomplete="new-password" />
            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:0.25rem;">Minimum 8 characters with at least 1 letter and 1 number or symbol.</div>
          </div>
          <div class="form-group" style="margin-bottom:1.25rem;">
            <label class="form-label" for="signup-confirm-password">Confirm Password</label>
            <input class="form-input" type="password" id="signup-confirm-password" placeholder="Confirm password" required autocomplete="new-password" />
          </div>
          <button type="submit" id="btn-signup-submit" class="btn btn-primary" style="width:100%; padding:0.65rem;">Create Account</button>
        </form>

        <div style="margin-top:1.25rem; text-align:center; font-size:0.8rem; color:var(--text-muted);">
          Already have an account? <a href="/login" data-route="/login" style="color:var(--color-cyan); font-weight:600;">Sign in</a>
        </div>
      </div>
    </div>
  `;
}

export function bindSignupEvents(container, api, onSignupSuccess) {
  const form = container.querySelector("#form-signup");
  const errBox = container.querySelector("#signup-error-container");
  const submitBtn = container.querySelector("#btn-signup-submit");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = container.querySelector("#signup-name")?.value?.trim();
      const email = container.querySelector("#signup-email")?.value?.trim();
      const password = container.querySelector("#signup-password")?.value;
      const confirmPassword = container.querySelector("#signup-confirm-password")?.value;

      if (!name || !email || !password) return;

      if (password !== confirmPassword) {
        if (errBox) {
          errBox.innerHTML = `
            <div style="background:rgba(239, 68, 68, 0.12); border:1px solid var(--color-rose); border-radius:var(--radius-md); padding:0.65rem 0.85rem; margin-bottom:1rem; font-size:0.8rem; color:var(--color-rose);">
              Passwords do not match.
            </div>
          `;
        }
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Creating Account...";
      }

      try {
        const res = await api.auth.register(name, email, password);
        if (res && res.user) {
          if (onSignupSuccess) onSignupSuccess(res.user);
        }
      } catch (err) {
        if (errBox) {
          errBox.innerHTML = `
            <div style="background:rgba(239, 68, 68, 0.12); border:1px solid var(--color-rose); border-radius:var(--radius-md); padding:0.65rem 0.85rem; margin-bottom:1rem; font-size:0.8rem; color:var(--color-rose);">
              ${escapeHtml(err.message || "Registration failed")}
            </div>
          `;
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Create Account";
        }
      }
    });
  }

  container.querySelectorAll("[data-oauth]").forEach(btn => {
    btn.addEventListener("click", () => {
      const provider = btn.getAttribute("data-oauth");
      const isConfigured = btn.getAttribute("data-configured") === "true";

      if (isConfigured) {
        window.location.href = `/api/auth/oauth/${encodeURIComponent(provider)}/authorize`;
      } else {
        const envKey = `${provider.toUpperCase()}_CLIENT_ID`;
        const envSecret = `${provider.toUpperCase()}_CLIENT_SECRET`;
        alert(`${provider.toUpperCase()} OAuth requires configuration in your .env file:\n\n1. Add ${envKey}=<your-client-id>\n2. Add ${envSecret}=<your-client-secret>\n\nOnce configured, restart the server to register via ${provider}.`);
      }
    });
  });
}

export function renderOnboardingPage(currentUser) {
  const user = currentUser || {
    name: "Operations Lead",
    email: "lead@enterprisecorp.io",
    provider: "google"
  };

  return `
    <div class="public-page" style="max-width:840px;">
      <div style="text-align:center; margin-bottom:1.5rem;">
        <div class="hero-tag"><span class="status-dot"></span><span>STEP 1 OF 2: OPERATIONAL READINESS</span></div>
        <h1 class="hero-headline" style="font-size:2.2rem; margin-top:0.5rem;">Welcome to ResolveCall</h1>
        <p class="hero-subtitle" style="font-size:0.95rem;">Review your operator identity and telephony authorization policy before launching Mission Control.</p>
      </div>

      <div style="background:var(--bg-secondary); border:1px solid var(--border-default); border-radius:var(--radius-xl); padding:2rem; display:flex; flex-direction:column; gap:1.5rem;">
        <!-- STEP 1: AUTHENTICATION STATUS -->
        <div class="step-card" style="border-color:var(--color-emerald-border); background:rgba(16, 185, 129, 0.03);">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <span class="step-card-num" style="color:var(--color-emerald);">AUTHENTICATION (VERIFIED)</span>
            <span class="badge badge-recovered">Authenticated</span>
          </div>
          <h3 class="step-card-title" style="color:#fff; margin-top:0.25rem;">"Who are you?"</h3>
          <p class="step-card-desc">Your operational coordinator identity is securely confirmed via enterprise SSO.</p>
          <div style="background:var(--bg-panel); padding:0.75rem 1rem; border-radius:var(--radius-md); border:1px solid var(--border-subtle); display:flex; align-items:center; justify-content:space-between; margin-top:0.5rem;">
            <div>
              <strong style="color:#fff; font-size:0.9rem;">${escapeHtml(user.name || "Operations Lead")}</strong>
              <div class="cell-mono text-muted" style="font-size:0.75rem;">${escapeHtml(user.email || "lead@enterprise.corp")}</div>
            </div>
            <span class="badge" style="background:rgba(6, 182, 212, 0.15); color:var(--color-cyan); text-transform:uppercase;">
              ${user.provider ? `${user.provider} SSO` : 'SSO Verified'}
            </span>
          </div>
        </div>

        <!-- STEP 2: TELEPHONY AUTHORIZATION POLICY -->
        <div class="step-card" style="border-color:var(--color-cyan-border); background:rgba(6, 182, 212, 0.03);">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <span class="step-card-num">AUTHORIZATION POLICY (ENFORCED)</span>
            <span class="badge badge-calling">Backend Enforced</span>
          </div>
          <h3 class="step-card-title" style="color:var(--color-cyan); margin-top:0.25rem;">"Which phone numbers can ResolveCall dial?"</h3>
          <p class="step-card-desc">
            ResolveCall will <strong>never freely dial arbitrary numbers</strong>. All outbound PSTN recovery calls are filtered against the authorized E.164 phone whitelist policy (<code class="mono">AUTHORIZED_PHONE_WHITELIST</code>).
          </p>
          <div style="background:var(--bg-panel); padding:0.75rem 1rem; border-radius:var(--radius-md); border:1px solid var(--border-subtle); margin-top:0.5rem; font-size:0.8rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
              <span class="text-muted">Policy Engine:</span>
              <span class="cell-mono text-cyan">E.164 Strict Regex & Whitelist Match</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
              <span class="text-muted">PSTN Gateway:</span>
              <span class="cell-mono" style="color:var(--color-emerald);">CALL-E Production MCP Dual-Phase</span>
            </div>
          </div>
        </div>

        <div style="display:flex; align-items:center; justify-content:space-between; margin-top:0.5rem;">
          <a href="/security" data-route="/security" style="font-size:0.8rem; color:var(--text-muted); text-decoration:underline;">Inspect Security Policy</a>
          <button class="btn btn-primary" id="btn-complete-onboarding" style="padding:0.7rem 1.75rem; font-size:0.9rem;">
            Authorize & Launch Mission Control ➔
          </button>
        </div>
      </div>
    </div>
  `;
}

export function bindOnboardingEvents(container, onComplete) {
  const btn = container.querySelector("#btn-complete-onboarding");
  if (btn) {
    btn.addEventListener("click", () => {
      if (onComplete) onComplete();
    });
  }
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
