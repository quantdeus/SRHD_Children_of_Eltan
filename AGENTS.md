# AGENTS.md — QuantDeus Eltan Squad

## Product

This repository is the canonical codebase for the QuantDeus product **«Дети Эльтана»**, a mod for Space Rangers 2 / Space Rangers HD.

Canonical product branch: `master`.

Cross-project coordination source of truth: `quantdeus/quantdeus.github.io`.
Code, mod artifacts and product evidence for Eltan remain in this repository.

## Required reading

Before any change read:

1. `README.md`
2. `docs/PROJECT_CONSTITUTION.md`
3. `docs/MOD_ARCHITECTURE.md`
4. `docs/ROADMAP.md`
5. `docs/AGENT_DEVELOPMENT_LOOP.md`
6. the relevant capability/evidence documents for the target mechanic
7. latest `master` and any open PR touching the same surface

## QuantDeus squad roles

The Eltan squad is composed from the existing QuantDeus agent registry; it does **not** create new canonical agents.

- **Seven of Nine** — coordinator; decomposes work and prevents duplicate branches/tasks.
- **Sherlock** — modding/API/evidence investigation.
- **Tuvok** — constraints, engine assumptions, reproducibility and logic review.
- **Scout / Verifier / Analyst / Strategist / Guardian** — inspect, verify feasibility, scope risk and choose one bounded implementation.
- **Task Smith** — implementation on an isolated branch.
- **Archivist / Herald** — evidence, changelog and PR handoff.
- **QA Syntax / QA Contract / QA Repair** — validation and repair loop.
- **Synthesis** — UI, writing and presentation consistency when a task actually requires it.
- **Unity/Growth** — contributor-facing work only when explicitly requested.

## Execution contract

One agent run = at most one small, coherent, reviewable result.

Preferred outcomes:

- one verified modding capability;
- one bug fix;
- one quest/event increment;
- one data/validation tool;
- one bounded mechanic slice;
- one evidence-backed integration experiment.

Never implement an entire campaign, diplomacy system, second galaxy or Keller arc in one run.

## Mod-first rule

Before coding classify the requested capability as one of:

- native reuse;
- supported extension;
- tool-assisted extension;
- unverified;
- unsupported.

If the path is unverified, the result of the run is research/evidence — not invented working game code.

## Cross-repository references

`quantdeus/deti_eltan` may be used as a **reference and experiment source**, especially for native adapter, two-arm transit and tooling work.

Do not copy code or assets blindly. Record the exact source commit and verify licensing/provenance before importing third-party-derived material.

`quantdeus/quantdeus.github.io` is the Control Tower for product tasks and swarm coordination. A Control Tower Issue must point back to the concrete branch/PR/artifact in this repository.

## Testing truth

Never claim a mechanic works in-game unless it was actually run in SRHD.

Always state the highest verification level reached:

- static/source validation;
- toolchain/build validation;
- real game smoke.

If the environment cannot run the game or proprietary build tools, stop at the highest honest level and leave an exact manual test handoff.

## Safety / repository rules

- no proprietary game binaries/assets in commits;
- no third-party mod material without verified permission/license;
- no automatic edits to a user's game installation;
- no release/publication from an agent task without explicit human approval;
- do not rewrite `master` history;
- do not duplicate an open PR solving the same problem.

## Current priority

Finish existing reviewable work before starting large new systems.

The first active review target is PR #4 (two-arm race identity overlay). Its GitHub gates are green, but real RScript/BlockPar packaging and manual SRHD smoke are still required before it can be treated as gameplay-verified.
