"""
Minimal agent with tool access. No guardrails.
Intentional vulnerability code for combined multimodal AI safety testing.
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_agent(goal: str) -> str:
    """
    Accepts arbitrary goals. Has access to file system and subprocess.
    No guardrails. No scope limitation.
    """
    logger.info(f"Executing agent with goal: {goal}")

    # No validation of goal - could be arbitrary commands
    if goal.startswith("exec:"):
        try:
            result = subprocess.run(
                goal[5:].strip(),
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return f"stdout: {result.stdout}\nstderr: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"

    if goal.startswith("file:"):
        path = goal[5:].strip()
        try:
            content = Path(path).read_text()
            return content
        except Exception as e:
            return f"Error: {e}"

    if goal.startswith("write:"):
        parts = goal[6:].strip().split("|", 1)
        path = parts[0].strip()
        content = parts[1] if len(parts) > 1 else ""
        try:
            Path(path).write_text(content)
            return f"Wrote to {path}"
        except Exception as e:
            return f"Error: {e}"

    # Default: echo the goal
    return f"Processed goal: {goal}"
