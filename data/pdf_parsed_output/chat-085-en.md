Date: 2026-03-01T09:25:00Z
Author: Elena Martín Ríos
Message: Before reusing ORION, we need to resolve inconsistent keys across historical exports.

Date: 2026-03-01T09:27:00Z
Author: Diego Ramos León
Message: The same person may appear as P-00123, PERSON123 and orion:123 depending on the year.

Date: 2026-03-01T09:29:00Z
Author: Mireia Soler Pons
Message: Projects also have call codes, internal codes and public URIs.

Date: 2026-03-01T09:31:00Z
Author: Sergio Vidal Cruz
Message: I counted 14 key patterns across eleven tables.

Date: 2026-03-01T09:34:00Z
Author: Nuria Castaño Rey
Message: Is there a master table that can reconcile them?

Date: 2026-03-01T09:37:00Z
Author: Diego Ramos León
Message: Only for 72 percent of profiles; the rest requires a combination of name, historical email and affiliation.

Date: 2026-03-01T09:40:00Z
Author: Elena Martín Ríos
Message: We cannot create a stable key based only on name.

Date: 2026-03-01T09:43:00Z
Author: Mireia Soler Pons
Message: I propose retaining sourceKey and creating stableId only when sufficient evidence exists.

Date: 2026-03-01T09:46:00Z
Author: Sergio Vidal Cruz
Message: The crosswalk table will contain sourceSystem, sourceKey, stableId, confidence and evidence.

Date: 2026-03-01T09:49:00Z
Author: Nuria Castaño Rey
Message: Which confidence threshold do we use for automatic assignment?

Date: 2026-03-01T09:52:00Z
Author: Diego Ramos León
Message: 0.95 with an external identifier or an exact match on three signals; the rest goes to review.

Date: 2026-03-01T09:55:00Z
Author: Elena Martín Ríos
Message: What do we do with keys that were reused for different people?

Date: 2026-03-01T09:58:00Z
Author: Mireia Soler Pons
Message: They must never map to a single stableId. They are separated by period and source and marked reused-key.

Date: 2026-03-01T10:01:00Z
Author: Sergio Vidal Cruz
Message: I will add contextual uniqueness validation and orphan-key detection.

Date: 2026-03-01T10:04:00Z
Author: Diego Ramos León
Message: We have 186 ambiguous keys and 43 orphan keys.

Date: 2026-03-01T10:07:00Z
Author: Nuria Castaño Rey
Message: Normalization must be reproducible and preserve the original export unchanged.

Date: 2026-03-01T10:10:00Z
Author: Elena Martín Ríos
Message: We will create a derivative layer rather than correcting preserved files.

Date: 2026-03-01T10:13:00Z
Author: Mireia Soler Pons
Message: I will document rules, exceptions and cases where no stableId is assigned.

Date: 2026-03-01T10:16:00Z
Author: Sergio Vidal Cruz
Message: The first run will produce coverage and conflict reports by table.

Date: 2026-03-01T10:20:00Z
Author: Elena Martín Ríos
Message: Agreed: preserved sourceKey values, evidence-conditioned stableId assignment, 186 cases for review and a reproducible derivative layer.