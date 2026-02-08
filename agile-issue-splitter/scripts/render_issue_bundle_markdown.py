#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


TYPE_DISPLAY = {"user_story": "User Story", "task": "Task", "bug": "Bug"}
ISSUE_PREFIX_ORDER = {"US": 0, "TASK": 1, "BUG": 2}


def _id_key(value: Any, *, prefix_order: dict[str, int]) -> tuple[int, int, str]:
    if not isinstance(value, str):
        return (99, 0, str(value))
    match = re.fullmatch(r"([A-Z]+)-(\d+)", value)
    if not match:
        return (99, 0, value)
    prefix, num_str = match.group(1), match.group(2)
    return (prefix_order.get(prefix, 99), int(num_str), value)


def _md_cell(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value if item is not None)
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "\\|") if text else "—"


def _format_estimate(estimate: Any) -> str:
    if not isinstance(estimate, dict):
        return "—"
    method = estimate.get("method")
    value = estimate.get("value")
    if method is None:
        return "—"
    if method == "unknown":
        return "unknown"
    if value is None:
        return str(method)
    return f"{method} {value}"


def _require_object(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("top-level JSON must be an object")
    for key in ("meta", "epics", "issues"):
        if key not in bundle:
            raise ValueError(f"missing required top-level key: {key}")
    if not isinstance(bundle.get("meta"), dict):
        raise ValueError("'meta' must be an object")
    if not isinstance(bundle.get("epics"), list):
        raise ValueError("'epics' must be an array")
    if not isinstance(bundle.get("issues"), list):
        raise ValueError("'issues' must be an array")
    return bundle


def _render_meta(lines: list[str], meta: dict[str, Any]) -> None:
    lines.append("## Meta")
    lines.append(f"- **Source:** {_md_cell(meta.get('source'))}")
    lines.append(f"- **Generated:** {_md_cell(meta.get('generated_at'))}")

    assumptions = meta.get("assumptions") if isinstance(meta.get("assumptions"), list) else []
    lines.append("")
    lines.append("## Assumptions")
    if assumptions:
        for item in assumptions:
            lines.append(f"- {_md_cell(item)}")
    else:
        lines.append("- —")

    open_questions = meta.get("open_questions") if isinstance(meta.get("open_questions"), list) else []
    lines.append("")
    lines.append("## Open Questions")
    if open_questions:
        for q in sorted(
            [item for item in open_questions if isinstance(item, dict)],
            key=lambda item: _id_key(item.get("id"), prefix_order={"Q": 0}),
        ):
            q_id = _md_cell(q.get("id"))
            q_type = _md_cell(q.get("type"))
            owner = _md_cell(q.get("owner"))
            question = _md_cell(q.get("question"))
            lines.append(f"- **{q_id}** ({q_type}, owner: {owner}): {question}")
            context = q.get("context")
            if isinstance(context, str) and context.strip():
                lines.append(f"  - Context: {_md_cell(context)}")
    else:
        lines.append("- —")


def _render_epics(lines: list[str], epics: list[Any]) -> dict[str, dict[str, Any]]:
    lines.append("")
    lines.append("## Epics")

    epic_dicts = [e for e in epics if isinstance(e, dict)]
    epic_by_id: dict[str, dict[str, Any]] = {}
    if not epic_dicts:
        lines.append("- —")
        return epic_by_id

    for epic in sorted(epic_dicts, key=lambda e: _id_key(e.get("id"), prefix_order={"E": 0})):
        epic_id = epic.get("id")
        if isinstance(epic_id, str):
            epic_by_id[epic_id] = epic
        lines.append(f"### {_md_cell(epic.get('id'))}: {_md_cell(epic.get('title'))}")
        lines.append(f"- **Objective:** {_md_cell(epic.get('objective'))}")
        exit_criteria = epic.get("exit_criteria") if isinstance(epic.get("exit_criteria"), list) else []
        lines.append("- **Exit criteria:**")
        if exit_criteria:
            for item in exit_criteria:
                lines.append(f"  - {_md_cell(item)}")
        else:
            lines.append("  - —")
        non_goals = epic.get("non_goals") if isinstance(epic.get("non_goals"), list) else []
        if non_goals:
            lines.append("- **Non-goals:**")
            for item in non_goals:
                lines.append(f"  - {_md_cell(item)}")
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()
    return epic_by_id


def _render_summary_table(lines: list[str], issues: list[dict[str, Any]]) -> None:
    lines.append("")
    lines.append("## Backlog Summary")
    lines.append("")
    lines.append("| ID | Type | P | Status | Epic | Parent | WS | Title | Blocked by |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for issue in issues:
        issue_id = _md_cell(issue.get("id"))
        issue_type = _md_cell(TYPE_DISPLAY.get(issue.get("type"), issue.get("type")))
        priority = _md_cell(issue.get("priority"))
        status = _md_cell(issue.get("status"))
        epic_id = _md_cell(issue.get("epic_id"))
        parent_id = _md_cell(issue.get("parent_id"))
        workstream = _md_cell(issue.get("workstream"))
        title = _md_cell(issue.get("title"))
        blocked_by = _md_cell(issue.get("blocked_by"))
        lines.append(
            f"| {issue_id} | {issue_type} | {priority} | {status} | {epic_id} | {parent_id} | {workstream} | {title} | {blocked_by} |"
        )


def _render_issue_common(lines: list[str], issue: dict[str, Any]) -> None:
    issue_type = issue.get("type")
    lines.append(f"#### {_md_cell(issue.get('id'))}: {_md_cell(issue.get('title'))}")
    lines.append(
        f"- **Type:** {_md_cell(TYPE_DISPLAY.get(issue_type, issue_type))}  "
        f"**Priority:** {_md_cell(issue.get('priority'))}  "
        f"**Status:** {_md_cell(issue.get('status'))}  "
        f"**Estimate:** {_md_cell(_format_estimate(issue.get('estimate')))}"
    )
    lines.append(
        f"- **Epic:** {_md_cell(issue.get('epic_id'))}  "
        f"**Parent:** {_md_cell(issue.get('parent_id'))}  "
        f"**Workstream:** {_md_cell(issue.get('workstream'))}"
    )
    lines.append(f"- **Labels:** {_md_cell(issue.get('labels'))}")
    lines.append(f"- **Blocked by:** {_md_cell(issue.get('blocked_by'))}")
    lines.append("")
    lines.append("**Description**")
    lines.append(_md_cell(issue.get("description")))


def _render_user_story(lines: list[str], issue: dict[str, Any]) -> None:
    lines.append("")
    lines.append("**Story**")
    lines.append(_md_cell(issue.get("story")))
    lines.append("")
    lines.append("**Value**")
    lines.append(_md_cell(issue.get("value")))
    ac = issue.get("acceptance_criteria") if isinstance(issue.get("acceptance_criteria"), list) else []
    lines.append("")
    lines.append("**Acceptance Criteria**")
    if ac:
        for item in ac:
            lines.append(f"- {_md_cell(item)}")
    else:
        lines.append("- —")
    dod = issue.get("definition_of_done") if isinstance(issue.get("definition_of_done"), list) else []
    if dod:
        lines.append("")
        lines.append("**Definition of Done**")
        for item in dod:
            lines.append(f"- {_md_cell(item)}")


def _render_task(lines: list[str], issue: dict[str, Any]) -> None:
    lines.append("")
    lines.append("**Task Kind**")
    lines.append(_md_cell(issue.get("task_kind")))
    lines.append("")
    lines.append("**Deliverable**")
    lines.append(_md_cell(issue.get("deliverable")))
    lines.append("")
    lines.append("**Verification**")
    lines.append(_md_cell(issue.get("verification")))
    ac = issue.get("acceptance_criteria") if isinstance(issue.get("acceptance_criteria"), list) else []
    if ac:
        lines.append("")
        lines.append("**Acceptance Criteria**")
        for item in ac:
            lines.append(f"- {_md_cell(item)}")
    dod = issue.get("definition_of_done") if isinstance(issue.get("definition_of_done"), list) else []
    if dod:
        lines.append("")
        lines.append("**Definition of Done**")
        for item in dod:
            lines.append(f"- {_md_cell(item)}")


def _render_bug(lines: list[str], issue: dict[str, Any]) -> None:
    lines.append("")
    lines.append("**Severity**")
    lines.append(_md_cell(issue.get("severity")))
    lines.append("")
    lines.append("**Environment**")
    lines.append(_md_cell(issue.get("environment")))
    steps = issue.get("steps_to_reproduce") if isinstance(issue.get("steps_to_reproduce"), list) else []
    lines.append("")
    lines.append("**Steps to Reproduce**")
    if steps:
        for item in steps:
            lines.append(f"- {_md_cell(item)}")
    else:
        lines.append("- —")
    lines.append("")
    lines.append("**Expected**")
    lines.append(_md_cell(issue.get("expected")))
    lines.append("")
    lines.append("**Actual**")
    lines.append(_md_cell(issue.get("actual")))
    ac = issue.get("acceptance_criteria") if isinstance(issue.get("acceptance_criteria"), list) else []
    lines.append("")
    lines.append("**Acceptance Criteria**")
    if ac:
        for item in ac:
            lines.append(f"- {_md_cell(item)}")
    else:
        lines.append("- —")
    dod = issue.get("definition_of_done") if isinstance(issue.get("definition_of_done"), list) else []
    if dod:
        lines.append("")
        lines.append("**Definition of Done**")
        for item in dod:
            lines.append(f"- {_md_cell(item)}")


def _render_issue_details(lines: list[str], issue: dict[str, Any]) -> None:
    _render_issue_common(lines, issue)
    issue_type = issue.get("type")
    if issue_type == "user_story":
        _render_user_story(lines, issue)
    elif issue_type == "task":
        _render_task(lines, issue)
    elif issue_type == "bug":
        _render_bug(lines, issue)
    lines.append("")


def render_issue_bundle_markdown(bundle: dict[str, Any], *, include_json: bool) -> str:
    bundle = _require_object(bundle)
    meta = bundle["meta"]
    epics = bundle["epics"]
    issues = bundle["issues"]

    project = meta.get("project") if isinstance(meta.get("project"), str) else "TBD"

    lines: list[str] = []
    lines.append(f"# Issue Bundle — {project}")
    lines.append("")
    _render_meta(lines, meta)
    epic_by_id = _render_epics(lines, epics)

    issue_dicts = [i for i in issues if isinstance(i, dict)]
    issue_dicts_sorted = sorted(
        issue_dicts, key=lambda i: _id_key(i.get("id"), prefix_order=ISSUE_PREFIX_ORDER)
    )
    _render_summary_table(lines, issue_dicts_sorted)

    children_by_parent_id: dict[str, list[dict[str, Any]]] = {}
    for issue in issue_dicts_sorted:
        parent_id = issue.get("parent_id")
        if isinstance(parent_id, str) and parent_id:
            children_by_parent_id.setdefault(parent_id, []).append(issue)

    lines.append("")
    lines.append("## Issue Details")

    epic_groups: dict[str | None, list[dict[str, Any]]] = {}
    for issue in issue_dicts_sorted:
        epic_groups.setdefault(issue.get("epic_id") if isinstance(issue.get("epic_id"), str) else None, []).append(
            issue
        )

    epic_ids_sorted = sorted([eid for eid in epic_groups.keys() if eid is not None], key=lambda eid: _id_key(eid, prefix_order={"E": 0}))
    if None in epic_groups:
        epic_ids_sorted.append(None)

    for epic_id in epic_ids_sorted:
        if epic_id is None:
            lines.append("")
            lines.append("### No Epic")
        else:
            epic = epic_by_id.get(epic_id, {})
            epic_title = epic.get("title") if isinstance(epic, dict) else None
            lines.append("")
            lines.append(f"### {epic_id}: {_md_cell(epic_title)}")

        group = epic_groups.get(epic_id, [])
        user_stories = [i for i in group if i.get("type") == "user_story"]
        others_top_level = [i for i in group if i.get("type") != "user_story" and not i.get("parent_id")]

        for story in sorted(user_stories, key=lambda i: _id_key(i.get("id"), prefix_order={"US": 0})):
            _render_issue_details(lines, story)
            story_id = story.get("id")
            if isinstance(story_id, str):
                children = children_by_parent_id.get(story_id, [])
                if children:
                    for child in sorted(
                        children,
                        key=lambda i: (
                            ISSUE_PREFIX_ORDER.get(str(i.get("id")).split("-", 1)[0], 99),
                            _id_key(i.get("id"), prefix_order=ISSUE_PREFIX_ORDER),
                        ),
                    ):
                        _render_issue_details(lines, child)

        for issue in others_top_level:
            _render_issue_details(lines, issue)

    if include_json:
        lines.append("")
        lines.append("## Issue Bundle (JSON)")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(bundle, indent=2, ensure_ascii=False))
        lines.append("```")

    return "\n".join(lines).rstrip() + "\n"


def _load_json_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Render an agile-issue-splitter Issue Bundle JSON file as human-readable Markdown (optionally embedding the JSON)."
    )
    parser.add_argument("path", nargs="?", default="issue-bundle.json", help="Path to issue-bundle.json (or '-' for stdin)")
    parser.add_argument("--no-json", action="store_true", help="Do not embed the JSON at the end of the Markdown output")
    parser.add_argument("--validate", action="store_true", help="Validate the bundle before rendering")
    parser.add_argument("--strict", action="store_true", help="Use strict validation (timestamp format and dependency cycles)")
    args = parser.parse_args(argv)

    try:
        raw = _load_json_text(args.path)
    except FileNotFoundError:
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: could not read {args.path}: {e}", file=sys.stderr)
        return 2

    try:
        bundle = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    if args.validate:
        try:
            from validate_issue_bundle import validate_issue_bundle  # type: ignore
        except Exception as e:  # pragma: no cover
            print(f"error: could not import validator: {e}", file=sys.stderr)
            return 2
        errors, warnings = validate_issue_bundle(bundle, strict=args.strict)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        if errors:
            return 1

    try:
        md = render_issue_bundle_markdown(bundle, include_json=not args.no_json)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

