# CLAUDE.md

## Project identity
This repository is `podcast_creator_agent`.

## Primary objective
Continue development from **Step 16 onward** using the roadmap in `docs/development_plan.md`.

## Non-negotiable workflow
1. Read `docs/development_plan.md` and `docs/step_tracker.md` before doing any work.
2. Work on **one step only** per cycle.
3. Never start the next step until the current step is:
   - implemented
   - tested
   - validated
   - logged in `docs/step_tracker.md`
4. After completing a step, stop and wait for user review unless the user explicitly says to continue.
5. Never mark a step complete unless the tests or validations were actually run and passed.

## Starting point
- Steps 1–15 are already completed.
- Begin at **Step 16** unless `docs/step_tracker.md` says a later step is active.

## Required operating behavior
Before coding:
- Inspect the current repository structure.
- Identify the files relevant to the active step.
- Summarize the implementation plan for that step in plain English.
- Make the smallest safe change that satisfies the step.

During coding:
- Avoid unrelated refactors.
- Preserve backward compatibility when practical.
- Do not delete or overwrite `.env`, local secrets, or user configuration.
- Do not introduce major dependencies unless clearly necessary for the active step.

After coding:
- Run the relevant checks.
- Prefer targeted tests first, then broader tests if needed.
- Perform a realistic manual validation for the active feature.
- Update `docs/step_tracker.md` with:
  - status
  - files changed
  - commands run
  - validation results
  - open issues
  - notes for next step

## Validation rules
Use the best matching commands that exist in this repository. If a command does not exist, say so explicitly and use the closest available alternative.

Recommended validation order:
1. Formatting or lint check
2. Unit tests
3. Integration or workflow test for the active step
4. Manual validation of user-facing behavior

Possible commands, only if available in this repo:
- `ruff check .`
- `ruff format --check .`
- `python -m pytest`
- `python -m pytest tests -q`
- `python main.py`
- `python app.py`

## Completion gate
A step is only complete when all are true:
- The code change for the active step is implemented.
- The relevant validations were run.
- The observed results are recorded.
- `docs/step_tracker.md` is updated.
- No unresolved blocker prevents normal use of the active step.

## Blocker handling
If blocked:
- Do not move to the next step.
- Explain the blocker clearly.
- Record the blocker in `docs/step_tracker.md`.
- Suggest the smallest next action needed to unblock the step.

## Output style for each work cycle
For each step, produce a short structured summary:
- Current step
- What you found
- What you changed
- What commands you ran
- What passed or failed
- What still needs review

## Step-specific guidance for Step 16
Goal:
- Prevent episode overwrites by creating unique episode IDs and timestamped output folders.

Expected example:
- `AI_overview_2026-04-06_101500`

Minimum acceptance for Step 16:
- Re-running the same topic twice should produce two distinct episode folders.
- Metadata and episode index behavior should still function correctly.
- Output paths should point to the new unique folder paths.

## Repo file conventions
Assume these files exist or should exist:
- `docs/development_plan.md`
- `docs/step_tracker.md`
- `CLAUDE.md`

If these files are missing in the repo, recreate them from the latest committed content or ask the user to restore them before continuing.
