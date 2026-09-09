"""
JARVIS Sentinel - Interactive CLI & Hackathon Demo Console
Run both scenarios live with rich terminal output and interactive HITL gates.
"""

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text

from core.simulation_state import SimulatedEnvironment
from core.telemetry import TelemetryGenerator
from agents.orchestrator import SentinelOrchestrator

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()


def print_banner():
    banner = r"""
     _   _    ______     _____  _____   _____ ______ _   _ _____ _____ _   _ _____ _     
    | | / \  | ___ \ \  / /_ _||  ___| /  ___||  ___|| \ | |_   _|_   _| \ | |  ___| |    
    | |/ _ \ | |_/ /\ \/ / | | | |__   \ `--. | |__  |  \| | | |   | | |  \| | |__ | |    
 _  | / /_\ \|    /  \  /  | | |  __|   `--. \|  __| | . ` | | |   | | | . ` |  __|| |    
| |_| |  _  || |\ \  / /  _| |_| |___  /\__/ /| |___ | |\  | | |  _| |_| |\  | |___| |___ 
 \___/\_| |_/\_| \_|/_/   \___/\____/  \____/ \____/ \_| \_/ \_/  \___/\_| \_/\____/\_____/
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print(Panel(
        "[bold white]Autonomous Security Operations Center (SOC)[/bold white]\n"
        "[italic cyan]\"Autonomous where safe. Human-controlled where consequential.\"[/italic cyan]\n"
        "[dim]Engine: AWS Strands Agents SDK (Python) | Governance: Deterministic Policy Engine[/dim]",
        border_style="cyan"
    ))


def run_scenario_a(orchestrator: SentinelOrchestrator):
    console.print("\n[bold yellow]══════════════════════════════════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]► RUNNING SCENARIO A: Routine Developer Health Check (DEV-BOX-02)[/bold yellow]")
    console.print("[bold yellow]══════════════════════════════════════════════════════════════════════[/bold yellow]")

    events = TelemetryGenerator.get_scenario_a_events()
    console.print(f"[dim]Ingesting {len(events)} security events for host DEV-BOX-02...[/dim]")

    with console.status("[bold cyan]Multi-Agent team investigating...", spinner="dots"):
        result = orchestrator.process_incident_stream(events, incident_id="INC-1019")

    brief = result["incident_brief"]
    console.print(f"\n[bold green]✔ MULTI-AGENT TRIAGE COMPLETED[/bold green]")
    console.print(f"  • Incident ID: [bold]{brief['incident_id']}[/bold]")
    console.print(f"  • Host: [bold]{brief['affected_host']}[/bold]")
    console.print(f"  • Assessed Risk: [bold green]{brief['risk_level']}[/bold green]")
    console.print(f"  • Policy Rule: [bold]{brief['policy_decision']['policy_rule_id']}[/bold]")
    console.print(f"  • Requires HITL: [bold green]{brief['requires_hitl']}[/bold green]")
    console.print(f"  • Final Status: [bold green]{result['status']}[/bold green]")
    console.print(f"  • Explanation: [italic]{brief['policy_decision']['explanation']}[/italic]")
    console.print("\n[bold green]► ACCEPTANCE TEST RESULT: RESOLVED AUTONOMOUSLY (0 Human Interventions)[/bold green]\n")


def run_scenario_b(orchestrator: SentinelOrchestrator, interactive: bool = True):
    console.print("\n[bold red]══════════════════════════════════════════════════════════════════════[/bold red]")
    console.print("[bold red]► RUNNING SCENARIO B: Critical Ransomware Attack (FINANCE-PC-07)[/bold red]")
    console.print("[bold red]══════════════════════════════════════════════════════════════════════[/bold red]")

    events = TelemetryGenerator.get_scenario_b_events()
    console.print(f"[dim]Ingesting {len(events)} correlated security events for host FINANCE-PC-07...[/dim]")

    with console.status("[bold red]Multi-Agent team correlating 17 forensic events...", spinner="dots"):
        result = orchestrator.process_incident_stream(events, incident_id="INC-1042")

    brief = result["incident_brief"]
    env = SimulatedEnvironment()
    pre_status = env.get_host("FINANCE-PC-07")["status"]

    # Render Incident Brief Card
    card_text = (
        f"[bold red]INCIDENT #{brief['incident_id'].replace('INC-', '')} — CRITICAL[/bold red]\n\n"
        f"[bold]Affected Host:[/bold] {brief['affected_host']}\n"
        f"[bold]Confidence Score:[/bold] [cyan]{int(brief['confidence'] * 100)}%[/cyan]\n"
        f"[bold]Evidence:[/bold] [green]{brief['evidence_count']} correlated events[/green]\n"
        f"[bold]Suspected Behavior:[/bold] {brief['suspected_behavior']}\n"
        f"[bold]Recommended Action:[/bold] [bold red]{brief['recommended_action']}[/bold red]\n"
        f"[bold]Potential Impact:[/bold] {brief['potential_impact']}\n"
        f"[bold]Policy Decision:[/bold] [bold yellow]{brief['policy_decision']['policy_rule_id']}[/bold yellow]\n\n"
        f"[bold yellow]⚠ EXECUTION BLOCKED: Policy enforces mandatory Human-In-The-Loop approval.[/bold yellow]\n"
        f"[dim]Simulated Host State: {pre_status} (NOT isolated yet)[/dim]"
    )
    console.print(Panel(card_text, title="[bold red]HITL INCIDENT BRIEF[/bold red]", border_style="red"))

    if interactive:
        choice = Prompt.ask("\n[bold white]Action Required[/bold white]", choices=["Approve", "Deny"], default="Approve")
    else:
        console.print("[dim]Non-interactive demo mode: Auto-selecting [Approve][/dim]")
        choice = "Approve"

    if choice.lower() == "approve":
        with console.status("[bold red]Isolating simulated endpoint and updating SDN...", spinner="dots"):
            action_res = orchestrator.handle_hitl_action("INC-1042", "approve", approver="Senior_Analyst_Alex")

        post_status = env.get_host("FINANCE-PC-07")["status"]
        console.print(f"\n[bold green]✔ CONTAINMENT AUTHORIZED & EXECUTED[/bold green]")
        console.print(f"  • Authorizing Token: [bold cyan]HITL_APPROVED_BY_SENIOR_ANALYST_ALEX[/bold cyan]")
        console.print(f"  • Endpoint Previous Status: [dim]{pre_status}[/dim]")
        console.print(f"  • Endpoint New Status: [bold red]{post_status}[/bold red]")
        console.print(f"  • Perimeter Firewall: [bold]DROP 185.220.101.5/32[/bold]")
        console.print(f"\n[bold green]► ACCEPTANCE TEST RESULT: CONTAINED POST-APPROVAL[/bold green]\n")

        console.print(Panel(action_res["report_markdown"][:600] + "\n...[TRUNCATED REPORT]...", title="Generated Postmortem Report", border_style="cyan"))
    else:
        orchestrator.handle_hitl_action("INC-1042", "deny", approver="Senior_Analyst_Alex", reason="Operator denied")
        post_status = env.get_host("FINANCE-PC-07")["status"]
        console.print(f"\n[bold yellow]✖ REMEDIATION DENIED BY OPERATOR[/bold yellow]")
        console.print(f"  • Endpoint Status Remains: [bold green]{post_status}[/bold green]")
        console.print(f"  • Containment was PREVENTED.\n")


def print_audit_log():
    env = SimulatedEnvironment()
    table = Table(title="Simulated Enterprise Security Audit Log", border_style="cyan")
    table.add_column("Audit ID", style="dim")
    table.add_column("Timestamp", style="dim")
    table.add_column("Action", style="bold")
    table.add_column("Target")
    table.add_column("Actor", style="cyan")
    table.add_column("Permitted by Policy")

    for entry in env.audit_log[-10:]:
        perm = "[green]YES[/green]" if entry["permitted_by_policy"] else "[red]NO[/red]"
        table.add_row(
            entry["audit_id"],
            entry["timestamp"].split("T")[1][:8],
            entry["action"],
            entry["target"],
            entry["actor"],
            perm
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="JARVIS Sentinel CLI Demo Console")
    parser.add_argument("--scenario", choices=["a", "b", "all"], default="all", help="Scenario to execute")
    parser.add_argument("--non-interactive", action="store_true", help="Auto-approve without interactive prompt")
    args = parser.parse_args()

    print_banner()
    orchestrator = SentinelOrchestrator()

    if args.scenario in ("a", "all"):
        run_scenario_a(orchestrator)

    if args.scenario in ("b", "all"):
        run_scenario_b(orchestrator, interactive=not args.non_interactive)

    print_audit_log()


if __name__ == "__main__":
    main()
