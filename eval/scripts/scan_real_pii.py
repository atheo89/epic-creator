#!/usr/bin/env python3
"""PII / leak scanner for the committed eval dataset.

Deterministic gate that runs over everything under ``eval/cases`` and
``eval/shared``.  Complements the LLM audit pass, which catches semantic
identifiers (customer prose, individuals) that regexes cannot.

Checks:
  1. email addresses
  2. URLs pointing at non-public hosts (internal wikis, Slack, Drive, Jira)
  3. real-range ticket keys — anything below the synthetic 7000 floor
  4. verbatim originals from the git-ignored entity map
  5. leftover «TOKEN» placeholders from the anonymization pass
  6. local filesystem paths and usernames

Exit code 1 if any finding.  Usage:
    python3 eval/scripts/scan_real_pii.py [--map eval/.entity-map.yaml]
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCAN_ROOTS = [Path("eval/cases"), Path("eval/shared")]
SYNTHETIC_FLOOR = 7000
SYNTHETIC_CEILING = 9999
PUBLIC_HOSTS = {"github.com", "docs.redhat.com", "www.redhat.com", "access.redhat.com"}
PUBLIC_SUFFIXES = (".github.io", ".nist.gov", ".kubernetes.io", ".openshift.io", ".readthedocs.io")
# Only these prefixes are real Jira projects.  Everything else that matches the
# key shape is a technical identifier (SHA-256, AES-256, KEM-768, AC-2, OCP-5)
# and must be left alone — rewriting those corrupts the strategy content.
JIRA_PREFIXES = {
    "RHAISTRAT", "RHAIRFE", "RHOAIENG", "RHOAIUX", "AIPCC", "RHAI", "RHAIC",
    "RHAICI", "RHAIFIRST", "INFERSUP", "OCPSTRAT", "OCPBUGS", "RHOAI",
    "KFLUXBUGS", "PSASTRAT", "RHELMISC", "RHELPLAN", "RFE",
}

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
URL = re.compile(r"https?://([\w.-]+)[^\s)\]\"']*")
TICKET = re.compile(r"\b([A-Z][A-Z0-9]{2,})-(\d+)\b")
TOKEN = re.compile(r"«[^»]+»")
LOCALPATH = re.compile(r"/Users/[\w.-]+|/home/[\w.-]+|C:\\Users\\[\w.-]+")
# HLR-1 / P0 style markers are not ticket keys.
NOT_TICKETS = {"HLR", "P0", "P1", "P2", "TL", "AGPL", "GPL", "FIPS", "CSV", "API"}


def scan(map_path):
    originals = []
    if map_path and Path(map_path).exists():
        data = yaml.safe_load(Path(map_path).read_text()) or {}
        originals = [o for o in (data.get("replacements") or data) if isinstance(o, str) and len(o) > 3]

    findings = []
    files = [p for root in SCAN_ROOTS if root.exists() for p in root.rglob("*") if p.is_file()]
    for p in files:
        try:
            text = p.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        # Files under .context/ are vendored verbatim from the PUBLIC
        # architecture-context repo.  Their URLs and identifiers are upstream
        # content, not ours to rewrite — but they must stay consistent with our
        # entity map, so an original surfacing there means we over-anonymized
        # a public name in the strategy body.
        vendored = ".context/" in str(p)
        for m in EMAIL.finditer(text):
            findings.append((p, "email", m.group(0)))
        for original in originals:
            if original in text:
                kind = "over-anonymized-public-name" if vendored else "entity-map-original"
                findings.append((p, kind, original[:40]))
        if vendored:
            continue
        for m in URL.finditer(text):
            host = m.group(1)
            if host not in PUBLIC_HOSTS and not host.endswith(PUBLIC_SUFFIXES):
                findings.append((p, "non-public-url", m.group(0)[:70]))
        for m in TICKET.finditer(text):
            prefix, num = m.group(1), int(m.group(2))
            if prefix not in JIRA_PREFIXES:
                continue
            # Anything outside the synthetic band is a real key.  Checking only
            # `< 7000` would miss high-numbered real issues (e.g. FOO-34693).
            if not (SYNTHETIC_FLOOR <= num <= SYNTHETIC_CEILING):
                findings.append((p, "real-range-ticket", m.group(0)))
        for m in TOKEN.finditer(text):
            findings.append((p, "unresolved-token", m.group(0)))
        for m in LOCALPATH.finditer(text):
            findings.append((p, "local-path", m.group(0)))

    print(f"scanned {len(files)} files under {', '.join(str(r) for r in SCAN_ROOTS)}")
    if not findings:
        print("CLEAN: no PII, internal links, real ticket keys, or unresolved tokens")
        return 0
    print(f"FINDINGS: {len(findings)}")
    for p, kind, sample in findings[:60]:
        print(f"  {kind}: {p} :: {sample}")
    if len(findings) > 60:
        print(f"  ... and {len(findings) - 60} more")
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default="eval/.entity-map.yaml")
    args = ap.parse_args()
    sys.exit(scan(args.map))
