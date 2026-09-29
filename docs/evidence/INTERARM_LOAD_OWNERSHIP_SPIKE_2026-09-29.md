# Inter-arm Load Ownership Spike — 2026-09-29

Tracks QuantDeus Control Tower Issue:
https://github.com/quantdeus/quantdeus.github.io/issues/235

## Scope

Investigate two symptoms documented by the current reference implementation:

1. return to the first arm may stall near the end of `GameLoad`;
2. hyperspace transitions after an inter-arm jump may loop.

This document is a **source-level defect spike**, not a claim that the defect is
fixed in-game.

## Evidence baseline

Reference repository:

- `quantdeus/deti_eltan`
- pinned commit:
  `149da8985709f285cebf053cb7aef1c1555c5bfe`

Primary files inspected:

- `src/engine_adapter/ce_second_map_adapter.c`
- `src/scripts/CE_MapSmoke.rson`
- `README.md`
- `docs/TESTING.md`

No proprietary game binary was inspected or committed by this spike.

## Confirmed transition sequence

The current RScript Turn path does the following:

1. polls `CEAdapterConsumePendingArrival()` **before** it considers completing
   the currently registered portal;
2. once the ship is no longer in the hole, calls
   `CEAdapterCompleteRegisteredPortal(...)`;
3. on success, calls `CEAdapterArmPendingArrival(targetArm)`;
4. requests `FormChange('GameLoad')`.

That ordering is intentional. Comments in the reference source record that
polling after the arming block caused the pending arrival to be repeatedly
re-armed and never consumed.

## Load-result hook is functional, not diagnostic

`CEAdapterInstallLoadGameDiagnostics` installs a hook around the engine's
`LoadGame` call.

The reference source explicitly records that an in-game `GameLoad` can finish
its progress bar with no next form queued. The hook's result body therefore
forces `StarMap` **only when the load is recognized as an Eltan portal load**.

This behavior is required for the current load-based inter-arm design.

## Primary state variable: `g_ce_portal_load_pending`

At the inspected commit, this variable has exactly three source occurrences:

1. declaration, initialized to `0`;
2. set to `1` inside `CEAdapterCompleteRegisteredPortal` after the target
   load path has been prepared;
3. consumed/reset with
   `InterlockedExchange(&g_ce_portal_load_pending, 0)` inside
   `ce_loadgame_result_body`.

There is no separate reset occurrence in the inspected source.

### Why that matters

If the path after setting the flag fails or diverges **before the hooked
LoadGame result body consumes it**, the DLL can retain a stale
`portal_load_pending=1`.

The next unrelated LoadGame that does reach the hook can then be misclassified
as an Eltan portal load and have its next form forced to `StarMap`.

The reference source itself contains a comment beside that forced-form logic
saying that the hyperspace-loop problem it was intended to avoid is a
**stale pending flag** problem.

## Secondary state: pending arrival

The same lifecycle asymmetry exists for:

- `g_ce_pending_arrival_direction`
- `g_ce_pending_arrival_ticks`

At the inspected commit:

- direction starts at `-1`;
- `CEAdapterArmPendingArrival` sets it to entering/returning;
- `CEAdapterConsumePendingArrival` is the normal path that returns it to
  `-1`;
- no other reset occurrence was found for the direction.

The external-reload recovery currently resets several portal/galaxy globals,
including portal status/hole/galaxy pointer and active arm, but the inspected
reset block does not reset either the portal-load pending flag or pending-arrival
direction/ticks.

## Falsifiable root-cause hypothesis

> An interrupted, failed, external or otherwise non-standard load path can leave
> Eltan's load-ownership and/or pending-arrival state armed after the transition
> that created it is no longer valid. A later load/hyperspace lifecycle then
> consumes stale transition state, producing a wrong follow-up form, wrong arm
> publication, or repeated transition behavior.

This hypothesis is intentionally narrower than "the loader is broken".

It predicts observable log/state behavior.

## Reproduction / instrumentation plan

Use a Windows machine with the reference build tools and installed SRHD.

### Logging evidence required

Capture a fresh `C:\ce_debug\live-arm-switch.jsonl` for each scenario.

The log already records `loadgame-result` with:

- `ok`
- `galaxy`
- `portal_pending`
- `queued_starmap`
- `previous_form`
- `tick`

### Scenario A — successful enter

1. clear/rotate old debug logs;
2. enter the Second Home normally;
3. locate the Eltan `portal-load-prepared` record;
4. require the corresponding `loadgame-result` to report
   `portal_pending:1` exactly once;
5. after arrival, perform an ordinary save/load;
6. require that ordinary load to report `portal_pending:0`.

### Scenario B — successful return

Repeat the same sequence from Second Home to the first arm.

If the return stalls, preserve the final 100 log records and note whether a
`loadgame-result` record appears at all.

- **No result record after `portal-load-prepared`** supports the hypothesis
  that ownership state can remain armed because the result hook was not reached.
- **Result record with `portal_pending:1` and no usable next form** moves the
  root cause downstream from flag consumption.

### Scenario C — interrupted / failed transition

Force one safely reproducible aborted transition path without modifying the
game installation by hand (for example, use an invalid disposable destination
save/path only if the existing test tooling supports that safely).

After returning to a stable UI, execute a normal game load.

If the normal load reports `portal_pending:1`, the stale-ownership hypothesis
is confirmed.

### Scenario D — hyperspace after successful arm jump

After a confirmed clean arrival:

1. perform the ordinary hyperspace transition that has previously looped;
2. inspect the nearest `loadgame-result`;
3. verify whether `portal_pending` is incorrectly non-zero;
4. correlate with `arrival-poll` direction.

## Source-level regression contract

Before accepting any future repair, add a deterministic adapter test or
source-level assertion for this lifecycle:

```text
idle:
  portal_load_pending = 0
  pending_arrival_direction = -1

portal prepared:
  portal_load_pending = 1

portal LoadGame result:
  portal_load_pending = 0

arrival consumed:
  pending_arrival_direction = -1

abort / external reload / stale-session reset:
  portal_load_pending = 0
  pending_arrival_direction = -1
  pending_arrival_ticks = 0
```

The important property is not a particular helper name: **every terminal abort
or global-state reset must return the transition ownership state to idle**.

## Patch candidate

The smallest candidate repair, if the game-machine logs confirm the hypothesis,
is to centralize Eltan transition-state cancellation and invoke it from:

- external reload recovery;
- stale-session recovery;
- any portal-load preparation failure/abort after ownership may have been armed.

The cancellation must reset at least:

- portal load ownership;
- pending arrival direction/ticks;
- stale portal identity/status fields that belong to the abandoned transition.

Do not patch blindly yet: the current reference repository has unresolved
project-wide licensing/provenance questions documented in
`docs/AGENT_COORDINATION.md`, and the canonical product repository should not
bulk-copy the native adapter.

## What this spike does NOT prove

- It does not prove that stale pending state is the only return-stall cause.
- It does not prove a repair works on Steam or Universe.
- It does not claim an in-game fix.
- It does not authorize copying the reference adapter into the canonical repo.

## Next bounded step

Run Scenarios A–D on the game machine.

If the logs confirm stale ownership, implement the smallest reset patch in the
appropriate licensed/source tree, then test the native adapter on **both Steam
and Universe** as required by the reference testing contract.
