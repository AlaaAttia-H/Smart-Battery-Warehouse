# Planner README

The planner uses PDDL and Fast Downward.

## Folder

```text
laptop/src/planner/
├── README.md
├── ai_planner.py
├── domain.pddl
├── problem_generator.py
└── generated_problem.pddl
```

## Fast Downward Setup

Official Fast Downward links:

```text
Main website:
https://www.fast-downward.org/

Latest releases / download:
https://www.fast-downward.org/latest/releases/

Quick start documentation:
https://www.fast-downward.org/latest/documentation/quick-start/

Windows installation guide:
https://www.fast-downward.org/latest/for-developers/blog/install-on-windows/
```

Download the latest release from the official releases page and extract it to any folder on the laptop.

Example folder:

```text
C:/tools/fast-downward/
```

The important file is:

```text
fast-downward.py
```

Build it from Developer PowerShell or x64 Native Tools Command Prompt:

```powershell
cd "<PATH_TO_FAST_DOWNWARD_FOLDER>"
py build.py
py fast-downward.py --help
```

Then set the path in:

```text
laptop/src/config/config.json
```

```json
"fast_downward_path": "<PATH_TO_FAST_DOWNWARD_FOLDER>/fast-downward.py"
```

Use forward slashes `/` in the JSON path. Do not commit a personal machine-specific path if the repository is shared.

## Planner Responsibility

The planner decides what actions are needed.

The executor should not contain special rules like:

```text
waiting for occupancy
checking sensors directly
dashboard formatting
hardware-specific safety logic
```

## High Risk Rule

```text
HIGH risk + occupancy = 1:
activate-alarm
set-red-light
notify-manager
request-evacuation
update-dashboard
do not close shutter

HIGH risk + occupancy = 0:
activate-alarm
set-red-light
notify-manager
close-shutter
update-dashboard
```

## Fan Rule

```text
MEDIUM risk -> start-fan
HIGH risk -> do not start fan
LOW risk -> stop-fan
```

## Battery Rule

```text
LOW battery -> send-battery-warning
CRITICAL battery -> request-battery-maintenance
```

## Test

From `laptop/src`:

```powershell
python -m planner.problem_generator
python -m planner.ai_planner
```
