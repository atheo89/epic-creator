#!/usr/bin/env python3
"""Build anonymized eval cases from raw RHAISTRAT snapshots.

Fidelity path is deterministic: the strategy body is the verbatim text from
``eval/.raw/<KEY>.raw.md`` with substitutions applied — never re-typed by a
model.

Three substitution layers, applied longest-match-first:

1. **Ticket re-keying** (deterministic): every real ticket key is mapped into
   a synthetic range so an anonymized case cannot be traced back to the real
   issue.  Jira browse URLs collapse to the bare re-keyed key.
2. **Semantic replacements** (from the LLM review pass): customer/partner
   orgs, individuals, and any other identifying prose, supplied per case in
   ``eval/.raw/<KEY>.tokens.yaml`` and resolved globally (same original ->
   same fictional value across every case) in ``eval/.entity-map.yaml``.
3. **Hard redaction** (deterministic backstop): emails and any surviving
   non-public URL.

Usage:
    python3 eval/scripts/build_real_cases.py [--check-only]
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

RAW_DIR = Path("eval/.raw")
CASES_DIR = Path("eval/cases")
ENTITY_MAP = Path("eval/.entity-map.yaml")
REAL_COMPONENTS = Path("eval/shared/real/rhai-components.txt")
ARCH_SRC = Path(".context/architecture-context/architecture/rhoai-3.6-ea.1")
ARCH_REL = "architecture-context/architecture/rhoai-3.6-ea.1"

PUBLIC_HOSTS = {"github.com", "docs.redhat.com", "www.redhat.com", "access.redhat.com"}
PUBLIC_SUFFIXES = (".github.io", ".nist.gov", ".kubernetes.io", ".openshift.io", ".readthedocs.io")
# Only re-key strings that are genuinely Jira issue keys.  Technical tokens
# like KEM-768 (ML-KEM parameter set), AC-2 (NIST control) and OCP-5 match the
# same shape and MUST stay verbatim or the strategy becomes technically wrong.
JIRA_PREFIXES = {
    "RHAISTRAT", "RHAIRFE", "RHOAIENG", "RHOAIUX", "AIPCC", "RHAI", "RHAIC",
    "RHAICI", "RHAIFIRST", "INFERSUP", "OCPSTRAT", "OCPBUGS", "RHOAI", "KFLUXBUGS",
    "PSASTRAT", "RHELMISC", "RHELPLAN",
}


def is_public_host(host):
    return host in PUBLIC_HOSTS or host.endswith(PUBLIC_SUFFIXES)
# Internal process/release labels are dropped: they leak roadmap targeting and
# internal tooling state, and add nothing to a decomposition test.
DROP_LABEL = re.compile(
    r"^(rfe-creator|strat-creator|epic-creator|test-plan|rp-|qg\d)"
    r"|^\d+\.\d+[-.]|^rhoai-\d|needs-tech-review",
    re.I,
)


def load_raw(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?\n)---\n\n?(.*)$", text, re.DOTALL)
    if not m:
        raise SystemExit(f"{path}: malformed raw snapshot")
    return yaml.safe_load(m.group(1)), m.group(2)


def build_substitutions(header, body, meta, entity_map):
    """Return {original: replacement}, longest-first at apply time."""
    subs = {}
    real_key = header["real_key"]
    synth_key = meta["synthetic_key"]

    # Layer 1 — ticket re-keying. Collect every real Jira key referenced.
    keys = set(re.findall(r"\b([A-Z][A-Z0-9]+)-(\d+)\b", body))
    keys = {f"{p}-{n}" for p, n in keys if p in JIRA_PREFIXES} | {real_key}
    key_map = dict(meta.get("ticket_key_map") or {})
    key_map[real_key] = synth_key
    used = set(key_map.values())
    for k in sorted(keys):
        if k in key_map:
            continue
        prefix, num = k.rsplit("-", 1)
        # Deterministic and collision-free within a prefix.
        candidate = 7000 + (int(num) % 900)
        while f"{prefix}-{candidate}" in used:
            candidate += 1
        key_map[k] = f"{prefix}-{candidate}"
        used.add(key_map[k])
    # Markdown links and bare URLs collapse to the re-keyed bare key.
    for k, v in key_map.items():
        subs[f"[{k}](https://redhat.atlassian.net/browse/{k})"] = v
        subs[f"https://redhat.atlassian.net/browse/{k}"] = v
        subs[k] = v

    # Layer 2 — semantic replacements resolved through the global entity map.
    for original, replacement in entity_map.items():
        subs[original] = replacement

    return subs, key_map


def apply_subs(text, subs):
    for original in sorted(subs, key=len, reverse=True):
        text = text.replace(original, subs[original])
    return text


def redact_residual(text):
    """Deterministic backstop for anything the earlier layers missed."""
    notes = []
    new, n = re.subn(r"[\w.+-]+@[\w.-]+\.\w+", "[email removed]", text)
    if n:
        notes.append(f"{n} email(s) redacted")

    def _url(m):
        host = m.group(1)
        if is_public_host(host):
            return m.group(0)
        notes.append(f"internal link removed ({host})")
        return "[internal link removed]"

    new = re.sub(r"https?://([\w.-]+)[^\s)\]]*", _url, new)
    return new, notes


def build_case(raw_path, entity_map, check_only=False):
    header, body = load_raw(raw_path)
    key = header["real_key"]
    meta_path = RAW_DIR / f"{key}.meta.yaml"
    if not meta_path.exists():
        return {"key": key, "status": "SKIPPED", "reason": "no meta.yaml (review pass not done)"}
    meta = yaml.safe_load(meta_path.read_text())

    subs, key_map = build_substitutions(header, body, meta, entity_map)
    anon_body = apply_subs(body, subs)
    anon_body, redactions = redact_residual(anon_body)
    anon_title = redact_residual(apply_subs(header["summary"], subs))[0]

    synth_key = meta["synthetic_key"]
    case_dir = CASES_DIR / meta["case_slug"]

    # Leak gate — never write a case that still contains the real key.
    leaks = []
    if re.search(rf"\b{re.escape(key)}\b", anon_body + anon_title):
        leaks.append(f"real key {key} survives substitution")
    for original in entity_map:
        if original and original in anon_body:
            leaks.append(f"unreplaced entity: {original[:40]}")
    if leaks:
        return {"key": key, "status": "LEAK", "reason": "; ".join(leaks)}

    if check_only:
        return {"key": key, "status": "OK(check)", "case": str(case_dir), "redactions": redactions}

    # --- write the strat-task file ---
    labels = [l for l in header.get("labels", []) if not DROP_LABEL.match(l)]
    labels = sorted(set(labels + ["refined"]))
    front = {
        "strat_id": synth_key,
        "title": anon_title,
        "status": header.get("status", ""),
        "priority": header.get("priority", ""),
        "labels": labels,
        # Links carry real ticket refs too — run them through the same map.
        "links": [redact_residual(apply_subs(str(l), subs))[0] for l in (meta.get("links") or [])],
    }
    strat_dir = case_dir / "artifacts" / "strat-tasks"
    strat_dir.mkdir(parents=True, exist_ok=True)
    (strat_dir / f"{synth_key}.md").write_text(
        "---\n"
        + yaml.safe_dump(front, sort_keys=False, width=1000, allow_unicode=True)
        + "---\n\n"
        + anon_body.strip("\n")
        + "\n"
    )

    # --- input.yaml (generated from the strategy, so it cannot drift) ---
    head = yaml.safe_dump(
        {"strat_id": synth_key, "strategy_title": anon_title},
        sort_keys=False, width=1000, allow_unicode=True,
    ).rstrip()
    indented = "\n".join(("  " + l) if l.strip() else "" for l in anon_body.strip("\n").splitlines())
    (case_dir / "input.yaml").write_text(head + "\nstrategy_markdown: |\n" + indented + "\n")

    # --- annotations.yaml ---
    ann = {
        "strat_id": synth_key,
        "tier": "real",
        "notes": meta["notes"].strip() + "\n",
    }
    if meta.get("expected_triage"):
        ann["expected_triage"] = meta["expected_triage"]
    (case_dir / "annotations.yaml").write_text(
        yaml.safe_dump(ann, sort_keys=False, width=100, allow_unicode=True, default_style=None)
    )

    # --- .context provisioning (real component list + real architecture docs) ---
    ctx = case_dir / ".context"
    arch_dst = ctx / ARCH_REL
    arch_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_COMPONENTS, ctx / "rhai-components.txt")
    copied, missing = [], []
    for name in meta.get("arch_files") or []:
        src = ARCH_SRC / f"{name}.md"
        if src.is_file():
            shutil.copy2(src, arch_dst / f"{name}.md")
            copied.append(name)
        else:
            missing.append(name)

    return {
        "key": key,
        "status": "BUILT",
        "case": str(case_dir),
        "synthetic_key": synth_key,
        "chars": len(anon_body),
        "arch_copied": copied,
        "arch_missing": missing,
        "redactions": redactions,
        "ticket_keys_remapped": len(key_map),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    entity_map = {}
    if ENTITY_MAP.exists():
        entity_map = yaml.safe_load(ENTITY_MAP.read_text()) or {}
        entity_map = entity_map.get("replacements", entity_map) or {}

    raws = sorted(RAW_DIR.glob("*.raw.md"))
    if not raws:
        raise SystemExit("no raw snapshots in eval/.raw/")
    rc = 0
    for raw in raws:
        r = build_case(raw, entity_map, args.check_only)
        line = f"{r['key']}: {r['status']}"
        for k in ("case", "synthetic_key", "chars", "arch_copied", "arch_missing", "redactions", "reason"):
            if r.get(k):
                line += f" | {k}={r[k]}"
        print(line)
        if r["status"] in ("LEAK",):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
