# TASK-197 Operational Campaign Sizing Report

Previous evidence: TASK-196 completed a 120-candidate WDI campaign reliably, while an initial 575-candidate health-topic attempt hit timeout/large-artifact pressure.

Selected size: 155 candidates.

Reason: 155 was the full remaining WDI Environment topic universe, far below the failed 575-candidate scale and only modestly above the proven 120-candidate scale. Expected maximum rows were 1,177,225, with estimated artifact sizes around 0.51GB raw and 1.08GB normalized.

Observed: initial command hit 600s timeout but checkpoint/resume completed deterministically; final artifacts were about 398MB raw and 882MB normalized.

Future sizing recommendation: keep current WDI annual-scalar single-artifact campaigns around 120-160 indicators unless streaming/chunked artifact writing is implemented. Larger campaigns should be partitioned.
