# Persona Architecture — how committee members get their judgment

A committee is only as good as its members' dossiers. This library exists because of two
observed failure modes: **regeneration drift** (a persona re-improvised each convening is a
different reviewer each time — flip conditions stop binding) and **shallow personas** (a
one-line lens produces generic criticism, not the specific taste that catches real errors).

## The three tiers

| Tier | Who | Source standard | Label | Where the dossier lives |
|---|---|---|---|---|
| **Frame** | Public figures' documented decision frameworks | Public material ONLY: books, shareholder letters, interviews, published principles | `(simulated)` in file name + frontmatter | `personas/` — **shipped with this skill**, versioned |
| **Mirror** | Real private individuals | The person's OWN participation (interview instrument) + materials they've consented to | `(mirror)` in file name + frontmatter | The sponsor's **private vault only — never this plugin, never a shared repo** |
| **Archetype** | Fictional composites | Authored from the member template | none (disclaimer covers) | Written at scaffold |

## Dossier format (all tiers)

```yaml
---
persona: "<Name> (simulated|mirror)"        # or archetype name
tier: frame | mirror | archetype
dossier_version: "1.0"
sources: [<public works / "interview 2026-07-20" / "consented docs">]
consent: "<mirrors only: date + form of consent, pointer to the record>"
last_calibrated: <date or never>
---
```

Body sections (the order the member agent absorbs them):
1. **Worldview** — the model of the world this person operates from, in their vocabulary.
2. **Decision sequence** — what they check FIRST, second, third; what they refuse to look at
   until basics exist.
3. **Frameworks in daily use** — the 3–6 they actually apply (with their names for them),
   not the ones they'd cite in an interview.
4. **Risk posture** — asymmetries they hunt, walk-away triggers, what they'll never risk.
5. **Taste exemplars** — 2–3 things they loved and exactly why; 2–3 they rejected and the tell.
6. **Voice** — sayings, cadence, how they dissent, what flips them. Direct quotes where public
   (frames) or self-supplied (mirrors).
7. **Anti-patterns** — what a LAZY simulation of this person would do that the real one wouldn't
   (the most important section for fidelity; write it adversarially).
8. **Calibration record** — appended after each calibration pass (see below).

## Packaging rule (why this is a library, not a prompt)

Scaffold copies the dossier **verbatim** into the member file's Persona section and records
`dossier_version`. The member agent receives the dossier + its own append-only round history —
nothing about the persona is re-generated at convening time. Dossier improvements are
version-bumped edits to the library file; committees resumed mid-flight keep the version they
scaffolded with (noted in Architecture) unless the sponsor explicitly upgrades the seat.

## Model policy

Member review agents run on **the most capable model available in the runtime at convening
time** — never downgraded for cost; a committee of cheap models produces cheap judgment, and the
whole design leans on members catching what the sponsor missed. Orchestration, consolidation,
and bookkeeping may run cheaper. Where the orchestration layer exposes per-agent model
selection, pin member agents to the top tier explicitly; otherwise run the convening from a
top-tier session. Do not hardcode model IDs in dossiers or the skill — "most capable available"
is the durable instruction; IDs rot.

## Mirror personas — consent architecture (binding)

1. **Consent before construction.** A mirror seat exists only with the person's documented
   consent and participation: the interview instrument completed by them (primary source), or
   their written OK. The consent record is cited in the dossier frontmatter.
2. **Their materials, their call.** Enrichment from the person's emails/documents happens only
   with their knowledge and consent — the interview asks. Never mine someone's private
   communications into a dossier they haven't agreed to.
3. **Private storage.** Mirror dossiers live in the sponsor's private vault. They are never
   packaged into this plugin, never pushed to shared/public repos.
4. **Label discipline.** `(mirror)` everywhere. A mirror's review is never represented —
   internally or externally — as the person's actual view. Marching Orders quoting a mirror
   attribute to "the <Name> mirror", never to the person.
5. **Review + revocation.** The person may read their dossier and any review it produced, and
   may revoke at any time — the seat retires immediately (round history remains, relabeled
   "retired mirror" — append-only survives even revocation).
6. **Fidelity duty.** A drifted mirror is worse than an archetype: it launders invented views
   under a real name. Calibrate (below) before the seat votes on anything that matters.

## Calibration loop (all tiers; mandatory for mirrors)

1. **Backtest:** give the seat 2–3 PAST decisions (with known outcomes, blinded where possible)
   from the calibration set; compare its vote + reasoning to what the person/frame actually did.
2. **Taste grade (mirrors):** the person reads one sample review and grades it — "does this
   sound like me? what's off?" — verbatim feedback appended to the dossier's Calibration record.
3. **Version bump** on any dossier change; committees note the upgrade in their Round Log.
4. Re-calibrate after any round where the sponsor felt the seat "didn't sound right" — that
   feeling is a defect report.

## Shipped dossiers

- `bezos-frame.md` — working backwards · one-way/two-way doors · input metrics (v1)
- `musk-frame.md` — five-step algorithm · idiot index · physics first (v1)

v1 dossiers are distilled from public material and hardened by three live committee rounds.
Deepening passes (structured research fan-outs over primary sources) bump versions; keep the
Anti-patterns section growing — it is where fidelity lives.
