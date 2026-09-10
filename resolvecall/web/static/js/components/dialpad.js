/**
 * Dedicated Enterprise Dialpad Component (DTMF Input)
 * Renders 3x4 numeric keypad with letters, audio feedback, and accessible ARIA attributes.
 */

import { playDtmfTone } from "../store.js";

const DIALPAD_KEYS = [
  { digit: "1", letters: "" },
  { digit: "2", letters: "ABC" },
  { digit: "3", letters: "DEF" },
  { digit: "4", letters: "GHI" },
  { digit: "5", letters: "JKL" },
  { digit: "6", letters: "MNO" },
  { digit: "7", letters: "PQRS" },
  { digit: "8", letters: "TUV" },
  { digit: "9", letters: "WXYZ" },
  { digit: "*", letters: "" },
  { digit: "0", letters: "+" },
  { digit: "#", letters: "" }
];

export function renderDialpad() {
  return `
    <div class="dialpad-container" role="group" aria-label="DTMF Keypad">
      <div class="dialpad-header">DTMF INPUT</div>
      
      <div class="dialpad-display" id="dtmf-display" aria-live="polite">
        <span id="dtmf-value"></span>
      </div>

      <div class="dialpad-grid">
        ${DIALPAD_KEYS.map(k => `
          <button type="button" class="dialpad-key" data-key="${k.digit}" aria-label="Keypad ${k.digit} ${k.letters}">
            <span class="key-digit">${k.digit}</span>
            ${k.letters ? `<span class="key-letters">${k.letters}</span>` : ''}
          </button>
        `).join("")}
      </div>

      <div style="display:flex; justify-content:space-between; width:100%; margin-top:0.4rem;">
        <button type="button" class="btn btn-ghost btn-sm" id="btn-clear-dtmf" style="font-size:0.7rem;">Clear</button>
        <span class="text-muted" style="font-size:0.65rem; align-self:center;">PSTN In-Call Tones</span>
      </div>
    </div>
  `;
}

export function bindDialpadEvents(container) {
  const displayVal = container.querySelector("#dtmf-value");
  const clearBtn = container.querySelector("#btn-clear-dtmf");
  const keys = container.querySelectorAll(".dialpad-key");

  function pressKey(digit) {
    playDtmfTone(digit);
    if (displayVal) {
      if (displayVal.textContent.length < 16) {
        displayVal.textContent += digit;
      }
    }
  }

  keys.forEach(key => {
    key.addEventListener("click", () => {
      const digit = key.getAttribute("data-key");
      key.classList.add("key-pressed");
      setTimeout(() => key.classList.remove("key-pressed"), 120);
      pressKey(digit);
    });
  });

  if (clearBtn && displayVal) {
    clearBtn.addEventListener("click", () => {
      displayVal.textContent = "";
    });
  }

  // Keyboard shortcut listener
  const keyHandler = (e) => {
    // Only capture if not inside an input/textarea
    if (["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
    const allowed = "0123456789*#";
    if (allowed.includes(e.key)) {
      const matchedKey = container.querySelector(`.dialpad-key[data-key="${e.key}"]`);
      if (matchedKey) {
        matchedKey.classList.add("key-pressed");
        setTimeout(() => matchedKey.classList.remove("key-pressed"), 120);
      }
      pressKey(e.key);
    }
  };

  document.removeEventListener("keydown", container._dtmfKeyHandler);
  container._dtmfKeyHandler = keyHandler;
  document.addEventListener("keydown", keyHandler);
}
