#!/usr/bin/env python3
"""ResolveCall CLI: Autonomous Operational Incident Recovery Telephony Agent"""

import argparse
import asyncio
import json
import logging
import sys
from resolvecall.core.config import settings
from resolvecall.engine.orchestrator import RecoveryOrchestrator
from resolvecall.telephony.calle_client import CalleClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("resolvecall.cli")


async def cmd_recover(incident_path: str):
    with open(incident_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    print("\n" + "=" * 60)
    print("RESOLVECALL: AUTONOMOUS OPERATIONAL INCIDENT RECOVERY")
    print("=" * 60)
    print(f"Loading incident payload from: {incident_path}")

    orchestrator = RecoveryOrchestrator()
    incident = orchestrator.ingest_incident(payload)
    print(f"[OK] Ingested Incident: {incident.incident_id}")
    print(f"     Vendor: {incident.vendor} | Phone: {incident.phone_number}")
    print(f"     Failure: {incident.failure_code}")
    print(f"     Deadline Cutoff: {incident.recovery_deadline}")
    print(f"     Cargo: {incident.cargo_information or 'N/A'}")
    print("-" * 60)
    print("Initiating autonomous CALL-E recovery pipeline...")

    res = await orchestrator.execute_recovery(incident.incident_id)

    print("\n" + "=" * 60)
    print("RECOVERY EXECUTION OUTCOME")
    print("=" * 60)
    print(f"Final Status: {res.status}")
    print(f"Summary:      {res.recovery_summary}")
    if res.extracted_evidence:
        print(f"Evidence:     Window: {res.extracted_evidence.get('agreed_window_start')} - {res.extracted_evidence.get('agreed_window_end')}")
        print(f"              Representative: {res.extracted_evidence.get('representative_name')}")
        print(f"              Auth Code:      {res.extracted_evidence.get('authorization_code')}")
    if res.policy_evaluation:
        print(f"Policy Check: {res.policy_evaluation.get('decision')} - {res.policy_evaluation.get('reason')}")
    print("=" * 60)


def cmd_plan_test(phone: str, goal: str):
    print(f"Testing CALL-E plan for destination: {phone}")
    client = CalleClient()
    res = client.plan_call(to_phone=phone, goal=goal)
    print("[OK] CALL-E Plan generated successfully:")
    print(json.dumps(res, indent=2))


def main():
    parser = argparse.ArgumentParser(description="ResolveCall Autonomous Telephony Agent")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Recover subcommand
    recover_p = subparsers.add_parser("recover", help="Ingest and recover an operational incident")
    recover_p.add_argument("incident_file", help="Path to incident JSON file")

    # Plan test subcommand
    plan_p = subparsers.add_parser("plan-test", help="Test CALL-E telephony call planning")
    plan_p.add_argument("--phone", required=True, help="Target phone number")
    plan_p.add_argument("--goal", required=True, help="Call goal text")

    args = parser.parse_args()

    if args.subcommand == "recover":
        asyncio.run(cmd_recover(args.incident_file))
    elif args.subcommand == "plan-test":
        cmd_plan_test(args.phone, args.goal)


if __name__ == "__main__":
    main()
