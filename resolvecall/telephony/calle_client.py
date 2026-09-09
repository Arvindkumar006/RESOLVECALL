import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from resolvecall.core.config import settings

logger = logging.getLogger(__name__)


class CalleError(Exception):
    """Exception raised for CALL-E telephony API/CLI failures."""
    pass


class CalleClient:
    """Production client wrapping the CALL-E CLI and MCP telephony runtime."""

    def __init__(self, cli_path: Optional[str] = None):
        base_path = cli_path or settings.CALLE_CLI_PATH
        resolved = shutil.which(base_path)
        self.cli_path = resolved or base_path
        self._is_windows = os.name == "nt"

    def plan_call(
        self,
        to_phone: str,
        goal: str,
        language: str = "en",
        region: Optional[str] = None,
        timeout_seconds: int = 120,
    ) -> Dict[str, Any]:
        """Plans a phone call with CALL-E. Returns plan_id, confirm_token, and structured planning output."""
        if not settings.is_phone_authorized(to_phone):
            raise CalleError(f"Destination phone {to_phone} is not authorized by security whitelist policy.")

        cmd = [
            self.cli_path,
            "call",
            "plan",
            "--to-phone",
            to_phone,
            "--goal",
            goal,
            "--language",
            language,
            "--json",
        ]
        if region:
            cmd.extend(["--region", region])

        logger.info(f"Executing CALL-E plan: {goal[:60]}... to {to_phone}")
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                shell=self._is_windows,
            )
        except subprocess.TimeoutExpired as e:
            raise CalleError(f"CALL-E plan_call timed out after {timeout_seconds} seconds") from e
        except Exception as e:
            raise CalleError(f"Failed to execute CALL-E CLI: {str(e)}") from e

        if res.returncode != 0:
            raise CalleError(f"CALL-E call plan failed (code {res.returncode}): {res.stderr.strip() or res.stdout.strip()}")

        try:
            raw_data = json.loads(res.stdout)
        except json.JSONDecodeError as e:
            raise CalleError(f"Invalid JSON returned by CALL-E CLI: {res.stdout}") from e

        if not raw_data.get("ok"):
            raise CalleError(f"CALL-E plan returned failure: {raw_data}")

        structured = raw_data.get("result", {}).get("structuredContent")
        if not structured and "content" in raw_data.get("result", {}):
            for c in raw_data["result"]["content"]:
                if c.get("type") == "text":
                    try:
                        structured = json.loads(c.get("text", "{}"))
                        break
                    except Exception:
                        pass

        if not structured:
            raise CalleError(f"No structured content in CALL-E plan result: {raw_data}")

        return structured

    def run_call(
        self,
        plan_id: str,
        confirm_token: str,
        timeout_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Triggers the planned phone call using the plan confirmation token."""
        cmd = [
            self.cli_path,
            "call",
            "run",
            "--plan-id",
            plan_id,
            "--confirm-token",
            confirm_token,
            "--json",
        ]
        logger.info(f"Executing CALL-E run for plan {plan_id}")
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                shell=self._is_windows,
            )
        except subprocess.TimeoutExpired as e:
            raise CalleError(f"CALL-E run_call timed out after {timeout_seconds} seconds") from e
        except Exception as e:
            raise CalleError(f"Failed to execute CALL-E run CLI: {str(e)}") from e

        if res.returncode != 0:
            raise CalleError(f"CALL-E call run failed (code {res.returncode}): {res.stderr.strip() or res.stdout.strip()}")

        try:
            raw_data = json.loads(res.stdout)
        except json.JSONDecodeError as e:
            raise CalleError(f"Invalid JSON returned by CALL-E CLI run: {res.stdout}") from e

        if not raw_data.get("ok"):
            raise CalleError(f"CALL-E run returned failure: {raw_data}")

        structured = raw_data.get("result", {}).get("structuredContent")
        if not structured and "content" in raw_data.get("result", {}):
            for c in raw_data["result"]["content"]:
                if c.get("type") == "text":
                    try:
                        structured = json.loads(c.get("text", "{}"))
                        break
                    except Exception:
                        pass

        if not structured:
            raise CalleError(f"No structured content in CALL-E run result: {raw_data}")

        return structured

    def get_call_status(
        self,
        run_id: str,
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """Fetches the real-time status, transcript, and duration of a call run."""
        cmd = [
            self.cli_path,
            "call",
            "status",
            "--run-id",
            run_id,
            "--json",
        ]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                shell=self._is_windows,
            )
        except subprocess.TimeoutExpired as e:
            raise CalleError(f"CALL-E status query timed out after {timeout_seconds} seconds") from e
        except Exception as e:
            raise CalleError(f"Failed to execute CALL-E status CLI: {str(e)}") from e

        if res.returncode != 0:
            raise CalleError(f"CALL-E call status failed: {res.stderr.strip() or res.stdout.strip()}")

        try:
            raw_data = json.loads(res.stdout)
        except json.JSONDecodeError as e:
            raise CalleError(f"Invalid JSON returned by CALL-E CLI status: {res.stdout}") from e

        structured = raw_data.get("result", {}).get("structuredContent")
        if not structured and "content" in raw_data.get("result", {}):
            for c in raw_data["result"]["content"]:
                if c.get("type") == "text":
                    try:
                        structured = json.loads(c.get("text", "{}"))
                        break
                    except Exception:
                        pass

        return structured or raw_data.get("result", {})
