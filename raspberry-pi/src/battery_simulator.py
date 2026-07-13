"""
Manual battery input.
"""

import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
BATTERY_STATE_FILE = PROJECT_ROOT / "runtime" / "battery_state.json"


def save_battery_value(battery_status):
    BATTERY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "battery_status": battery_status,
        "last_updated": datetime.now().isoformat(timespec="seconds"),
    }

    temp_file = BATTERY_STATE_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    temp_file.replace(BATTERY_STATE_FILE)


def main():
    print("[BATTERY INPUT] Type a battery percentage from 0 to 100")
    print("[BATTERY INPUT] Type q to quit")

    while True:
        user_input = input("Battery percentage: ").strip()

        if user_input.lower() == "q":
            break

        try:
            battery_status = int(user_input)
        except ValueError:
            print("[ERROR] Please enter a number between 0 and 100")
            continue

        if battery_status < 0 or battery_status > 100:
            print("[ERROR] Battery value must be between 0 and 100")
            continue

        save_battery_value(battery_status)
        print(f"[BATTERY INPUT] Saved battery value: {battery_status}%")


if __name__ == "__main__":
    main()