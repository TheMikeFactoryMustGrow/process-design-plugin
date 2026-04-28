# Inputs Checklist — what to pull, from where

The agent fills out the figures table from this list. Every figure here must
end up in the table; every number in the draft must come from this table.

If a figure isn't in the source where this checklist says it should be, the
agent stops and asks Mike. It does NOT estimate, interpolate, or pull from
last quarter's update as a substitute (that's how stale numbers leak in).

## From the financial model

Mike to confirm sheet/tab names each quarter — they tend to drift.
Suggested stable convention: a tab called `INVESTOR_UPDATE_PULL` that
references the live cells, so the agent always pulls from one place. (This
is the single highest-leverage change Mike can make to stabilize this
process — see `05_review-loop.md` for why.)

| # | Figure | Tab/Section | Notes |
|---|--------|-------------|-------|
| F1 | Revenue (this quarter, actual) | P&L |  |
| F2 | Revenue (prior quarter, actual) | P&L |  |
| F3 | Revenue (YTD actual) | P&L |  |
| F4 | Revenue (FY plan / forecast) | P&L |  |
| F5 | Gross margin % (this quarter) | P&L |  |
| F6 | OpEx (this quarter) | P&L |  |
| F7 | EBITDA (this quarter) | P&L |  |
| F8 | CapEx — construction (this quarter) | CapEx |  |
| F9 | CapEx — construction (YTD) | CapEx |  |
| F10 | Cash on hand (end of quarter) | Balance sheet |  |
| F11 | Debt drawn (end of quarter) | Balance sheet |  |
| F12 | Debt available (undrawn) | Debt schedule |  |
| F13 | Current monthly burn | Cash flow |  |
| F14 | Implied months of runway (F10 / F13) | Derived; agent must compute and double-check |  |
| F15 | Construction commitments outstanding (end of quarter) | Commitments |  |

## From the operations dashboard

| # | Figure | Notes |
|---|--------|-------|
| O1 | Homes passed, cumulative |  |
| O2 | Homes passed this quarter |  |
| O3 | Customers connected, cumulative |  |
| O4 | Net adds this quarter |  |
| O5 | Take rate (O3 / O1) | Confirm denominator includes only mature passings (>6 mo). Note exclusion in template if so. |
| O6 | ARPU (this quarter) |  |
| O7 | Monthly churn (this quarter) |  |
| O8 | Active markets |  |
| O9 | Construction milestones — planned vs actual | One row per market. Slip in weeks. |
| O10 | Top 1–2 ops issues this quarter | Free text from dashboard or Mike's notes. |

## From last quarter's update

| # | Figure | Notes |
|---|--------|-------|
| L1 | Last quarter's "Outlook — next quarter" commitments | These become this quarter's score card. |
| L2 | Last quarter's risks watched | Decide which resolved, which still live. |
| L3 | Anything Greg flagged in last quarter's review | The agent must explicitly check that this quarter's draft does not repeat the same mistake. |

## From Mike's running notes

Free-form. The agent reads them, lifts:
- Wins / losses / hires / departures / partnerships / regulatory items
  for §7 (Strategic moves) and §5–6 (working / not working).
- Anything explicitly marked "investor update" by Mike.

## From the outstanding-asks log (if it exists)

Every open ask from any investor that hasn't been answered. If we have an
answer this quarter, address it explicitly, even if just one sentence. If we
don't yet, say "still working on it; expect resolution by [date]." Silence
on an open ask is a trust hit.
