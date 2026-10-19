Date: 2026-02-21T10:00:00Z
Author: Lucía Navarro Gil
Message: We need to coordinate the first bulk load into the KG Portal without affecting the demonstration environment.

Date: 2026-02-21T10:02:00Z
Author: Nuria Castaño Rey
Message: The load contains 12,400 descriptions and approximately 310,000 triples.

Date: 2026-02-21T10:04:00Z
Author: Sergio Vidal Cruz
Message: I validated the package: it has a manifest, checksum and transformation version.

Date: 2026-02-21T10:06:00Z
Author: Diego Ramos León
Message: Entity links still include candidates, so not all of them should be published as confirmed.

Date: 2026-02-21T10:09:00Z
Author: Mateo Ruiz Serra
Message: Candidates are separated by status and should not appear in public queries by default.

Date: 2026-02-21T10:12:00Z
Author: Lucía Navarro Gil
Message: What load window do we need?

Date: 2026-02-21T10:15:00Z
Author: Nuria Castaño Rey
Message: Ninety minutes to import and another forty-five to rebuild indexes and run checks.

Date: 2026-02-21T10:18:00Z
Author: Sergio Vidal Cruz
Message: I propose starting at 18:00, after the archive session, and keeping the portal read-only.

Date: 2026-02-21T10:21:00Z
Author: Diego Ramos León
Message: Is there a complete backup of the current state?

Date: 2026-02-21T10:24:00Z
Author: Nuria Castaño Rey
Message: Yes. I will take one snapshot before the load and another after verification.

Date: 2026-02-21T10:27:00Z
Author: Mateo Ruiz Serra
Message: We need to check counts by type: objects, people, places, organizations and uncertain dates.

Date: 2026-02-21T10:30:00Z
Author: Sergio Vidal Cruz
Message: I will add control queries to detect unlabeled nodes, orphan relationships and duplicate identifiers.

Date: 2026-02-21T10:33:00Z
Author: Lucía Navarro Gil
Message: What do we do if index rebuilding fails?

Date: 2026-02-21T10:36:00Z
Author: Nuria Castaño Rey
Message: We restore the pre-load snapshot and leave the portal read-only until analysis is complete.

Date: 2026-02-21T10:39:00Z
Author: Diego Ramos León
Message: I want a specific test ensuring that candidate links do not appear as confirmed.

Date: 2026-02-21T10:42:00Z
Author: Mateo Ruiz Serra
Message: We will also verify that original date expressions remain alongside normalized intervals.

Date: 2026-02-21T10:45:00Z
Author: Sergio Vidal Cruz
Message: The verification package will contain twenty queries and a difference summary against the previous version.

Date: 2026-02-21T10:48:00Z
Author: Lucía Navarro Gil
Message: Who authorizes reopening the portal?

Date: 2026-02-21T10:51:00Z
Author: Nuria Castaño Rey
Message: I will confirm infrastructure; Sergio will confirm integrity; Diego and Mateo will validate links and dates.

Date: 2026-02-21T10:55:00Z
Author: Lucía Navarro Gil
Message: The 18:00–20:15 window is set, with a pre-load backup, read-only mode and reopening after four validations.