#!/usr/bin/env python3
"""Run inline `check` judges against artifacts from a completed eval run.

Lets a judge be validated on real decomposition output before it is wired into
eval.yaml — a judge that has never seen a real artifact tree is a guess.

The `outputs` record mirrors what skills/eval-run/scripts/score.py builds:
  files            {path relative to the case dir: content}
  annotations      parsed annotations.yaml from the DATASET case (not the run)
  case_dir         absolute path to the collected case directory
  exit_code / duration_s / cost_usd / num_turns   from run_result.json
  conversation     assistant text extracted from stdout.log (best effort)

Execution matches score.py exactly: the snippet is wrapped in
`def _check(outputs, arguments)` and exec'd, so top-level `return` works.

Usage:
    # every check judge in eval.yaml, over every case of the latest run
    python3 eval/scripts/try_judge.py

    # candidate judges from a scratch file, one judge, one case
    python3 eval/scripts/try_judge.py --judges-file /tmp/candidates.yaml \
        --judge component_vocabulary --case case-002-complex-genai-eval
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

import yaml

# Default to the newest run directory so calibration always uses current data.
def _latest_run():
    root = Path("eval/runs/epic-decompose")
    runs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "cases").is_dir()) \
        if root.is_dir() else []
    return runs[-1] if runs else root / "none"

DEFAULT_RUN = _latest_run()
DATASET = Path("eval/cases")


def _load_case_outputs(case_dir, dataset_dir=DATASET):
    """Build the `outputs` record score.py would pass to a check judge."""
    files = {}
    for p in sorted(case_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(case_dir).as_posix()
        if rel.split("/")[0] in {"subagents"} or rel.endswith((".log", ".json")):
            continue
        try:
            files[rel] = p.read_text()
        except (UnicodeDecodeError, OSError):
            continue

    annotations = {}
    ann_path = dataset_dir / case_dir.name / "annotations.yaml"
    if ann_path.is_file():
        annotations = yaml.safe_load(ann_path.read_text()) or {}

    record = {
        "files": files,
        "annotations": annotations,
        "case_dir": str(case_dir.resolve()),
        "conversation": "",
        "exit_code": 0,
        "modified_files": {},
        "tool_calls": [],
        "stderr": "",
        "events": [],
    }

    stdout_path = case_dir / "stdout.log"
    if stdout_path.is_file():
        try:
            record["stdout"] = stdout_path.read_text(errors="ignore")
        except OSError:
            pass

    events_path = case_dir / "events.json"
    if events_path.is_file():
        try:
            parsed = json.loads(events_path.read_text())
            if isinstance(parsed, list):
                record["events"] = parsed
        except (json.JSONDecodeError, OSError):
            pass

    rr = case_dir / "run_result.json"
    if rr.is_file():
        try:
            data = json.loads(rr.read_text())
            for k in ("exit_code", "duration_s", "cost_usd", "num_turns"):
                if k in data:
                    record[k] = data[k]
        except json.JSONDecodeError:
            pass

    stdout = case_dir / "stdout.log"
    if stdout.is_file():
        texts = []
        for line in stdout.read_text(errors="ignore").splitlines():
            try:
                ev = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
                for b in ev.get("message", {}).get("content", []):
                    if b.get("type") == "text" and b.get("text", "").strip():
                        texts.append(b["text"])
        record["conversation"] = "\n\n".join(texts)
    return record


def _compile_check(name, source):
    wrapped = f"def _check(outputs, arguments):\n{textwrap.indent(source, '    ')}"
    ns = {"__builtins__": __builtins__}
    exec(compile(wrapped, f"<check:{name}>", "exec"), ns)  # noqa: S102 — same as score.py
    return ns["_check"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(DEFAULT_RUN))
    ap.add_argument("--judges-file", default="eval/epic-decompose.yaml")
    ap.add_argument("--judge", action="append", help="judge name (repeatable); default all check judges")
    ap.add_argument("--case", action="append", help="case id (repeatable); default all cases in the run")
    ap.add_argument("--dataset", default=str(DATASET))
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.judges_file).read_text()) or {}
    judges = [j for j in (cfg.get("judges") or []) if j.get("check")]
    if args.judge:
        judges = [j for j in judges if j["name"] in set(args.judge)]
    if not judges:
        raise SystemExit(f"no inline check judges matched in {args.judges_file}")

    cases_root = Path(args.run) / "cases"
    if not cases_root.is_dir():
        raise SystemExit(f"no cases under {cases_root}")
    case_dirs = sorted(d for d in cases_root.iterdir() if d.is_dir())
    if args.case:
        wanted = set(args.case)
        case_dirs = [d for d in case_dirs if d.name in wanted]

    failures = 0
    for j in judges:
        print(f"\n=== {j['name']} ===")
        try:
            fn = _compile_check(j["name"], j["check"])
        except SyntaxError as exc:
            print(f"  SYNTAX ERROR: {exc}")
            failures += 1
            continue
        for case_dir in case_dirs:
            outputs = _load_case_outputs(case_dir, Path(args.dataset))
            try:
                result = fn(outputs, j.get("arguments") or {})
            except Exception as exc:  # a judge must never explode on real data
                print(f"  {case_dir.name:<44} RAISED {type(exc).__name__}: {exc}")
                failures += 1
                continue
            if not (isinstance(result, tuple) and len(result) == 2):
                print(f"  {case_dir.name:<44} BAD RETURN {result!r}")
                failures += 1
                continue
            value, rationale = result
            print(f"  {case_dir.name:<44} {str(value):<6} {str(rationale)[:110]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
