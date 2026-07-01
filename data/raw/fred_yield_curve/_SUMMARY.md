# data/raw/fred_yield_curve Summary

Status: TASK-065 bounded raw evidence fixture.

This directory contains the recorded FRED CSV fixture used by the bounded monthly U.S. Treasury yield curve evidence slice.

## Fixture

- `fred-monthly-yield-curve-gs1m-gs1-gs10-gs30.csv`

## Source

- Provider: Federal Reserve Bank of St. Louis FRED.
- URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS1M,GS1,GS10,GS30`
- Series: `GS1M`, `GS1`, `GS10`, `GS30`.
- Source content: monthly U.S. Treasury constant maturity yields.

## Bounded slice

TASK-065 uses only:

- Periods: `2024-01`, `2024-02`.
- Tenors: `GS1M`, `GS1`, `GS10`, `GS30`.
- Expected observations: 8.

The full CSV fixture is preserved for deterministic clean-clone replay, but the implementation intentionally normalizes only the bounded selected-period/tenor slice.

## Checksums

- Fixture SHA-256: `0870977a6dc92d4eb841235ed1335c32ad88914387fe7588ffeeb851e3411a2f`
