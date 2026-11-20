---
name: money
description: Whenever money or a price is calculated OR displayed, route it through the app's single money helper (lib/money.ts or equivalent) — 2 decimals always, Half-Up ROUND(x,2), the helper owns the currency symbol + decimal places (default THB, never scatter ฿/$ as raw strings). No toLocaleString/toFixed on money outside the helper; price inputs type=number step=0.01 parsed via the helper. Enforce with a check:money build gate. Scope = fiat / accounting / tax money, NOT exchange/trading tick-size. Run alongside verify-changes before pushing.
---

# money

A commit-time gate for **money**. Bills/ledgers that don't match the system come from
non-standard rounding (rounded at different points, float drift, inconsistent decimals) —
and it hits tax invoices / filings. So every money value in an app flows through **one
money helper**, rounded Half-Up to 2 decimals, with the currency symbol owned by that
helper. Canonical spec: **[money-rounding-standard](../../standards/money-rounding-standard.md)** (§gate rules); per-repo code
detail lives in the repo (e.g. `src/lib/money.ts` + `docs/money-standard.md`).

## 0. Does this gate apply? (scope first)

- **YES** — any **fiat / accounting / tax** money: prices, totals, VAT, withholding,
  invoices, payouts, balances, anything shown with a currency symbol or persisted as an
  amount. Shop / product pricing, finance, storefront/ops money all qualify.
- **NO** — **exchange / trading tick-size & precision** (e.g. a trading bot
  snapping price/qty to exchange filters). That's a different domain with no tax money — let
  the repo own it; do **not** force Half-Up / 2-decimals over it.

If it doesn't touch money, this gate is a no-op — say so and move on.

## 1. Detect the money helper (before touching anything)

Find the app's single source of truth for money — `lib/money.ts` (or `money.js`, a
`ioun:money`/`currency` util, a shared package). It should expose at least:

- `roundMoney(n)` — Half-Up, **float-safe** (`Math.round((n + Number.EPSILON) * 100) / 100`,
  or a decimal lib). Not bare `Math.round` on a float.
- `fmtMoney(n, currency?)` — **always 2 decimals** + thousands separator, symbol from config.
- `parseMoney(str)` — parse user input safely.
- A **currency config map** the helper owns: `THB → { symbol: '฿', decimals: 2 }`, extendable.
  Default THB. The **symbol + decimal count live here**, never hardcoded at call sites.

**No helper, but money is calculated/displayed?** That's the fix — set one up (this is a
real code change → run **verify-changes** after). Don't scatter `toFixed`/`toLocaleString`/`฿`.

## 2. The rules (calc + display)

1. **Store/compute** unit price · cost · rate · FX at **full precision (4–6 dp)** — keep raw,
   don't round early.
2. **Display + persist** amounts / VAT / withholding at **2 decimals always** (`฿7,500.00`,
   not `฿7,500`).
3. **Half-Up ROUND(x, 2)** at every truncation point (`100.545 → 100.55`) — per สรรพากร ป.86/2542.
4. **Calc order, rounding step-by-step:** line total (price × qty, full precision) → discount
   → **net ROUND2** → VAT 7% **ROUND2** → grand total 2dp.
5. **Cash rounding** (counter change) is a separate concern — ledger keeps true 2dp; the change
   difference is booked as rounding gain/loss. Only when there's a real cash POS.

## 3. The check (run before committing — must come back empty)

Don't hardcode `src/` (App-Router repos use `app/`/`components/`/`lib/`, monorepos `apps/*`):

```bash
ROOTS=$(ls -d app src components lib apps packages 2>/dev/null); [ -z "$ROOTS" ] && ROOTS=.
INC='--include=*.ts --include=*.tsx --include=*.jsx'
EXC='--exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist --exclude-dir=build'
# toFixed / toLocaleString on money, OUTSIDE the money helper itself
grep -rnE '\.(toFixed|toLocaleString)\(' $INC $EXC $ROOTS | grep -viE '/money\.(ts|tsx|js)'
# raw currency symbols hardcoded near a value (should come from fmtMoney/config)
grep -rnE '[฿$€£]\s*[\{0-9]' $INC $EXC $ROOTS | grep -viE '/money\.(ts|tsx|js)'
# price inputs not using a numeric step (should be type=number step=0.01)
grep -rniE 'type=.number.' $INC $EXC $ROOTS | grep -i price | grep -v 'step'
```

Any hit is either (a) migrated to the helper, or (b) a justified exception tagged inline
(e.g. a genuinely non-money number). A **`check:money` build gate** (same shape as
`check:dates` / `check:pii`) should fail the build on these — wire it per repo.

## 4. Report (gate)

```
money
scope: applies (storefront prices + VAT)     helper: apps/ops/src/lib/money.ts
✓ all amounts via fmtMoney (2dp)  ✓ Half-Up roundMoney (float-safe)  ✓ symbol from config (THB)
✓ grep clean: no toFixed/toLocaleString/raw ฿ outside helper
✓ price inputs type=number step=0.01 via parseMoney
```

- All green → safe to commit/push (then the normal verify-changes gate applies).
- Any escapee, early rounding, or `฿`/`$` shown without 2 decimals → **stop; fix first.**
- **Enforcement vs guidance:** this skill is the *procedure* — run it yourself and push if
  green. The machine-wide `PreToolUse` git hook (the ioun git-gate hook) only reminds.
- Pairs with **verify-changes** (checks the code) and **i18n-guard** (checks the words); this
  one checks the numbers.
