# TASK-194 Campaign Selection Report

Selected domain: Education and human-capital attainment.

Selected analytical capability: global educational attainment distribution and schooling-stock monitoring.

Remaining capability gap: detailed attainment distribution and schooling stock by age/sex were missing from the WDI human-capital repository section.

Confidence cell: WDI public API v2 annual scalar country-indicator observations for Barro-Lee education attainment series.

Implementation path: existing WDI annual-scalar fetch/classify/normalize/load path with raw evidence preservation and provider evidence classification.

Why preferred: this campaign produces a coherent domain-completion increment in an already operationally useful domain, creates substantial canonical growth, and avoids the architectural pressure present in trade relationship, financial counterparty, housing provider, or company entity campaigns. A WDI energy-emissions preflight produced a smaller viable compatible subset because many legacy emissions candidates were provider-unavailable in the requested API window.
