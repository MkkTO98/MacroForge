# TASK-189 Campaign Selection Report

Status: complete
Date: 2026-07-09

## Planning hierarchy result

Strategic objective: construct the canonical macroeconomic repository under evidence-maintained architecture.

Selected macroeconomic domain: external sector / macro-financial vulnerability.

Selected analytical capability: external vulnerability and financial openness monitoring.

Capability maturity gap: the repository had broad WDI trade/finance core and IMF bounded evidence, but lacked broad annual country-panel coverage for current-account balance, reserves adequacy, FDI flows, external-debt burden, debt service, and savings/external-balance context.

Confidence cell: WDI public API v2 annual scalar country-indicator observations.

Largest evidence-supported campaign: all 20 selected WDI external-vulnerability/financial-openness candidate indicators over all 217 non-aggregate WDI countries and 1990-2024.

Source-specific implementation path: existing WDI annual-scalar canonical loader.

## Candidate universe

Candidate indicators: 20.

Included after deterministic preflight: 17.
Excluded as localized provider evidence: 3.

## Included indicators

- `BM.KLT.DINV.CD.WD`
- `BM.KLT.DINV.WD.GD.ZS`
- `BN.CAB.XOKA.CD`
- `BN.CAB.XOKA.GD.ZS`
- `BN.KAC.EOMS.CD`
- `BN.TRF.KOGT.CD`
- `BX.KLT.DINV.CD.WD`
- `BX.KLT.DINV.WD.GD.ZS`
- `DT.DOD.DECT.CD`
- `DT.DOD.DECT.GN.ZS`
- `DT.TDS.DECT.EX.ZS`
- `FI.RES.TOTL.CD`
- `FI.RES.TOTL.MO`
- `FI.RES.XGLD.CD`
- `NE.RSB.GNFS.ZS`
- `NY.GNS.ICTR.CD`
- `NY.GNS.ICTR.ZS`

## Excluded indicators

- `DT.DOD.DECT.EX.ZS` — unsupported response shape
- `DT.INT.DECT.EX.ZS` — unsupported response shape
- `DT.NFL.DECT.CD` — unsupported response shape

## Selection rationale

This was the highest-value compatible campaign because it materially improves investment-relevant external vulnerability monitoring using the proven WDI annual-scalar path. It closes a real capability gap without selecting a provider first, creating a generic framework, or reopening architecture.
