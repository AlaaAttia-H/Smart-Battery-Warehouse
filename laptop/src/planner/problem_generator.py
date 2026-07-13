"""
PDDL problem generator for the Smart Battery Warehouse.

Creates a problem.pddl file from the current symbolic context.
"""

from pathlib import Path

from knowledge_base import warehouse_kb as kb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_PROBLEM_PATH = PROJECT_ROOT / "planner" / "generated_problem.pddl"


def make_fact(predicate, *objects):
    return f"({predicate} {' '.join(objects)})"


def generate_problem(context, output_path=GENERATED_PROBLEM_PATH):
    battery_zone = kb.get_zone_pddl_name("battery_zone")
    manager_zone = kb.get_zone_pddl_name("manager_zone")
    manager_dashboard = kb.get_dashboard_pddl_name("manager_dashboard")

    risk_level = context.get("risk_level", "LOW").upper()
    battery_condition = context.get("battery_condition", "NORMAL").upper()
    occupancy = int(context.get("occupancy", 0))

    init_facts = [
    make_fact("light-off", manager_zone),
    make_fact("needs-dashboard-update", manager_dashboard),
    ]

    goal_facts = [
        make_fact("dashboard-updated", manager_dashboard),
    ]

    if risk_level == "HIGH":
        init_facts.extend([
            make_fact("needs-ventilation", battery_zone),
            make_fact("needs-alarm", battery_zone),
            make_fact("needs-red-light", manager_zone),
            make_fact("needs-shutter-closed", manager_zone),
            make_fact("needs-manager-notification", manager_zone),
        ])

        goal_facts.extend([
            make_fact("fan-on", battery_zone),
            make_fact("alarm-on", battery_zone),
            make_fact("red-light-on", manager_zone),
            make_fact("shutter-closed", manager_zone),
            make_fact("manager-notified", manager_zone),
        ])

        if occupancy > 0:
            init_facts.append(make_fact("needs-evacuation", manager_zone))
            goal_facts.append(make_fact("evacuation-requested", manager_zone))

    elif risk_level == "MEDIUM":
        init_facts.extend([
            make_fact("needs-ventilation", battery_zone),
            make_fact("needs-orange-light", manager_zone),
            make_fact("needs-shutter-open", manager_zone),
        ])

        goal_facts.extend([
            make_fact("fan-on", battery_zone),
            make_fact("alarm-off", battery_zone),
            make_fact("orange-light-on", manager_zone),
            make_fact("shutter-open", manager_zone),
        ])

    else:
        init_facts.extend([
            make_fact("needs-green-light", manager_zone),
            make_fact("needs-shutter-open", manager_zone),
        ])

        goal_facts.extend([
            make_fact("fan-off", battery_zone),
            make_fact("alarm-off", battery_zone),
            make_fact("green-light-on", manager_zone),
            make_fact("shutter-open", manager_zone),
        ])

    if battery_condition == "LOW":
        init_facts.append(make_fact("needs-battery-warning", battery_zone))
        goal_facts.append(make_fact("battery-warning-sent", battery_zone))

    elif battery_condition == "CRITICAL":
        init_facts.append(make_fact("needs-battery-maintenance", battery_zone))
        goal_facts.append(make_fact("battery-maintenance-requested", battery_zone))

    init_text = "\n    ".join(init_facts)
    goal_text = "\n      ".join(goal_facts)

    problem_text = f"""(define (problem smart-battery-warehouse-current-state)
  (:domain smart-battery-warehouse)

  (:objects
    {battery_zone} {manager_zone} - zone
    {manager_dashboard} - dashboard
  )

  (:init
    {init_text}
  )

  (:goal
    (and
      {goal_text}
    )
  )
)
"""

    output_path = Path(output_path)
    output_path.write_text(problem_text, encoding="utf-8")

    print(f"[PDDL] Generated problem file: {output_path}")
    print(f"[PDDL] Risk level: {risk_level}")
    print(f"[PDDL] Battery condition: {battery_condition}")

    return output_path


if __name__ == "__main__":
    example_context = {
        "temperature": 26.0,
        "humidity": 17.0,
        "gas_status": "OK",
        "occupancy": 0,
        "battery_status": 80,
        "risk_level": "LOW",
        "battery_condition": "NORMAL",
    }

    generate_problem(example_context)