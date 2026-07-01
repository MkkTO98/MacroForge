# data/raw/imf_bop_financial_account Summary

Status: TASK-063 bounded raw evidence fixture.

This directory contains the recorded IMF BOP SDMX XML fixtures used by the bounded financial-account evidence slice.

## Fixture

- `imf-bop-financial-account-usa-jpn-2022-2023.xml`
- Source URL: `https://api.imf.org/external/sdmx/2.1/data/BOP/USA+JPN.A_NFA_T+L_NIL_T.D_F+P_F.USD.A?startPeriod=2022&endPeriod=2023`
- SHA-256: `0bef9c7cd07512668c23e1ca69b18c20123c338c6ec11a919d940220c5e0a7bf`

## Metadata fixture

- `imf-bop-dataflow-references-20260701.xml`
- Metadata URL: `https://api.imf.org/external/sdmx/2.1/dataflow/all/BOP/latest?references=all`
- SHA-256: `973edcc6bc64347314de55d408fb86a3d3de16320d9bf0ec2fff71ee8729c136`

## Bounded scope

- Dataflow: IMF BOP.
- Countries: USA and JPN.
- Accounting entries: `A_NFA_T`, `L_NIL_T`.
- Indicators: `D_F`, `P_F`.
- Unit/frequency: USD, annual.
- Periods: 2022 and 2023.
- Expected observations: 16.

## Non-goals

No broad IMF/BOP support, financial-account framework, generic SDMX extraction, canonical loading, or KnowledgeForge semantics are introduced by this fixture.
