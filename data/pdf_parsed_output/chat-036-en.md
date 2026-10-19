Date: 2026-05-28T10:05:00Z
Author: Elena Martín Ríos
Message: The postmortem remains open because of duplicate profiles that appeared after migration. We need to close the cause and actions.

Date: 2026-05-28T10:07:00Z
Author: Diego Ramos León
Message: The review found 312 suspicious pairs and 74 confirmed duplicates.

Date: 2026-05-28T10:09:00Z
Author: Mireia Soler Pons
Message: The main cause is that the new system treated identifiers from different sources as different people.

Date: 2026-05-28T10:11:00Z
Author: Sergio Vidal Cruz
Message: The ORCID reconciliation rule ran after internal keys were created rather than before.

Date: 2026-05-28T10:14:00Z
Author: Nuria Castaño Rey
Message: There was also a partial load repeated after a network failure.

Date: 2026-05-28T10:17:00Z
Author: Clara Ibáñez Soto
Message: Did the restart lack an idempotency control?

Date: 2026-05-28T10:20:00Z
Author: Sergio Vidal Cruz
Message: The control existed for complete records but not for affiliation relationships created in batches.

Date: 2026-05-28T10:23:00Z
Author: Diego Ramos León
Message: That explains 19 duplicate profiles; the other 55 result from late reconciliation.

Date: 2026-05-28T10:26:00Z
Author: Elena Martín Ríos
Message: What impact did this have on outputs and projects?

Date: 2026-05-28T10:29:00Z
Author: Diego Ramos León
Message: No data was lost, but 128 outputs were split across duplicate profiles.

Date: 2026-05-28T10:32:00Z
Author: Mireia Soler Pons
Message: Corrections must retain merge history and source identifiers.

Date: 2026-05-28T10:35:00Z
Author: Nuria Castaño Rey
Message: We can rerun migration in an isolated environment and compare counts before touching the preserved snapshot.

Date: 2026-05-28T10:38:00Z
Author: Sergio Vidal Cruz
Message: I will add an idempotencyKey for records and relationships, plus a pre-reconciliation phase.

Date: 2026-05-28T10:41:00Z
Author: Clara Ibáñez Soto
Message: We need actions with dates, owners and closure evidence.

Date: 2026-05-28T10:44:00Z
Author: Diego Ramos León
Message: I will review the 74 duplicates and the 128 output assignments.

Date: 2026-05-28T10:47:00Z
Author: Mireia Soler Pons
Message: I will prepare rules for alternate names, incorrectly shared ORCIDs and overlapping affiliations.

Date: 2026-05-28T10:50:00Z
Author: Nuria Castaño Rey
Message: The full rerun can take place on 2 June with immediate restoration if counts diverge.

Date: 2026-05-28T10:53:00Z
Author: Sergio Vidal Cruz
Message: Validation will include uniqueness, relationship counts, hashes and absence of repeated loads.

Date: 2026-05-28T10:56:00Z
Author: Elena Martín Ríos
Message: The postmortem must state that the original snapshot is preserved and the correction is a derivative version.

Date: 2026-05-28T11:00:00Z
Author: Clara Ibáñez Soto
Message: Agreed: 74 documented merges, pre-reconciliation, full idempotency and closure only after comparing the repeated migration.