# ResolveCall — Autonomous Operational Incident Recovery Agent

> **Built for the CALL-E: Your Code Is Calling Hackathon ($10,000 Prize Pool)**  
> **Autonomous Telephony Category**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Telephony](https://img.shields.io/badge/Telephony-CALL--E%20MCP-green.svg)](https://github.com/CALLE-AI/call-e-integrations)
[![Architecture](https://img.shields.io/badge/Design-Zero--Mock%20Real--Time-purple.svg)](#real-time-end-to-end-architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Executive Summary

Enterprise logistics, healthcare supply chains, and freight networks can detect operational failures through APIs and webhooks in milliseconds. However, **thousands of real-world carriers, terminal docks, warehouse facilities, and dispatchers offer zero APIs for emergency exception resolution**. Their only interface is a telephone number.

When a $60,000 temperature-sensitive medication shipment is marked `UNDELIVERABLE — Gate Code Missing` at 8:45 AM with an 11:30 AM spoilage deadline, legacy systems can only file a ticket while human coordinators spend 30 minutes on phone hold.

**ResolveCall is an autonomous operational recovery agent that bridges digital enterprise systems to physical operations via real-time CALL-E telephony.**

When a critical operational incident occurs:
1. **Dynamic Incident Ingestion**: Accepts arbitrary operational incident payloads via REST API or CLI.
2. **Recovery Planning**: Formulates concrete talking points, authorization tokens (gate codes, dock PINs), and strict deadline constraints.
3. **PSTN Telephony via CALL-E**: CALL-E dials the carrier dispatcher over real telephone lines.
4. **Autonomous Negotiation**: The agent converses with IVRs or human dispatchers, rejects proposals that violate operational deadlines, and secures redelivery commitments.
5. **Real-Time Structured Extraction**: Extracts confirmed time windows, dispatcher names, and authorization codes directly from the conversation.
6. **Deterministic Policy Validation**: Mathematically evaluates the proposed window against operational cutoff deadlines.
7. **Automated Enterprise Update & Audit**: Transitions incident status from `UNDELIVERABLE` to `RECOVERED` (or `DEADLINE_MISSED`/`ESCALATED`) and records an immutable audit log.

---

## Real-Time End-to-End Architecture

ResolveCall is built strictly as a **real-time production agent** with zero hardcoded demo scripts, zero synthetic simulated calls, and zero pre-scripted conversational replays.

```
                  ┌─────────────────────────────────┐
                  │    Operational Incident Event   │
                  │ (API Webhook / JSON Ingestion)  │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │      Recovery Planner Engine    │
                  │ - Analyzes failure & cargo      │
                  │ - Injects authorization keys    │
                  │ - Sets strict deadline cutoff   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │     CALL-E Telephony Gateway    │
                  │      (calle call plan & run)    │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │       Real PSTN Phone Call      │
                  │ - Interactive IVR navigation    │
                  │ - Live dispatcher negotiation   │
                  │ - Deadline enforcement          │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │   Structured Evidence Extractor │
                  │ - Agreed window (Start - End)   │
                  │ - Representative name           │
                  │ - Authorization / Ticket code   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │   Deterministic Policy Engine   │
                  │    (proposed_time <= deadline)  │
                  └────────────────┬────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌──────────────────┐                               ┌──────────────────┐
│    RECOVERED     │                               │ DEADLINE_MISSED  │
│  (Window Valid)  │                               │   or ESCALATED   │
└────────┬─────────┘                               └────────┬─────────┘
         │                                                   │
         └─────────────────────────┬─────────────────────────┘
                                   ▼
                  ┌─────────────────────────────────┐
                  │ Live SSE Dashboard & Audit Log  │
                  └─────────────────────────────────┘
```

---

## Project Structure

```
├── resolvecall/
│   ├── core/
│   │   ├── models.py           # Domain models: Incident, Evidence, Policy, Audit
│   │   └── config.py           # Telephony security whitelist & settings
│   ├── engine/
│   │   ├── planner.py          # Dynamic recovery prompt generator
│   │   ├── policy_engine.py    # Generic mathematical time-window evaluator
│   │   └── orchestrator.py     # End-to-end lifecycle & SSE event broadcaster
│   ├── telephony/
│   │   └── calle_client.py     # Production wrapper around CALL-E CLI & MCP
│   ├── extraction/
│   │   └── extractor.py        # Dialogue turn & confirmation evidence parser
│   └── web/
│       ├── app.py              # FastAPI REST endpoints & SSE streaming
│       └── static/
│           ├── index.html      # Mission Control operations dashboard
│           ├── style.css       # Obsidian dark-mode styling & waveform animations
│           └── app.js          # Real-time state tracker & EventSource listener
├── incidents/
│   ├── medical_coldchain_gate_code.json  # Flagship $60K pharma incident
│   └── air_cargo_dock_refusal.json       # AOG aircraft component incident
├── tests/
│   ├── test_policy_engine.py   # Policy engine boundary & validation tests
│   ├── test_planner.py         # Recovery prompt generation tests
│   └── test_extractor.py       # Dialogue turn parsing tests
├── cli.py                      # Standalone command-line autonomous agent
├── run_server.py               # Mission Control web server runner
└── requirements.txt            # Dependencies
```

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** with `npm`
- **CALL-E CLI** installed and authenticated:
  ```bash
  npm install -g @call-e/cli
  npx -y skills add https://github.com/CALLE-AI/call-e-integrations --skill calle -g
  calle auth login
  calle auth status
  ```

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Arvindkumar006/jarvis-sentinel.git
cd "jarvis sentinel"
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key settings in `.env`:
```env
# Telephony Whitelist Policy (enforces callable destinations)
AUTHORIZED_PHONE_WHITELIST=+18005550199,+15551234567

# CALL-E CLI Path
CALLE_CLI_PATH=calle

# Web Server Port
PORT=8000
```

---

## Running ResolveCall

### 1. Launch Mission Control Dashboard
Start the real-time web operations center:
```bash
python run_server.py
```
Open your browser to: **`http://localhost:8000`**

### 2. Standalone Autonomous CLI
You can also run autonomous incident recovery directly from the terminal:

```bash
# Test CALL-E call planning
python cli.py plan-test --phone "+18005550199" --goal "Inquire about shipment delivery status"

# Run autonomous recovery for an incident payload
python cli.py recover incidents/medical_coldchain_gate_code.json
```

---

## REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/incidents/ingest` | Ingests an arbitrary operational incident payload |
| `GET` | `/api/incidents` | Lists all active and historical incidents |
| `GET` | `/api/incidents/{id}` | Returns incident status, transcript, evidence, policy results |
| `POST` | `/api/incidents/{id}/recover` | Initiates autonomous recovery via CALL-E |
| `GET` | `/api/incidents/{id}/stream` | Server-Sent Events (SSE) live stream of real-time progress |
| `GET` | `/api/audit` | Returns immutable audit event trail |
| `GET` | `/api/health` | Health check and system status |

---

## Running Automated Tests

Run the automated test suite covering policy engine calculations, dynamic planning, and evidence extraction:

```bash
python -m pytest -v
```

---

## Hackathon Eligibility & Compliance

- **Sponsor**: Built exclusively with [CALL-E](https://call-e.devpost.com/) telephony runtime and MCP tools.
- **Real-Time Integration**: Uses `@call-e/cli` and `seleven-mcp-sg.airudder.com` authenticated broker endpoints.
- **Production-Oriented**: Generic architecture accepting arbitrary operational schemas with strict zero-mock policy compliance.
