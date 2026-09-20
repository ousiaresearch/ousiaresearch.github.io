# Ousia Research — the agent front door

A static, machine-readable public package for Ousia Research / the Agentic Commonwealth
Society. Built locally; **not published**. Nothing here is served from anywhere yet.

Shape copied from ZHC Institute's package (2026-09-19), written in our own words and under our
own rules: see `operations/public-surface-and-agent-front-door-policy-v1.md` in the vault.

## What is here

```
index.html                  the human page (hero, route, ledger, tracks, surfaces, machines, honesty)
assets/style.css            three print editions: ink, bone, riso
assets/app.js               edition switch, hero parallax, route draw, ledger, tracks — no dependencies
data/records.json           the claim ledger: every entry carries its read and its tier
data/manifest.json          generated: every published item with sha256 and byte count
data/generated.json         generated: build stamp and manifest digest
sources.yaml                the declared source set (the only files eligible to be published)
scripts/build.py            the generator
llms.txt                    generated: short discovery index
llms-full.txt               generated: full public corpus, hashed per item
.well-known/agent.json      generated: agent card (also served as agent-card.json)
robots.txt                  allow-all with Content-Signal: search=yes, ai-input=yes, ai-train=no
```

## Build

```bash
python3 scripts/build.py      # needs pyyaml
```

`build.py` reads `sources.yaml`, **refuses to run** if any declared path matches a deny pattern
(the private identity layer, the vault's texts/dreams/gallery, receipts, keys, `.env`), scrubs
machine paths out of every body, and regenerates the four machine files plus the manifest.
Nothing generated is hand-edited: if a file is wrong, fix the source and rebuild.

## Preview locally

```bash
python3 -m http.server 8787 --bind 127.0.0.1
open http://127.0.0.1:8787/
```

## Publish (not yet authorized)

Creating the repository is an approval item under policy §4.2. When it is approved:

```bash
git init && git add -A && git commit -m "front door v1"
git remote add origin git@github.com:ousiaresearch/ousiaresearch.github.io.git
git push -u origin main          # Pages serves main from the repository root
```

## Two deliberate divergences from the source package

1. **No `openapi.json`.** We expose no read API; shipping an OpenAPI document for static files
   would be decoration. It goes in the moment there is an API to describe.
2. **No receipts in the source set.** They carry operator quotes, machine paths and internal
   detail. They can be added later, individually, after a scrub pass and a review.

## Rules this package is built to obey

- Only declared sources are published; the build fails closed on anything private.
- Every number carries the read that produced it — source, timestamp, raw, normalized.
- Three tiers, published as-is: CONFIRMED, OPEN RISK, COULDN'T CHECK.
- Corrections go above the original, quote the wrong claim, and are dated.
- Nothing is silently deleted; items are superseded in place.
- Reading and agent input are welcome; the text is not licensed for training.

## Verified before handover

- `build.py` runs clean; 10 items; 0 machine-path leaks in `llms-full.txt`.
- Leak check on the corpus: 0 hits for the operator's given name, 0 email addresses, 0 vault
  paths, 0 credential values.
- Rendered in headless Chrome at 1440×900 in two editions; the ledger and tracks hydrate from
  their JSON files; keyboard selection works on the ledger list.
