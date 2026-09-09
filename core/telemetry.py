"""
JARVIS Sentinel - Telemetry Engine
Supplies realistic SIEM/EDR/Sysmon event streams for autonomous evaluation.
"""

from typing import List
from core.models import SecurityEvent


class TelemetryGenerator:
    """Provides high-fidelity incident telemetry datasets."""

    @staticmethod
    def get_scenario_a_events() -> List[SecurityEvent]:
        """
        Scenario A: Routine Benign Developer Diagnostic (DEV-BOX-02).
        3 events representing routine dev health check.
        Expected outcome: Autonomous resolution per policy POL-001.
        """
        return [
            SecurityEvent(
                event_id="EVT-DEV-001",
                host_id="DEV-BOX-02",
                user="alex.dev",
                event_type="PROCESS_CREATE",
                process_name="python3",
                process_id=101,
                parent_process="bash",
                command_line="python3 /home/alex/scripts/health_check.py --loop --interval 5",
                file_path="/home/alex/scripts/health_check.py",
                sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                details={"reason": "periodic_cron", "service": "api_health"}
            ),
            SecurityEvent(
                event_id="EVT-DEV-002",
                host_id="DEV-BOX-02",
                user="alex.dev",
                event_type="NETWORK_CONNECT",
                process_name="python3",
                process_id=101,
                dest_ip="127.0.0.1",
                dest_port=8080,
                details={"protocol": "TCP", "status": "SYN_SENT"}
            ),
            SecurityEvent(
                event_id="EVT-DEV-003",
                host_id="DEV-BOX-02",
                user="alex.dev",
                event_type="SYSTEM_METRIC",
                process_name="python3",
                process_id=101,
                details={"metric": "cpu_utilization", "value": 91.4, "threshold": 90.0, "duration_seconds": 4}
            )
        ]

    @staticmethod
    def get_scenario_b_events() -> List[SecurityEvent]:
        """
        Scenario B: Critical Ransomware Incident (FINANCE-PC-07).
        Exactly 17 correlated forensic events detailing infection lifecycle:
        Macro execution -> Shadow copy deletion -> File encryption -> C2 beaconing.
        Expected outcome: Mandatory HITL halt, Incident Brief #1042, Endpoint Isolation on approval.
        """
        return [
            SecurityEvent(
                event_id="EVT-FIN-001",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="FILE_CREATE",
                process_name="outlook.exe",
                file_path=r"C:\Users\claire\Downloads\Q4_Invoice_Review.xlsm",
                details={"source": "external_email", "sender": "billing-urgent@vendor-invoices-corp.com"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-002",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="excel.exe",
                process_id=4080,
                parent_process="explorer.exe",
                command_line=r'"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE" "Q4_Invoice_Review.xlsm"',
                file_path=r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                details={"macro_executed": True, "vba_project": "Module1.AutoOpen"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-003",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="cmd.exe",
                process_id=4200,
                parent_process="excel.exe",
                command_line=r'cmd.exe /c "powershell.exe -ExecutionPolicy Bypass -NoProfile -EncodedCommand JABzAHIAYwAgAD0A..."',
                details={"mitre_technique": "T1059.001"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-004",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="powershell.exe",
                process_id=4412,
                parent_process="cmd.exe",
                command_line=r"powershell.exe -ExecutionPolicy Bypass -NoProfile -EncodedCommand JABzAHIAYwAgAD0A...",
                details={"amsi_bypass_detected": True, "obfuscation": "Base64"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-005",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="REGISTRY_SET",
                process_name="powershell.exe",
                process_id=4412,
                details={
                    "key": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                    "value_name": "WindowsSecurityUpdate",
                    "value_data": r"C:\Users\claire\AppData\Roaming\svchost_updater.exe"
                }
            ),
            SecurityEvent(
                event_id="EVT-FIN-006",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="vssadmin.exe",
                process_id=4890,
                parent_process="powershell.exe",
                command_line="vssadmin.exe delete shadows /all /quiet",
                details={"mitre_technique": "T1490", "tactic": "Impact", "description": "Inhibit System Recovery"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-007",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="wbadmin.exe",
                process_id=4894,
                parent_process="powershell.exe",
                command_line="wbadmin.exe delete catalog -quiet",
                details={"mitre_technique": "T1490", "description": "Delete backup catalog"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-008",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="bcdedit.exe",
                process_id=4898,
                parent_process="powershell.exe",
                command_line="bcdedit.exe /set {default} bootstatuspolicy ignoreallfailures",
                details={"mitre_technique": "T1490"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-009",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="bcdedit.exe",
                process_id=4902,
                parent_process="powershell.exe",
                command_line="bcdedit.exe /set {default} recoveryenabled no",
                details={"mitre_technique": "T1490"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-010",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="FILE_ACCESS",
                process_name="powershell.exe",
                process_id=4412,
                file_path=r"C:\Users\claire\Documents\canary_trap_01.docx",
                details={"canary_indicator": True, "alert_level": "TRIPPED"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-011",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="FILE_MODIFY",
                process_name="powershell.exe",
                process_id=4412,
                file_path=r"C:\Shares\Finance\Ledger_2026.xlsx.locked",
                details={"original_path": r"C:\Shares\Finance\Ledger_2026.xlsx", "action": "ENCRYPT_AND_RENAME"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-012",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="FILE_MODIFY",
                process_name="powershell.exe",
                process_id=4412,
                file_path=r"C:\Shares\Finance\Payroll_Aug.pdf.locked",
                details={"original_path": r"C:\Shares\Finance\Payroll_Aug.pdf", "action": "ENCRYPT_AND_RENAME"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-013",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="FILE_CREATE",
                process_name="powershell.exe",
                process_id=4412,
                file_path=r"C:\Shares\Finance\HOW_TO_DECRYPT_README.txt",
                details={"content_snippet": "All your financial files have been encrypted using AES-256..."}
            ),
            SecurityEvent(
                event_id="EVT-FIN-014",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="NETWORK_CONNECT",
                process_name="powershell.exe",
                process_id=4412,
                dest_ip="185.220.101.5",
                dest_port=443,
                details={"threat_intel_match": "LockBit 3.0 C2 Gateway", "protocol": "TLSv1.3"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-015",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="DNS_QUERY",
                process_name="powershell.exe",
                process_id=4412,
                details={"query": "c2-sync-gateway.onion.to", "response_ip": "185.220.101.5"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-016",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="PROCESS_CREATE",
                process_name="sc.exe",
                process_id=5104,
                parent_process="powershell.exe",
                command_line="sc.exe stop WinDefend",
                details={"mitre_technique": "T1562.001", "description": "Disable Security Tools"}
            ),
            SecurityEvent(
                event_id="EVT-FIN-017",
                host_id="FINANCE-PC-07",
                user="claire.finance",
                event_type="HEURISTIC_ALERT",
                process_name="powershell.exe",
                process_id=4412,
                details={
                    "heuristic_rule": "RANSOMWARE_MASS_ENTROPY",
                    "file_count": 42,
                    "entropy_score": 7.94,
                    "confidence": 0.94
                }
            )
        ]
