# Praxis

Spec-driven, test-driven development skills for Claude Code.

## Workflow

Pipeline: `clarifying-intent` → [`slicing-stories`] → `sketching-design` → `driving-tdd` → `verifying-and-adapting`

Fast paths: Trivial skips everything. Bug fix → clarify + TDD. Refactor → existing tests + refactor. Every skill triages by size.

## Artifact paths

Skills write workflow artifacts to `.praxis/` in the working project:

| Artifact         | Path              | Producer                 |
| ---------------- | ----------------- | ------------------------ |
| Feature Brief    | `brief.md`        | `clarifying-intent`      |
| Slice Map        | `slice-map.json`  | `slicing-stories`        |
| Story-Level Spec | `spec.md`         | `clarifying-intent`      |
| Design Sketch    | `sketch.md`       | `sketching-design`       |
| TDD Session      | `tdd.md`          | `driving-tdd`            |
| Verification     | `verification.md` | `verifying-and-adapting` |

Single-story: `.praxis/spec.md`, `.praxis/sketch.md`, etc.
Multi-slice: `.praxis/slices/{slice-id}/spec.md`, `.praxis/slices/{slice-id}/sketch.md`, etc.
Feature-level artifacts (`brief.md`, `slice-map.json`) always live at `.praxis/` root.
