/**
 * Public SaaS Landing Page Component
 * Showcases ResolveCall's autonomous telephony value proposition:
 * "WHEN THE API CAN'T FIX IT, RESOLVECALL PICKS UP THE PHONE."
 */

export function renderLandingPage() {
  return `
    <div class="public-page">
      <!-- Public Navigation Header -->
      <header class="public-nav">
        <a href="/" data-route="/" class="brand-link">
          <div class="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
            </svg>
          </div>
          <div class="brand-titles">
            <span class="brand-name">RESOLVECALL</span>
            <span class="brand-tag">Autonomous Recovery</span>
          </div>
        </a>

        <nav class="public-nav-links">
          <a href="/how-it-works" data-route="/how-it-works" class="public-nav-link">How It Works</a>
          <a href="/architecture" data-route="/architecture" class="public-nav-link">Architecture</a>
          <a href="/security" data-route="/security" class="public-nav-link">Security & Whitelist</a>
          <a href="/login" data-route="/login" class="btn btn-secondary btn-sm">Sign In</a>
          <a href="/signup" data-route="/signup" class="btn btn-primary btn-sm">Get Started</a>
        </nav>
      </header>

      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-tag">
          <span class="status-dot"></span>
          <span>AUTONOMOUS TELEPHONY OPERATIONS PLATFORM</span>
        </div>

        <h1 class="hero-headline">
          WHEN THE API CAN'T FIX IT,<br/>
          <span class="text-gradient">RESOLVECALL PICKS UP THE PHONE.</span>
        </h1>

        <p class="hero-subtitle">
          Resolve operational breakdowns by letting an autonomous AI agent call the human dispatchers, security gates, and freight docks that software APIs cannot reach.
        </p>

        <div class="hero-cta-group">
          <a href="/signup" data-route="/signup" class="btn btn-primary" style="padding:0.75rem 1.5rem; font-size:0.95rem;">
            Get Started
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          </a>
          <a href="/how-it-works" data-route="/how-it-works" class="btn btn-secondary" style="padding:0.75rem 1.5rem; font-size:0.95rem;">
            See How It Works
          </a>
        </div>

        <!-- Centerpiece Phone Visualization (AUTONOMOUS TELEPHONY) -->
        <div class="hero-phone-showcase">
          <div class="phone-console" style="border:none; border-radius:0;">
            <div class="phone-console-header">
              <div class="phone-header-left">
                <span class="telephony-terminal-badge">AUTONOMOUS TELEPHONY</span>
                <span class="cell-mono text-muted" style="font-size:0.75rem;">VISUAL ARCHITECTURE SPECIFICATION</span>
              </div>
              <div class="phone-status-pill connected">
                <span class="status-dot"></span>
                <span>CONNECTED</span>
              </div>
            </div>

            <div class="phone-body">
              <div class="phone-avatar-wrap">
                <div class="phone-avatar connected">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                  </svg>
                </div>
              </div>

              <div>
                <h3 class="phone-contact-name">Authorized Operations Dispatch</h3>
                <p class="phone-contact-org">Regional Freight & Field Carrier</p>
              </div>

              <div class="phone-number-tag">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
                <span>+1 800 •••• 0199</span>
              </div>

              <div class="phone-timer mono">00:02:14</div>

              <div class="voice-waveform-channel">
                <div class="waveform-bars">
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                  <span class="wave-bar active"></span>
                </div>
                <span class="voice-channel-label">VOICE CHANNEL ACTIVE (PSTN)</span>
              </div>

              <div class="call-controls-row">
                <button class="ctrl-btn" title="Microphone Monitor">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
                </button>
                <button class="ctrl-btn active" title="DTMF Input">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" x2="21" y1="9" y2="9"/><line x1="3" x2="21" y1="15" y2="15"/><line x1="9" x2="9" y1="3" y2="21"/><line x1="15" x2="15" y1="3" y2="21"/></svg>
                </button>
                <button class="ctrl-btn btn-end-call" title="End Call">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L6.09 9.91"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 7-Step Product Explanation -->
      <section class="steps-section">
        <div class="section-header">
          <h2 class="section-title">The 7-Step Autonomous Telephony Lifecycle</h2>
          <p class="section-desc">From digital incident alert to verified real-world recovery in minutes</p>
        </div>

        <div class="steps-grid">
          <div class="step-card">
            <span class="step-card-num">STEP 01</span>
            <h3 class="step-card-title">Incident Ingested</h3>
            <p class="step-card-desc">ERP or logistics platform triggers an exception: blocked gate, dock refusal, or expired security credential.</p>
          </div>

          <div class="step-card">
            <span class="step-card-num">STEP 02</span>
            <h3 class="step-card-title">Recovery Planned</h3>
            <p class="step-card-desc">Planner analyzes hard business deadlines, sanitizes credentials against phishing guardrails, and sets goals.</p>
          </div>

          <div class="step-card">
            <span class="step-card-num">STEP 03</span>
            <h3 class="step-card-title">CALL-E Dials PSTN</h3>
            <p class="step-card-desc">The telephony gateway dials an authorized operational phone number across genuine public telecom networks.</p>
          </div>

          <div class="step-card">
            <span class="step-card-num">STEP 04</span>
            <h3 class="step-card-title">Agent Negotiates</h3>
            <p class="step-card-desc">Autonomous voice agent coordinates with the human dispatcher, resolves blockers, and agrees on an emergency redelivery slot.</p>
          </div>

          <div class="step-card">
            <span class="step-card-num">STEP 05</span>
            <h3 class="step-card-title">Evidence Extracted</h3>
            <p class="step-card-desc">Structured parser extracts dispatcher name, confirmed time window, authorization code, and verbatim audio quotes.</p>
          </div>

          <div class="step-card">
            <span class="step-card-num">STEP 06</span>
            <h3 class="step-card-title">Policy Verified</h3>
            <p class="step-card-desc">Zero-hallucination mathematical engine proves that the committed redelivery time strictly satisfies the operational deadline.</p>
          </div>

          <div class="step-card" style="border-color:var(--color-emerald-border); background:rgba(16, 185, 129, 0.04);">
            <span class="step-card-num" style="color:var(--color-emerald);">STEP 07</span>
            <h3 class="step-card-title" style="color:#fff;">Incident Recovered</h3>
            <p class="step-card-desc">Enterprise state is updated, audit log is written, and operations resume without human coordinator fatigue.</p>
          </div>
        </div>
      </section>

      <!-- Impact Comparison: Traditional vs ResolveCall -->
      <section class="steps-section">
        <div class="section-header">
          <h2 class="section-title">The Real-World Operational Impact</h2>
          <p class="section-desc">Why autonomous telephony solves what software APIs cannot</p>
        </div>

        <div class="comparison-grid">
          <div class="comparison-card traditional">
            <h3 class="comparison-title" style="color:var(--color-rose);">Traditional Incident Management</h3>
            <div class="comparison-flow">
              <div class="flow-step">
                <span style="color:var(--color-rose);">1.</span> Digital alert detected in ERP
              </div>
              <div class="flow-step">
                <span style="color:var(--color-rose);">2.</span> Routed to human coordinator queue (15-30m delay)
              </div>
              <div class="flow-step">
                <span style="color:var(--color-rose);">3.</span> Human dials carrier and waits on hold (30-45m)
              </div>
              <div class="flow-step">
                <span style="color:var(--color-rose);">4.</span> Manual verbal negotiation & handwritten notes
              </div>
              <div class="flow-step">
                <span style="color:var(--color-rose);">5.</span> Deadline misses; SLA penalties & product spoilage
              </div>
            </div>
          </div>

          <div class="comparison-card resolvecall">
            <h3 class="comparison-title" style="color:var(--color-cyan);">ResolveCall Autonomous Telephony</h3>
            <div class="comparison-flow">
              <div class="flow-step">
                <span style="color:var(--color-cyan);">✓</span> Ingests incident JSON via REST / webhook in 50ms
              </div>
              <div class="flow-step">
                <span style="color:var(--color-cyan);">✓</span> Formulates recovery objective and safety guardrails
              </div>
              <div class="flow-step">
                <span style="color:var(--color-cyan);">✓</span> Dials authorized contact immediately via CALL-E
              </div>
              <div class="flow-step">
                <span style="color:var(--color-cyan);">✓</span> Autonomous spoken negotiation & evidence capture
              </div>
              <div class="flow-step">
                <span style="color:var(--color-cyan);">✓</span> Mathematical policy validation (Δ ≥ 0) & instant recovery
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Public Footer -->
      <footer style="border-top:1px solid var(--border-subtle); padding:2rem 0; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
        <div style="font-size:0.8rem; color:var(--text-muted);">
          &copy; 2026 ResolveCall. Autonomous Telephony Infrastructure. Built for CALL-E Hackathon.
        </div>
        <div style="display:flex; gap:1.5rem; font-size:0.8rem; color:var(--text-secondary);">
          <a href="/security" data-route="/security">Phone Whitelist Policy</a>
          <a href="/architecture" data-route="/architecture">Architecture</a>
          <a href="/console" data-route="/console">Console</a>
        </div>
      </footer>
    </div>
  `;
}
