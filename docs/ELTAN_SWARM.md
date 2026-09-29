# QuantDeus Eltan Swarm

## Mission

Turn **«Дети Эльтана»** into a continuously developed QuantDeus product while preserving the mod-first architecture and evidence rules of this repository.

## Architecture

```text
QuantDeus Control Tower
quantdeus/quantdeus.github.io Issues
        ↓
Seven of Nine / OpenClaw
        ↓
specialist agent role
        ↓
quantdeus/SRHD_Children_of_Eltan branch / PR
        ↓
Eltan GitHub gates
        ↓
manual SRHD gate when required
        ↓
review / merge
```

## Product repositories

### Canonical shipping repository

`quantdeus/SRHD_Children_of_Eltan`

- canonical branch: `master`;
- canonical product: Space Rangers 2 / Space Rangers HD mod;
- code, mod content and release evidence belong here.

### Engineering reference / experimental fork

`quantdeus/deti_eltan`

Useful evidence includes:

- two-arm transit experiments;
- native adapter work;
- SRHD/Universe compatibility findings;
- build/test tooling;
- game-machine testing notes.

It is a reference source, not an automatic replacement for the canonical product repository.

## Current execution lanes

### Lane A — finish existing increments

PR #4: two-arm race identity overlay.

Current verified state:

- source/static tests: passed;
- repository GitHub gates: passed;
- PR is mergeable;
- RScript/BlockPar build: not yet verified in this PR;
- live SRHD smoke: not yet verified.

Do not mark gameplay complete until the missing levels are executed.

### Lane B — core stability

Highest-value technical targets:

1. confirmed install/build pipeline for the canonical mod;
2. bidirectional inter-arm transit;
3. hyperspace-loop/load ownership defects;
4. save/state integrity across arm transitions;
5. Steam + Universe compatibility for native-adapter changes.

### Lane C — vertical slice

After the technical path is confirmed:

1. one start hook;
2. one character/contact;
3. one quest chain;
4. one item/equipment/content addition;
5. one real faction/reputation consequence.

### Lane D — system extensions

Only after earlier gates are healthy:

- Smart Diplomacy slice;
- alliance/reputation consequences;
- deep hyperspace;
- black-hole/shadow-world content;
- Keller story/mechanics;
- wider faction simulation.

## Definition of progress

Progress means a linked artifact: commit, branch, PR, test result, reproducible research note or real-game smoke evidence.

An Issue comment saying that work is planned is not progress.

## Handoff format

Every agent handoff must include:

- target Control Tower Issue;
- target repository;
- branch/PR;
- changed files;
- verification level reached;
- exact unverified gap;
- next bounded step.
