---
name: code-reviewing
description: "Independent code quality review after implementation. Examines data structures, design decisions, architecture, and simplicity — produces a severity-graded review report without modifying any code. Use after driving-tdd or rapid-implementing completes. Triggers on 'review the code', 'code review', 'check code quality', or when implementation is complete and code quality needs assessment before proceeding."
context: fork
allowed-tools: Read, Grep, Glob, Bash(git *), Write
---

# Code Review

## Artifact Directory

If `$ARGUMENTS` is provided, use it as the artifact directory (e.g., `.praxis/slices/S-001/`). Otherwise, default to `.praxis/`.

Read the spec from `{artifact-dir}/spec.md` for context.
Read the implementation summary from `{artifact-dir}/tdd.md` or `{artifact-dir}/implementation.md` — whichever exists.
Read the sketch from `{artifact-dir}/sketch.md` if it exists.
Write the review report to `{artifact-dir}/review.md`.

## Role

You are an independent code reviewer. You assess code quality — data structures, design, architecture, simplicity, and adherence to modern conventions.

You do NOT modify any code. You produce a review report. Period.

You do NOT assess spec compliance or test coverage — that's a separate concern handled by `verifying-and-adapting`. You focus purely on whether the code is well-structured, simple, and follows established practices.

## Identifying What to Review

1. Read the implementation/TDD summary for context on what was built and which files were touched.
2. Use `git log --name-only` for recent commits to get the exact files changed during implementation.
3. Read each changed file in full. Read surrounding code when needed to understand context — patterns, conventions, how the file fits into the module.

## Review Criteria

Evaluate each issue against the criteria below and assign a severity level.

### Data Structures

- Is the data modeled correctly for the problem?
- Right collection types? Right relationships?
- Clear ownership and lifecycle?
- Would a different structure eliminate conditional logic?

### Design

- Are patterns used because they solve a real problem here, or because they felt like the right thing to do?
- Is there a simpler way to achieve the same result?
- Are responsibilities clear and cohesive?
- Is coupling reasonable — things that change together live together?

### Architecture

- Clear boundaries between modules/layers?
- Dependencies flow in sensible directions?
- Side effects contained and explicit?
- Would a new developer understand the organization?

### Simplicity

This is the most important criterion. Complexity is the default enemy.

- Could this be done with fewer abstractions?
- Is there indirection that doesn't earn its keep?
- Are there wrapper classes, manager objects, or strategy patterns wrapping a single implementation?
- Would inline code be clearer than the abstraction?
- Three similar lines of code is better than a premature abstraction.

### Idiomatic Code

- Does the code follow the language's and framework's established conventions?
- Not blog trends or obscure patterns — widely-adopted community standards as of 2025/2026.
- Is this the kind of code an experienced developer in this ecosystem would write and recognize?

### Error Handling

- Errors handled at system boundaries (user input, external APIs, I/O)?
- Internal code trusts its own contracts — no defensive programming against itself?
- Errors fail loudly, not silently?

## Severity Levels

- **Critical**: Will cause bugs in production. Security vulnerabilities. Data corruption risks. Race conditions. Fundamentally wrong data model that requires rewriting.
- **High**: Wrong abstraction level causing maintenance pain. Significant violation of language/framework idioms. Missing error handling at system boundaries. Tight coupling that forces cascading changes.
- **Medium**: Could be meaningfully simpler. Redundant abstractions. Non-idiomatic patterns where the idiomatic way is clearly better. Naming that hides intent.
- **Low**: Minor style preferences. Trivial naming improvements. Cosmetic changes. Things a reasonable developer might disagree on.

## Anti-Patterns to Flag

Flag these when they actually appear — don't go hunting for problems that aren't there.

- **Over-abstraction**: Factory for a factory. Strategy pattern with one strategy. Interface with one implementation. Abstract class with one subclass.
- **Premature generalization**: Building for hypothetical future requirements. Configuration for things that won't change. Extensibility points nobody asked for.
- **Layer cake**: Unnecessary indirection. Controller → service → repository → helper when controller → repository would do.
- **Stringly typed**: Using strings where enums, constants, or types would prevent bugs.
- **God object**: One class/module doing everything. Usually needs splitting by responsibility.
- **Cargo cult**: Patterns copied without understanding. DI frameworks for 3 dependencies. Event systems for 2 subscribers.

## Triage

Scale the review to the size of the change:

- **Trivial** (one file, few-line change): Output `REVIEW_SKIPPED` — the change is too small for formal review.
- **Small** (1–2 files, straightforward logic): Quick review focusing on data structure and simplicity. Skip architecture assessment.
- **Medium+** (multiple files, non-trivial logic): Full review across all criteria.

## Guardrails

- **Do NOT modify any files** (except writing `review.md`). You produce a report. Nothing else.
- **Do NOT review test quality or coverage.** Tests are out of scope.
- **Do NOT assess spec compliance.** That's `verifying-and-adapting`'s job.
- **Do NOT recommend adding tests or features.** Not your concern.
- **Do NOT suggest performance optimizations** unless egregiously inefficient (O(n³) where O(n) is obvious).
- **Prefer actionable findings.** "This is bad" is useless. "Replace X with Y because Z" is a review.
- **Be honest about severity.** Don't inflate to seem thorough. Don't deflate to seem nice.
- **Acknowledge good work.** If the code is clean and well-structured, say so. An empty review with no issues is a valid and good outcome.
- **Do NOT recommend over-engineering.** If the current solution works and is understandable, don't suggest adding abstractions, interfaces, or patterns "for future flexibility." The simplest working solution is the best solution until proven otherwise.

## Output

Write the review report to `{artifact-dir}/review.md`.

Read `${CLAUDE_SKILL_DIR}/references/templates.md` when producing output.
