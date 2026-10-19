Date: 2026-05-09T09:15:00Z
Author: Andrés Beltrán Vega
Message: We need alerts that distinguish data loss, synchronization delay and privacy suppression.

Date: 2026-05-09T09:17:00Z
Author: Inés Ferrer Lozano
Message: The dashboard currently shows only missing intervals even when causes differ.

Date: 2026-05-09T09:19:00Z
Author: Carmen Rey Palacios
Message: SolCentro can send qualityCode and last-reading time for each facility.

Date: 2026-05-09T09:21:00Z
Author: Nuria Castaño Rey
Message: The connector also knows whether an interval was suppressed before transfer.

Date: 2026-05-09T09:24:00Z
Author: Sergio Vidal Cruz
Message: I propose the states missing-source, delayed, suppressed, rejected and complete.

Date: 2026-05-09T09:27:00Z
Author: Héctor Molina Frías
Message: The dashboard must not reveal how many facilities contributed to a suppressed interval.

Date: 2026-05-09T09:30:00Z
Author: Andrés Beltrán Vega
Message: Which thresholds do we use for missing data?

Date: 2026-05-09T09:33:00Z
Author: Inés Ferrer Lozano
Message: Warning when more than 2 percent is missing in a 24-hour window, and critical above 5 percent or when four consecutive intervals are missing.

Date: 2026-05-09T09:36:00Z
Author: Carmen Rey Palacios
Message: For an individual facility, two hours without readings should alert the metering team.

Date: 2026-05-09T09:39:00Z
Author: Nuria Castaño Rey
Message: Synchronization will trigger a warning after ten minutes and a critical alert after thirty.

Date: 2026-05-09T09:42:00Z
Author: Sergio Vidal Cruz
Message: Alerts need an identifier, start time, scope, known cause, owner and status.

Date: 2026-05-09T09:45:00Z
Author: Héctor Molina Frías
Message: Suppression should not be classified as loss when required by policy.

Date: 2026-05-09T09:48:00Z
Author: Inés Ferrer Lozano
Message: But we need to measure its impact on indicators and avoid confusing it with complete data.

Date: 2026-05-09T09:51:00Z
Author: Andrés Beltrán Vega
Message: Who receives each level?

Date: 2026-05-09T09:54:00Z
Author: Carmen Rey Palacios
Message: Source warnings go to SolCentro; synchronization alerts to Nuria; scientific-quality alerts to Inés.

Date: 2026-05-09T09:57:00Z
Author: Sergio Vidal Cruz
Message: Critical alerts also notify Andrés and are recorded in the governance log.

Date: 2026-05-09T10:00:00Z
Author: Nuria Castaño Rey
Message: I will add deduplication so the same incident does not create a new alert for every interval.

Date: 2026-05-09T10:03:00Z
Author: Héctor Molina Frías
Message: Closure must record the cause, correction and whether any transfer or analysis was affected.

Date: 2026-05-09T10:06:00Z
Author: Andrés Beltrán Vega
Message: We will test the rules with simulated failures before connecting them to real data.

Date: 2026-05-09T10:10:00Z
Author: Inés Ferrer Lozano
Message: Agreed: separate states, 2 and 5 percent thresholds for loss, ten and thirty minutes for synchronization and owner-based escalation.