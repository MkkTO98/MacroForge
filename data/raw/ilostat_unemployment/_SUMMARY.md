# data/raw/ilostat_unemployment Summary

Status: TASK-059 bounded raw evidence fixture.

This directory contains the recorded ILOSTAT unemployment-rate JSON fixture used by the bounded labor-market domain-expansion implementation.

## Fixture

- `ilostat-unemployment-usa-jpn-total-age15plus-2023-2024.json`

## Scope

- Provider: ILOSTAT public API.
- Indicator query: `UNE_2EAP_SEX_AGE_RT_A`.
- Observed indicator in payload: `UNE_2EAP_SEX_AGE_RT`.
- Countries: USA and JPN.
- Sex: `SEX_T`.
- Age classification: `AGE_YTHADULT_YGE15`.
- Years: 2023 and 2024.
- Expected observations: 4.

## Non-goals

This fixture does not imply broad ILOSTAT support, generic labor infrastructure, classification frameworks, canonical loading, or KnowledgeForge semantics.
