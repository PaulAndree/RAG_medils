Date: 2026-05-16T10:10:00Z
Author: Nuria Castaño Rey
Message: The second collection load finished with 286 rejected records and 43 warnings.

Date: 2026-05-16T10:12:00Z
Author: Lucía Navarro Gil
Message: We need to classify schema, encoding and link failures before rerunning it.

Date: 2026-05-16T10:14:00Z
Author: Sergio Vidal Cruz
Message: One hundred seventy-two rejections are caused by fields renamed after guide 1.1.

Date: 2026-05-16T10:16:00Z
Author: Mateo Ruiz Serra
Message: The archive export template still used creatorRole instead of archivalRole.

Date: 2026-05-16T10:19:00Z
Author: Eva Calderón Gil
Message: That is a version-alignment issue; the archive did not receive the final template.

Date: 2026-05-16T10:22:00Z
Author: Diego Ramos León
Message: Sixty-eight rejections involve entity identifiers containing spaces or non-normalized characters.

Date: 2026-05-16T10:25:00Z
Author: Nuria Castaño Rey
Message: Can we normalize them automatically without collision risk?

Date: 2026-05-16T10:28:00Z
Author: Diego Ramos León
Message: Only in 51 cases. The other 17 produce the same normalized identifier and require review.

Date: 2026-05-16T10:31:00Z
Author: Sergio Vidal Cruz
Message: The remaining 46 rejections are UTF-8 encoding problems in titles and proper names.

Date: 2026-05-16T10:34:00Z
Author: Lucía Navarro Gil
Message: We must not replace characters with generic symbols; we need to recover the original text.

Date: 2026-05-16T10:37:00Z
Author: Eva Calderón Gil
Message: The archive can regenerate those records from the primary database, which retains the characters correctly.

Date: 2026-05-16T10:40:00Z
Author: Mateo Ruiz Serra
Message: What do the 43 warnings represent?

Date: 2026-05-16T10:43:00Z
Author: Sergio Vidal Cruz
Message: Uncertain dates without method, candidate links without evidence and educational rights without an expiry date.

Date: 2026-05-16T10:46:00Z
Author: Lucía Navarro Gil
Message: Those warnings should block publication even if they do not block a diagnostic load.

Date: 2026-05-16T10:49:00Z
Author: Nuria Castaño Rey
Message: I will create two profiles: ingestion-diagnostic and publication-strict.

Date: 2026-05-16T10:52:00Z
Author: Diego Ramos León
Message: I will review the 17 colliding identifiers and document the correct entity.

Date: 2026-05-16T10:55:00Z
Author: Eva Calderón Gil
Message: The archive will deliver the updated template and the 46 corrected records on 19 May.

Date: 2026-05-16T10:58:00Z
Author: Mateo Ruiz Serra
Message: I will update method, evidence and expiryDate in the warned cases.

Date: 2026-05-16T11:01:00Z
Author: Sergio Vidal Cruz
Message: The rerun will include counts by status, hash validation and comparison with the first load.

Date: 2026-05-16T11:05:00Z
Author: Lucía Navarro Gil
Message: Agreed: template 1.1, controlled normalization, UTF-8 recovery, review of 17 collisions and a strict profile before publication.