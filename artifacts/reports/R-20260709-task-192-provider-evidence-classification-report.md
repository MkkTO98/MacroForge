# TASK-192 Provider Evidence Classification Report

Status: complete
Date: 2026-07-09

Classification rule: Classifications are based on archived raw data response, indicator metadata response, response shape, non-aggregate row count, non-null observations, annual-period check, and indicator/country consistency checks.

Excluded indicator count: 1.

## Excluded datasets

- `FB.AST.LIQU.ZS`: classification=`provider_unavailable`, provider_evidence_category=`provider_unavailable_invalid_indicator`, evidence=[{"id": "120", "key": "Invalid value", "value": "The provided parameter value is not valid"}]

## Evidence preservation

The raw acquisition artifact retains both data responses and indicator metadata responses for every candidate indicator, including excluded datasets. The processed normalized artifact retains an evidence manifest with response checksums, metadata checksums, byte sizes, classifications, and preservation status.

No raw acquisition artifacts were deleted.
