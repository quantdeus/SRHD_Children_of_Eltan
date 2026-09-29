# Toolchain Reference Bridge — canonical Eltan ↔ deti_eltan

Tracks QuantDeus Control Tower Issue:
https://github.com/quantdeus/quantdeus.github.io/issues/234

## Purpose

This document records what the canonical **Children of Eltan** repository can
safely learn from `quantdeus/deti_eltan` without pretending that the two
repositories are interchangeable.

Canonical product repository:

- `quantdeus/SRHD_Children_of_Eltan`
- canonical branch: `master`

Engineering/reference fork inspected:

- `quantdeus/deti_eltan`
- inspected commit: `149da8985709f285cebf053cb7aef1c1555c5bfe`

The reference fork is evidence and tooling research. It is **not** automatically
the canonical shipping tree.

## Verified reference facts

### Build and test levels

The reference fork documents three explicit verification levels in
`docs/TESTING.md`:

1. **Level 1 — Python/data**
   - `python -m unittest discover -s tools/tests -t .`
   - `python tools/validate_content.py`
   - does not require an installed game.

2. **Level 2 — module build**
   - uses local/non-repository tools under `references/tools/`;
   - RScript 4.10f compiles `.rson` to `.scr`;
   - BlockParEditor 1.9 produces the game's BlockPar data;
   - LLVM-MinGW is required for the PE32 native adapter;
   - the reference command is `.\tools\build-game-smoke.ps1`.

3. **Level 3 — real game smoke**
   - requires an installed Space Rangers HD;
   - dry run:
     `.\tools\install-game-smoke.ps1 -GameRoot '<game>'`;
   - install:
     `.\tools\install-game-smoke.ps1 -GameRoot '<game>' -Install`;
   - the game must be launched through the mod launcher when the native adapter
     is part of the test.

These levels are useful as a **verification model** for the canonical repository
even when the scripts themselves are not imported.

### Steam and Universe compatibility

The reference README and `docs/TESTING.md` state that native-adapter changes
must be checked on both the stock Steam engine and the patched Universe engine.

The reference testing notes record defects that appeared on only one engine
variant, so "works on one executable" is not sufficient evidence for native
adapter work.

Canonical rule derived from that evidence:

> Any future canonical native-adapter change must name which engine build was
> tested. Adapter work is not release-ready until both supported engine paths
> have evidence or one path is explicitly removed from the support contract.

### Script-size constraint

The reference testing notes record a compiled script at 60,972 bytes against a
65,536-byte engine ceiling.

Canonical rule:

- record compiled `.scr` size whenever RScript output changes materially;
- treat the engine ceiling as a hard compatibility gate;
- do not infer safe headroom from source character count alone.

### BlockPar comparison

The reference testing notes report that BlockPar output is not byte-stable
between equivalent runs.

Canonical rule:

- do not use binary equality of generated `.dat` files as the semantic
  regression test;
- compare size plus decoded textual/structural content using a verified
  decoder/tool path.

## Two-arm transit and native adapter evidence

The reference fork contains working/research surfaces for:

- a native second-map adapter;
- stash/fetch transfer of player state;
- Steam/Universe engine-address handling;
- inter-arm transition scripts;
- a launcher/injection path.

PR #4 in this repository already pins selected files from
`deti_eltan@149da8985709f285cebf053cb7aef1c1555c5bfe` by SHA-256 before preparing
its race-identity source overlay.

That is the correct integration pattern for experimental cross-repository work:

1. pin an exact commit;
2. pin exact file hashes where transformation depends on integration points;
3. refuse to run if the reference changed;
4. write output to a fresh disposable tree;
5. never mutate the reference checkout automatically;
6. distinguish source/static validation from real-game validation.

## What is safe to reuse now

The following may be reused as **knowledge, protocol or independently
reimplemented logic** with source attribution:

- the three-level testing model;
- the requirement to test native adapter changes on Steam + Universe;
- the concept of pinning reference files before applying a transform;
- dry-run-before-install behavior;
- refusal to overwrite an existing installed mod directory;
- separation of source, build output and game installation;
- exact test observations and engine constraints when cited to their source
  commit/file.

Documentation may link to the reference repository and commit rather than
copying its implementation.

## What must NOT be copied blindly

### Third-party-derived tools

The reference repository's `docs/AGENT_COORDINATION.md` contains a human-sync
warning that:

- `tools/srgi.py` and `tools/srpkg.py` are copies from
  `ArtYudin89/rson-decompiler`;
- `tools/srblockpar.py` is adapted from that project;
- the upstream was placed under GNU GPL v3;
- the reference repository itself had no project-wide licence decision recorded
  at that point.

Therefore those files must **not** be copied into the canonical Eltan repository
until the licence/provenance path is reviewed and the canonical repository's
licensing choice is compatible.

### Proprietary/local build tools

Do not commit:

- RScript executable;
- BlockParEditor executable;
- game binaries;
- engine executables/DLLs;
- proprietary game assets copied from an installation.

The repository may document how a user-supplied legal installation/tool path is
used.

### Reference mod assets/code

Do not import code, data, text or art from third-party mods merely because the
reference fork can inspect or use them.

Mechanic evidence can inform an original implementation; redistribution rights
must be established separately.

## Canonical implementation guidance

### Near term

The canonical repository should adopt the **verification contract** before
adopting the reference implementation wholesale:

1. define Level 1 checks that run in public CI;
2. document Level 2 requirements without checking proprietary tools into Git;
3. provide a Level 3 manual smoke template for the machine with SRHD;
4. record Steam/Universe coverage for native changes;
5. keep build output separate from `master` source.

### For PR #4

PR #4 is a source overlay, not an installed mod change.

Its current truthful status is:

- repository gates: passed;
- source/static overlay tests: passed according to PR evidence;
- pinned reference commit: current at the time of this audit;
- RScript/BlockPar package build: still required;
- live SRHD smoke: still required.

See Control Tower task #233 for the exact game-machine handoff.

### For future transit work

The known return/hyperspace-loop defects in the reference fork should be handled
as a separate bounded defect spike, not silently mixed into PR #4.

Control Tower task:
https://github.com/quantdeus/quantdeus.github.io/issues/235

## Evidence index

- Canonical project rules:
  - `README.md`
  - `docs/PROJECT_CONSTITUTION.md`
  - `docs/MOD_ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- Canonical experimental integration:
  - PR #4 — two-arm race identity overlay
- Reference repository:
  - `quantdeus/deti_eltan@149da8985709f285cebf053cb7aef1c1555c5bfe`
  - `README.md`
  - `docs/TESTING.md`
  - `docs/AGENT_COORDINATION.md`

## Decision

Use `deti_eltan` as a pinned evidence/toolchain laboratory.

Do **not** make it the canonical product branch, and do not bulk-import its
implementation. Port one bounded capability at a time only after technical,
provenance and verification gates are explicit.
