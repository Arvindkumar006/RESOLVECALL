"""
JARVIS Sentinel - Threat Intelligence Tools
Decorated with @tool for Strands Agent invocation.
Enriches indicators of compromise (IOCs) with reputation scores and MITRE ATT&CK mappings.
"""

import json
from strands import tool
from core.simulation_state import SimulatedEnvironment


THREAT_INTEL_DB = {
    "185.220.101.5": {
        "indicator": "185.220.101.5",
        "type": "IP",
        "reputation": "MALICIOUS",
        "score": 98.5,
        "threat_actor": "LockBit Ransomware Cartel (FIN7 affiliate)",
        "mitre_techniques": ["T1071.001", "T1486", "T1490"],
        "details": "Known active command-and-control (C2) server for LockBit 3.0 ransomware staging."
    },
    "127.0.0.1": {
        "indicator": "127.0.0.1",
        "type": "IP",
        "reputation": "BENIGN",
        "score": 0.0,
        "threat_actor": None,
        "mitre_techniques": [],
        "details": "Standard local loopback address."
    }
}

MITRE_TECHNIQUES_DB = {
    "T1490": {
        "id": "T1490",
        "name": "Inhibit System Recovery",
        "tactic": "Impact",
        "severity": "CRITICAL",
        "description": "Adversaries delete or modify system recovery artifacts (like shadow copies or catalog backups) to prevent file restoration."
    },
    "T1059.001": {
        "id": "T1059.001",
        "name": "Command and Scripting Interpreter: PowerShell",
        "tactic": "Execution",
        "severity": "HIGH",
        "description": "PowerShell command execution with bypass flags used to execute obfuscated staging payloads."
    },
    "T1562.001": {
        "id": "T1562.001",
        "name": "Impair Defenses: Disable or Modify Tools",
        "tactic": "Defense Evasion",
        "severity": "HIGH",
        "description": "Adversaries attempt to disable security agents or endpoint antivirus services like Windows Defender."
    },
    "T1486": {
        "id": "T1486",
        "name": "Data Encrypted for Impact",
        "tactic": "Impact",
        "severity": "CRITICAL",
        "description": "Adversaries encrypt data on target systems to interrupt availability to system and network resources."
    }
}


@tool
def lookup_ip_reputation(ip: str) -> str:
    """
    Query global threat intelligence reputation databases for a remote IP address.

    Args:
        ip: IPv4 address to evaluate (e.g. '185.220.101.5')

    Returns:
        JSON string with reputation score, associated threat actors, and malware families.
    """
    clean_ip = ip.strip()
    match = THREAT_INTEL_DB.get(clean_ip, {
        "indicator": clean_ip,
        "type": "IP",
        "reputation": "UNKNOWN",
        "score": 10.0,
        "threat_actor": None,
        "mitre_techniques": [],
        "details": "No known malicious history in commercial threat feeds."
    })

    env = SimulatedEnvironment()
    env.add_trace(
        agent_name="ThreatIntelAgent",
        action_type="TOOL_CALL",
        message=f"Queried threat intelligence for IP {clean_ip}: {match['reputation']} (Score: {match['score']})",
        payload={"ip": clean_ip, "reputation": match["reputation"], "score": match["score"]}
    )
    return json.dumps(match, indent=2)


@tool
def lookup_hash_reputation(sha256: str) -> str:
    """
    Look up file hash in threat feeds to check for known malware signatures.

    Args:
        sha256: SHA-256 hash string

    Returns:
        JSON string indicating whether hash matches known malware or benign developer tools.
    """
    clean_hash = sha256.strip().lower()
    # Benign empty or dev hash
    if clean_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
        res = {
            "sha256": clean_hash,
            "classification": "BENIGN",
            "threat_actor": None,
            "signature_match": "Standard empty file or clean script signature"
        }
    else:
        res = {
            "sha256": clean_hash,
            "classification": "MALICIOUS",
            "threat_actor": "LockBit-Ransomware-Payload",
            "signature_match": "Trojan.Win32.LockBit.Gen"
        }

    env = SimulatedEnvironment()
    env.add_trace(
        agent_name="ThreatIntelAgent",
        action_type="TOOL_CALL",
        message=f"Checked hash reputation {clean_hash[:12]}... -> {res['classification']}",
        payload={"hash": clean_hash, "classification": res["classification"]}
    )
    return json.dumps(res, indent=2)


@tool
def mitre_attack_lookup(technique_id: str) -> str:
    """
    Map an observed MITRE ATT&CK technique code to tactical description and severity.

    Args:
        technique_id: Technique code such as 'T1490', 'T1059.001', 'T1562.001'

    Returns:
        JSON string detailing the tactic, technique name, and severity impact.
    """
    clean_id = technique_id.strip().upper()
    tech = MITRE_TECHNIQUES_DB.get(clean_id, {
        "id": clean_id,
        "name": "General Execution Technique",
        "tactic": "Execution",
        "severity": "MEDIUM",
        "description": "Unclassified security event technique."
    })

    env = SimulatedEnvironment()
    env.add_trace(
        agent_name="ThreatIntelAgent",
        action_type="TOOL_CALL",
        message=f"Mapped MITRE technique {clean_id}: {tech['name']} ({tech['severity']})",
        payload={"technique_id": clean_id, "name": tech["name"]}
    )
    return json.dumps(tech, indent=2)
