#!/usr/bin/env python3
"""Summarise a kicad-cli ERC or DRC JSON report for GitHub Actions.

Usage:
    kicad_report.py erc REPORT.json [--fail-on error|warning]
    kicad_report.py drc REPORT.json [--fail-on error|warning]

Reads the JSON written by `kicad-cli sch erc --format json` or
`kicad-cli pcb drc --format json` (run with --severity-all so warnings and
excluded markers are present), then:

  * prints one GitHub annotation (::error:: / ::warning:: / ::notice::) per
    non-excluded violation, so they show up on the run and on pull requests;
  * prints a per-type count table to stdout and appends it to the job summary
    ($GITHUB_STEP_SUMMARY) when running under GitHub Actions;
  * exits 1 if any non-excluded violation at or above --fail-on exists.

Violations the user excluded in KiCad ("excluded": true) are counted but never
annotated and never fail the run.
"""

import argparse
import collections
import json
import os
import sys

SEVERITY_RANK = {"error": 2, "warning": 1, "info": 0}


def iter_violations(kind, data):
    """Yield (section_label, sheet_path, violation) for every entry in the report."""
    if kind == "erc":
        for sheet in data.get("sheets", []):
            path = sheet.get("path") or ""
            for v in sheet.get("violations", []):
                yield "ERC", path, v
    else:
        sections = (
            ("violations", "DRC"),
            ("unconnected_items", "Unconnected"),
            ("schematic_parity", "Parity"),
        )
        for key, label in sections:
            for v in data.get(key, []):
                yield label, "", v


def describe_items(violation, units):
    parts = []
    for item in violation.get("items", []):
        text = item.get("description", "")
        pos = item.get("pos")
        if isinstance(pos, dict) and "x" in pos and "y" in pos:
            text += f" @ ({pos['x']}, {pos['y']}) {units}"
        if text:
            parts.append(text)
    return "; ".join(parts)


def escape_annotation(text):
    """Escape a message for a GitHub workflow command."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("kind", choices=["erc", "drc"])
    parser.add_argument("report", help="JSON report written by kicad-cli")
    parser.add_argument("--fail-on", choices=["error", "warning"], default="error",
                        help="lowest severity that fails the run (default: error)")
    args = parser.parse_args()

    with open(args.report, encoding="utf-8-sig") as f:
        data = json.load(f)

    units = data.get("coordinate_units", "mm")
    threshold = SEVERITY_RANK[args.fail_on]
    counts = collections.Counter()
    totals = collections.Counter()
    failing = 0

    for label, sheet, v in iter_violations(args.kind, data):
        severity = str(v.get("severity", "error")).lower()
        if v.get("excluded"):
            totals["excluded"] += 1
            continue
        counts[(label, v.get("type", "?"), severity)] += 1
        totals[severity] += 1
        if SEVERITY_RANK.get(severity, 2) >= threshold:
            failing += 1

        message = f"{label} {v.get('type', '?')}: {v.get('description', '')}"
        detail = describe_items(v, units)
        if detail:
            message += f" [{detail}]"
        if sheet:
            message += f" (sheet {sheet})"
        command = {"error": "error", "warning": "warning"}.get(severity, "notice")
        print(f"::{command}::{escape_annotation(message)}")

    title = f"{args.kind.upper()} — KiCad {data.get('kicad_version', '?')} — {os.path.basename(data.get('source', args.report))}"
    lines = [f"### {title}", ""]
    if counts:
        lines += ["| Check | Type | Severity | Count |", "|---|---|---|---|"]
        for (label, vtype, severity), n in sorted(counts.items(), key=lambda kv: (-SEVERITY_RANK.get(kv[0][2], 2), kv[0])):
            lines.append(f"| {label} | `{vtype}` | {severity} | {n} |")
        lines.append("")
    lines.append(
        f"**{totals['error']} error(s), {totals['warning']} warning(s), "
        f"{totals['excluded']} excluded** — fail on: {args.fail_on}"
    )
    verdict = "FAILED" if failing else "passed"
    lines.append(f"Result: **{verdict}**")
    summary = "\n".join(lines) + "\n"

    print(summary)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(summary + "\n")

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
