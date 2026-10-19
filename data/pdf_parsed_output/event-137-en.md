First VERDANT monitoring review to define policy v1.0 indicators and alerts, supervise hourly transfers and local processing, and detect breaches involving granularity, retention or group size.

Andrés Beltrán: Policy v1.0 is approved, but we need to observe its application without relying on manual reviews.
Sergio Vidal: I propose indicators for approved and rejected requests, granularity, effective group size, retention, revocations and confirmed deletion.
Nuria Castaño: The connector already records those fields. We can generate alerts when a request asks for 15-minute data, omits its purpose or exceeds the authorized period.
Héctor Molina: We also need an alert if effective group size falls below three for hourly data or five for local-processing results.
Inés Ferrer: We should distinguish preventive suppression from technical failure. In the first case, absence of a result is the correct behavior.
Carmen Rey: SolCentro wants a weekly summary and an immediate alert only for prohibited-access attempts or deletion failures.
Sergio Vidal: The dashboard can separate compliance, quality and operations. Sensitive details will remain visible only to the provider and auditor.
Andrés Beltrán: Which initial thresholds will we apply?
Nuria Castaño: A critical alert for requested 15-minute export, access without a signed decision and overdue deletion. A warning for more than 5 percent suppressed intervals or synchronization errors above ten minutes.
Héctor Molina: The thresholds are appropriate for the pilot and should be reviewed after one month.
Andrés Beltrán: Approved. The monitoring dashboard will activate on 13 July and feed the monthly review.