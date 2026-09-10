/**
 * ResolveCall Central State & Operational Utilities
 */

class Store {
  constructor() {
    this.incidents = [];
    this.activeIncident = null;
    this.auditLog = [];
    this.health = null;
    this.listeners = new Set();
    this.callTimerInterval = null;
    this.callElapsedSeconds = 0;
    
    // Active Operations Profile (Console Operator)
    this.currentUser = {
      name: "Operations Lead",
      email: "lead@resolvecall.io",
      role: "Autonomous Telephony Lead"
    };
  }


  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify(event, data) {
    for (const listener of this.listeners) {
      try {
        listener(event, data);
      } catch (err) {
        console.error("Store listener error:", err);
      }
    }
  }

  setIncidents(incidents) {
    this.incidents = incidents || [];
    this.notify("incidents", this.incidents);
  }

  setActiveIncident(incident) {
    this.activeIncident = incident;
    this.notify("activeIncident", this.activeIncident);
  }

  setAuditLog(logs) {
    this.auditLog = logs || [];
    this.notify("auditLog", this.auditLog);
  }

  setHealth(health) {
    this.health = health;
    this.notify("health", this.health);
  }
}

export const store = new Store();

/**
 * Mask phone numbers to preserve privacy
 * e.g. "+18005550199" -> "+1 800 •••• 0199"
 */
export function maskPhoneNumber(phone) {
  if (!phone || typeof phone !== "string") return "Not available";
  const cleaned = phone.replace(/[^\d+]/g, "");
  if (cleaned.length < 7) return cleaned;
  const start = cleaned.slice(0, Math.min(6, Math.floor(cleaned.length / 2)));
  const end = cleaned.slice(-4);
  return `${start} •••• ${end}`;
}

/**
 * Format timestamp into readable localized time
 */
export function formatTime(isoString) {
  if (!isoString) return "Not available";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (e) {
    return isoString;
  }
}

/**
 * Format ISO or HH:MM into standard display
 */
export function formatDateTime(isoString) {
  if (!isoString) return "Not available";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return isoString;
  }
}

/**
 * Web Audio DTMF Frequency Synthesizer
 * Generates genuine ITU standard DTMF dual-tone sound frequencies for dialpad presses.
 */
let audioCtx = null;
const DTMF_FREQS = {
  '1': [697, 1209], '2': [697, 1336], '3': [697, 1477],
  '4': [770, 1209], '5': [770, 1336], '6': [770, 1477],
  '7': [852, 1209], '8': [852, 1336], '9': [852, 1477],
  '*': [941, 1209], '0': [941, 1336], '#': [941, 1477]
};

export function playDtmfTone(key) {
  const freqs = DTMF_FREQS[key];
  if (!freqs) return;

  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }

    const osc1 = audioCtx.createOscillator();
    const osc2 = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc1.frequency.value = freqs[0];
    osc2.frequency.value = freqs[1];

    gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.15);

    osc1.connect(gainNode);
    osc2.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc1.start();
    osc2.start();
    osc1.stop(audioCtx.currentTime + 0.15);
    osc2.stop(audioCtx.currentTime + 0.15);
  } catch (err) {
    // Audio synthesis fallback
  }
}
