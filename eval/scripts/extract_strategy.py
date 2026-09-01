#!/usr/bin/env python3
"""Extract a RHAISTRAT strategy verbatim from an auto-saved MCP tool result.

The Atlassian MCP saves oversized responses to a file instead of returning
them inline.  Requesting `fields: ["*all"]` reliably triggers that, which
lets us pull the description VERBATIM with no LLM in the fidelity path.

Writes ``eval/.raw/<KEY>.raw.md`` (git-ignored): YAML header with the
selection metadata, then the untouched description body.

Usage:
    python3 eval/scripts/extract_strategy.py <tool-result.json> [...]
"""

import json
import re
import sys
from pathlib import Path

import yaml

RAW_DIR = Path("eval/.raw")


def extract(path):
    data = json.loads(Path(path).read_text())
    nodes = data.get("issues", {}).get("nodes") or []
    if not nodes:
        raise SystemExit(f"{path}: no issues in payload")
    out = []
    for node in nodes:
        f = node["fields"]
        desc = f.get("description") or ""
        if not desc.strip():
            print(f"  WARNING: {node['key']} has an empty description", file=sys.stderr)
        effort = ""
        m = re.search(r"### Effort Estimate\s*\n+\*\*([^*]+)\*\*", desc)
        if m:
            effort = m.group(1).strip()
        header = {
            "real_key": node["key"],
            "summary": f.get("summary", ""),
            "components": [c["name"] for c in (f.get("components") or [])],
            "priority": (f.get("priority") or {}).get("name", ""),
            "status": (f.get("status") or {}).get("name", ""),
            "labels": sorted(f.get("labels") or []),
            "effort_estimate": effort,
            "desc_chars": len(desc),
            "hlr_count": len(re.findall(r"\\?\[P[012]\\?\]", desc)),
            # Deterministic PII probes — the LLM pass double-checks semantics.
            "probe_emails": len(re.findall(r"[\w.+-]+@[\w.-]+\.\w+", desc)),
            "probe_jira_urls": len(
                re.findall(r"https://[\w.-]*atlassian\.net/browse/[A-Z]+-\d+", desc)
            ),
            "probe_other_hosts": sorted(
                set(re.findall(r"https?://([\w.-]+)", desc))
                - {"redhat.atlassian.net", "github.com", "docs.redhat.com"}
            ),
            "probe_ticket_keys": sorted(set(re.findall(r"\b[A-Z][A-Z0-9]+-\d+\b", desc))),
        }
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        dest = RAW_DIR / f"{node['key']}.raw.md"
        dest.write_text(
            "---\n"
            + yaml.safe_dump(header, sort_keys=False, width=1000, allow_unicode=True)
            + "---\n\n"
            + desc.rstrip("\n")
            + "\n"
        )
        out.append((node["key"], header))
        print(
            f"{node['key']}: {header['desc_chars']} chars, {header['hlr_count']} HLRs, "
            f"effort={header['effort_estimate'] or '?'}, "
            f"emails={header['probe_emails']} jira_urls={header['probe_jira_urls']} "
            f"other_hosts={header['probe_other_hosts']} "
            f"refs={[k for k in header['probe_ticket_keys'] if not k.startswith('HLR')][:6]}"
        )
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        extract(p)
