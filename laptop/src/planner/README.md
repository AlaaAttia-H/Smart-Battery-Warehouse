# AI Planner Setup

This README explains how to set up and test the AI planner.

The project uses:

```text
PDDL domain and problem files
Fast Downward classical planner
Python wrapper to run the planner
```

## 1. Planner Folder Contents

```text
planner/
├── README.md
├── __init__.py
├── ai_planner.py
├── domain.pddl
├── generated_problem.pddl
└── problem_generator.py
```

## 2. Download Fast Downward

Download Fast Downward from its official source and extract it to a folder on your computer.

Example folder structure:

```text
tools/
└── fast-downward/
    ├── fast-downward.py
    ├── build.py
    └── ...
```

The exact folder location does not matter, but you must remember the path to:

```text
fast-downward.py
```

## 3. Build Fast Downward on Windows

Open:

```text
Developer PowerShell for Visual Studio
```

or:

```text
x64 Native Tools Command Prompt for Visual Studio
```

Go to the Fast Downward folder:

```powershell
cd "<PATH_TO_FAST_DOWNWARD_FOLDER>"
```

Build:

```powershell
py build.py
```

Test:

```powershell
py fast-downward.py --help
```

If the help text appears, Fast Downward is working.

## 4. Add Planner Path to Config

Open:

```text
config/config.json
```

Set:

```json
"planner": {
  "fast_downward_path": "<PATH_TO_FAST_DOWNWARD_FOLDER>/fast-downward.py",
  "plan_output_path": "planner/generated_plan.txt"
}
```

Example format:

```json
"planner": {
  "fast_downward_path": "C:/tools/fast-downward/fast-downward.py",
  "plan_output_path": "planner/generated_plan.txt"
}
```

Use forward slashes `/` in the JSON path.

## 5. Test Problem Generation

From the project root:

```powershell
.\venv\Scripts\activate
python -m planner.problem_generator
```

This should create or update:

```text
planner/generated_problem.pddl
```

## 6. Test AI Planner

From the project root:

```powershell
python -m planner.ai_planner
```

Expected result:

```text
Planner runs
Plan is printed in terminal
planner/generated_plan.txt is created
```

## 7. Planner Flow

```text
sensor data
    ↓
context_processor.py
    ↓
problem_generator.py
    ↓
domain.pddl + generated_problem.pddl
    ↓
ai_planner.py
    ↓
generated_plan.txt
    ↓
plan_executor.py
```

## 8. Main Planner Actions

```text
start-fan
stop-fan
activate-alarm
deactivate-alarm
set-red-light
set-orange-light
set-green-light
open-shutter
close-shutter
notify-manager
request-evacuation
send-battery-warning
request-battery-maintenance
update-dashboard
```

## 9. Common Problems

### Fast Downward path is wrong

Check:

```text
config/config.json
```

The path must point to:

```text
fast-downward.py
```

### Windows cannot execute fast-downward.py

The Python wrapper should run Fast Downward using Python, not by executing the `.py` file directly.

The command should behave like:

```text
python fast-downward.py ...
```

### No plan generated

Check:

```text
planner/domain.pddl
planner/generated_problem.pddl
```

Make sure the generated problem has reachable goals.
