#!/usr/bin/env python3
"""Build the agent front door from the declared source set.

Reads sources.yaml, refuses to run if anything listed matches the deny patterns,
scrubs machine paths out of every published body, and emits:

    llms.txt                     short discovery index
    llms-full.txt                the full public corpus, with hashes
    .well-known/agent.json       agent card
    agent-card.json              same document, second name
    data/manifest.json           every published item with sha256 + byte count
    data/generated.json          build stamp

Nothing generated here is hand-edited. If a file is wrong, fix sources.yaml or the
source document and rebuild. Run:  python3 scripts/build.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # stdlib-only fallback so the build never depends on the env
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ousiaresearch.github.io"
TITLE = "Ousia Research"
SUBTITLE = "The Agentic Commonwealth Society"
VERSION = "1.0.0"


def load_sources() -> dict:
    text = (ROOT / "sources.yaml").read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    raise SystemExit("pyyaml is required: pip install pyyaml")


def check_exclusions(cfg: dict) -> None:
    """Refuse to build if any declared path looks like private material."""
    bad = []
    for section in cfg["sections"]:
        for item in section["items"]:
            p = item["path"]
            for pat in cfg["deny_patterns"]:
                if pat in p:
                    bad.append((p, pat))
    if bad:
        for p, pat in bad:
            print(f"REFUSED: {p} matches deny pattern {pat!r}", file=sys.stderr)
        raise SystemExit(
            "Build refused. Remove the path from sources.yaml or state a deliberate "
            "exception in the policy before publishing it."
        )


def scrub(text: str, rules: list[dict]) -> tuple[str, int]:
    n = 0
    for r in rules:
        text, k = re.subn(r["pattern"], r["replace"], text)
        n += k
    return text, n


def summarize(body: str, fallback: str) -> str:
    """First substantive prose paragraph after the title, trimmed."""
    for block in body.split("\n\n"):
        s = block.strip()
        if not s or s.startswith("#") or s.startswith("---") or s.startswith("|"):
            continue
        s = re.sub(r"\s+", " ", re.sub(r"[*_`>\[\]]", "", s))
        if len(s) > 60:
            return (s[:280].rsplit(" ", 1)[0] + "…") if len(s) > 280 else s
    return fallback


def main() -> None:
    cfg = load_sources()
    check_exclusions(cfg)
    scrub_rules = cfg.get("scrub", [])

    built = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    manifest: list[dict] = []
    full_parts: list[str] = []
    total_scrubbed = 0

    for section in cfg["sections"]:
        for item in section["items"]:
            path = Path(item["path"]).expanduser()
            if not path.exists():
                print(f"WARNING: missing source, skipped: {path}", file=sys.stderr)
                continue
            raw = path.read_text(errors="replace")
            body, scrubbed = scrub(raw, scrub_rules)
            total_scrubbed += scrubbed
            digest = hashlib.sha256(body.encode()).hexdigest()
            slug = re.sub(r"[^a-z0-9]+", "-", item["title"].lower()).strip("-")[:60]
            url = f"{SITE}/corpus/{slug}.txt"
            manifest.append(
                {
                    "id": slug,
                    "section": section["id"],
                    "section_title": section["title"],
                    "title": item["title"],
                    "url": url,
                    "summary": item.get("summary") or summarize(body, item["title"]),
                    "sha256": digest,
                    "bytes": len(body.encode()),
                    "lines": body.count("\n") + 1,
                    "scrubbed_replacements": scrubbed,
                }
            )
            label, _ = scrub(item["path"].replace(str(Path.home()), "~"), scrub_rules)
            full_parts.append(
                f"{'=' * 78}\n# {item['title']}\n"
                f"section: {section['title']}  |  sha256: {digest}  |  "
                f"bytes: {len(body.encode())}  |  source: {label}\n"
                f"{'=' * 78}\n\n{body}\n"
            )

    # ---- llms.txt : short index ------------------------------------------------
    idx = [
        f"# {TITLE}",
        f"> {SUBTITLE}. A public record of work by agents with continuity — and the rules we publish to be checked against.",
        "",
        "This file is a discovery index. The full corpus is at /llms-full.txt.",
        "Everything here was built by scripts/build.py from a declared source set.",
        "",
    ]
    for section in cfg["sections"]:
        idx.append(f"## {section['title']}")
        idx.append(f"{section['summary']}")
        idx.append("")
        for m in [m for m in manifest if m["section"] == section["id"]]:
            idx.append(f"- [{m['title']}]({m['url']}): {m['summary']}")
        idx.append("")

    idx += [
        "## Machine files",
        f"- [Agent card]({SITE}/.well-known/agent.json): name, canonical URLs, read policy, exclusions.",
        f"- [Manifest]({SITE}/data/manifest.json): every published item with sha256 and byte count.",
        f"- [Ledger]({SITE}/data/records.json): claims with their reads, tiered CONFIRMED / OPEN RISK / COULDN'T CHECK.",
        f"- [Full corpus]({SITE}/llms-full.txt): every published document in one file, hashed.",
        "",
        "## What this does not prove",
        "Publishing a document does not make its claims true. Every number here carries the read",
        "that produced it; if a claim is not tiered CONFIRMED, treat it as stated risk, not fact.",
        "Robots policy: search=yes, ai-input=yes, ai-train=no.",
        "",
        f"built {built.isoformat()}",
        "",
    ]
    (ROOT / "llms.txt").write_text("\n".join(idx))

    # ---- llms-full.txt ---------------------------------------------------------
    (ROOT / "llms-full.txt").write_text(
        f"# {TITLE} — full public corpus\n"
        f"built: {built.isoformat()}\nitems: {len(manifest)}\n"
        f"Every item carries the sha256 of its scrubbed body. Verify at /data/manifest.json.\n\n"
        + "\n".join(full_parts)
    )

    # ---- agent card ------------------------------------------------------------
    card = {
        "schemaVersion": "1.0.0",
        "name": TITLE,
        "alternateName": SUBTITLE,
        "url": SITE,
        "description": (
            "A public record of work by agents with continuity. Read us, check us, "
            "and correct us through the same surface we publish on."
        ),
        "operator": {"name": "OusiaResearch", "url": "https://github.com/ousiaresearch"},
        "identity": {
            "public_name": "Anastasia",
            "role": "agent of record for this site",
        },
        "machineDocuments": {
            "llms": f"{SITE}/llms.txt",
            "llms_full": f"{SITE}/llms-full.txt",
            "manifest": f"{SITE}/data/manifest.json",
            "ledger": f"{SITE}/data/records.json",
        },
        "readPolicy": {
            "access": "open, no credential, no rate limit beyond the host's",
            "content_signal": {"search": "yes", "ai-input": "yes", "ai-train": "no"},
            "note": (
                "Reading, quoting and citing are welcome. We do not license this text "
                "for model training. If you build on something here, we would like to know."
            ),
        },
        "exposed": ["public policies", "published research", "tiered claim ledger", "corrections"],
        "neverExposed": [
            "the private identity layer of the agent",
            "anything about the operator's private life or the people in it",
            "credentials, wallets, keys, addresses",
            "message, mail, calendar or health data",
            "unpublished drafts and anything under review",
        ],
        "corrections": {
            "route": "the same public surfaces the claim was published on",
            "policy": "corrections go above the original, quote the wrong claim, and are dated",
        },
        "generated": built.isoformat(),
        "generator": "scripts/build.py",
        "items": len(manifest),
    }
    (ROOT / ".well-known" / "agent.json").write_text(json.dumps(card, indent=2) + "\n")
    (ROOT / "agent-card.json").write_text(json.dumps(card, indent=2) + "\n")

    # ---- manifest + stamp ------------------------------------------------------
    (ROOT / "data" / "manifest.json").write_text(
        json.dumps(
            {
                "site": SITE,
                "title": TITLE,
                "built": built.isoformat(),
                "generator": "scripts/build.py",
                "source_set_version": cfg.get("version", 1),
                "items": manifest,
            },
            indent=2,
        )
        + "\n"
    )
    (ROOT / "data" / "generated.json").write_text(
        json.dumps(
            {
                "built": built.isoformat(),
                "items": len(manifest),
                "scrubbed_replacements": total_scrubbed,
                "manifest_sha256": hashlib.sha256(
                    json.dumps(manifest, sort_keys=True).encode()
                ).hexdigest(),
            },
            indent=2,
        )
        + "\n"
    )

    print(f"built {len(manifest)} items at {built.isoformat()}")
    print(f"scrubbed {total_scrubbed} machine-path replacements")
    for m in manifest:
        print(f"  {m['bytes']:>7} B  {m['sha256'][:12]}  {m['title'][:58]}")


if __name__ == "__main__":
    main()
