Date: 2026-05-27T09:25:00Z
Author: Inés Ferrer Lozano
Message: I found six intervals shifted by one hour and twelve records with non-zero seconds.

Date: 2026-05-27T09:27:00Z
Author: Andrés Beltrán Vega
Message: Does this affect one facility or several?

Date: 2026-05-27T09:29:00Z
Author: Inés Ferrer Lozano
Message: The six shifts belong to two facilities; non-zero seconds appear across all four.

Date: 2026-05-27T09:31:00Z
Author: Carmen Rey Palacios
Message: The two facilities use a meter model that exports local time without a zone indicator.

Date: 2026-05-27T09:34:00Z
Author: Nuria Castaño Rey
Message: The connector assumed UTC because the field was absent.

Date: 2026-05-27T09:37:00Z
Author: Sergio Vidal Cruz
Message: That explains the shift, but we need to check whether it coincides with daylight-saving time.

Date: 2026-05-27T09:40:00Z
Author: Inés Ferrer Lozano
Message: The records are from 31 March and 1 April; not all coincide with the official clock change.

Date: 2026-05-27T09:43:00Z
Author: Carmen Rey Palacios
Message: The device retained an old configuration for two days after the clock change.

Date: 2026-05-27T09:46:00Z
Author: Andrés Beltrán Vega
Message: Can we correct them without losing the original literal?

Date: 2026-05-27T09:49:00Z
Author: Sergio Vidal Cruz
Message: Yes. We retain sourceTimestamp and add normalizedTimestamp, sourceTimeZone and correctionRule.

Date: 2026-05-27T09:52:00Z
Author: Nuria Castaño Rey
Message: The twelve records with seconds come from readings sent at :58 or :02 because of clock drift.

Date: 2026-05-27T09:55:00Z
Author: Inés Ferrer Lozano
Message: We should not round blindly when two readings may fall into the same interval.

Date: 2026-05-27T09:58:00Z
Author: Carmen Rey Palacios
Message: The metering system guarantees one reading per fifteen-minute window; we can use nearest-interval with a three-minute tolerance.

Date: 2026-05-27T10:01:00Z
Author: Sergio Vidal Cruz
Message: If two candidates map to the same interval or drift exceeds three minutes, the record is marked temporal-ambiguous.

Date: 2026-05-27T10:04:00Z
Author: Andrés Beltrán Vega
Message: Did these errors reach an external transfer?

Date: 2026-05-27T10:07:00Z
Author: Nuria Castaño Rey
Message: No. They were found during pre-transfer validation, and the batch remains blocked.

Date: 2026-05-27T10:10:00Z
Author: Inés Ferrer Lozano
Message: After correction, we will rerun hourly aggregation and balance comparison.

Date: 2026-05-27T10:13:00Z
Author: Carmen Rey Palacios
Message: I will update the two devices' configuration and provide time-zone evidence.

Date: 2026-05-27T10:16:00Z
Author: Sergio Vidal Cruz
Message: I will add mandatory UTC validation and a specific daylight-saving test.

Date: 2026-05-27T10:20:00Z
Author: Andrés Beltrán Vega
Message: Agreed: retain original timestamps, normalize with an explicit zone, use a three-minute tolerance and block ambiguous cases.