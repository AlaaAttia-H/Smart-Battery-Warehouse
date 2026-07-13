"""
AI planner wrapper for the Smart Battery Warehouse.

Runs Fast Downward on the PDDL domain and generated problem file,
then reads the generated plan.
"""

import subprocess
from pathlib import Path
import sys

from config.config_loader import get_plan_output_path, get_planner_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOMAIN_PATH = PROJECT_ROOT / "planner" / "domain.pddl"
PROBLEM_PATH = PROJECT_ROOT / "planner" / "generated_problem.pddl"
PLAN_OUTPUT_PATH = PROJECT_ROOT / get_plan_output_path()


def delete_old_plan():
    if PLAN_OUTPUT_PATH.exists():
        PLAN_OUTPUT_PATH.unlink()


def parse_plan(plan_path=PLAN_OUTPUT_PATH):
    plan_path = Path(plan_path)

    if not plan_path.exists():
        print("[PLANNER] No plan file found.")
        return []

    plan = []

    with open(plan_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith(";"):
                continue

            if line.startswith("(") and line.endswith(")"):
                action = line[1:-1]
                plan.append(action)

    return plan


def run_planner():
    delete_old_plan()

    planner_path = get_planner_path()

    command = [
        sys.executable,
        planner_path,
        "--alias",
        "lama-first",
        "--plan-file",
        str(PLAN_OUTPUT_PATH),
        str(DOMAIN_PATH),
        str(PROBLEM_PATH),
    ]

    print("[PLANNER] Running planner...")
    print("[PLANNER COMMAND]", " ".join(command))

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("[PLANNER ERROR] Planner did not finish successfully.")
            print(result.stderr)
            return []

        plan = parse_plan()

        print("[PLANNER] Plan found:")
        for step in plan:
            print(f"  - {step}")

        return plan

    except FileNotFoundError:
        print("[PLANNER ERROR] Fast Downward was not found.")
        print("Check fast_downward_path in config/config.json.")
        return []
    except OSError as e:
        print("[PLANNER ERROR] Could not run Fast Downward.")
        print(e)
        return []


if __name__ == "__main__":
    plan = run_planner()
    print(plan)