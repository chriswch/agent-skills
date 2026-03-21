# Code Review Report Template

Use this template for medium+ reviews. For small reviews, use a condensed version — just the issues table and a one-line assessment.

```markdown
## Code Review: [story/slice title]

**Scope**: [N files reviewed] | [brief description of what was built]
**Overall Assessment**: [One sentence — is this code well-structured, adequate, or problematic?]

### Critical Issues

_None found._ (or table below)

| # | File:Line | Issue | Recommendation |
|---|-----------|-------|----------------|
| 1 | `path/to/file.ts:42` | [what's wrong and why it matters] | [specific fix: "Replace X with Y"] |

### High Issues

_None found._ (or table below)

| # | File:Line | Issue | Recommendation |
|---|-----------|-------|----------------|
| 1 | `path/to/file.ts:15` | [what's wrong and why it matters] | [specific fix] |

### Medium Issues

_None found._ (or table below)

| # | File:Line | Issue | Recommendation |
|---|-----------|-------|----------------|
| 1 | `path/to/file.ts:88` | [what's wrong and why it matters] | [specific fix] |

### Low Issues (for user consideration)

_None found._ (or table below)

| # | File:Line | Issue | Recommendation |
|---|-----------|-------|----------------|
| 1 | `path/to/file.ts:3` | [description] | [suggestion] |

### What's Done Well

- [Acknowledge specific good decisions — data structure choice, clean separation, idiomatic usage, etc.]

### Summary

- Critical: N | High: N | Medium: N | Low: N
- Auto-fixable (critical + high + medium): N
- For user review (low): N
```

## Guidelines

- **File:Line format**: Always include the file path and line number so the fixer can locate issues precisely.
- **Actionable recommendations**: Every issue needs a concrete recommendation. "Replace the string map with a typed enum" not "consider improving this."
- **Group related issues**: If the same pattern appears in multiple files, list it once with all locations rather than repeating the same finding.
- **Empty sections are fine**: If there are no critical issues, say so. Don't manufacture findings to fill the template.
- **Overall assessment in one sentence**: "Clean implementation with minor simplification opportunities" or "Data model needs restructuring before this is maintainable."
