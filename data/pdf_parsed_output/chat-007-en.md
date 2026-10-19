Date: 2026-02-01T08:40:00Z
Author: Alba Prieto Mora
Message: I found two different procedures sharing the same local identifier, SM-REG-014.

Date: 2026-02-01T08:42:00Z
Author: Javier Ortega Campos
Message: Is it a source duplicate, or did we introduce it during transformation?

Date: 2026-02-01T08:44:00Z
Author: Sergio Vidal Cruz
Message: The original municipal file contains SM-REG-014 and SM-REG-041. The transformation removed the last digit because of an old rule.

Date: 2026-02-01T08:46:00Z
Author: Mireia Soler Pons
Message: Then the error is in normalization, not in the identifier model.

Date: 2026-02-01T08:49:00Z
Author: Nuria Castaño Rey
Message: How many records could be affected by that rule?

Date: 2026-02-01T08:52:00Z
Author: Sergio Vidal Cruz
Message: The rule was applied to 62 procedures, but it only creates a collision when final digits are reversed or repeated.

Date: 2026-02-01T08:55:00Z
Author: Alba Prieto Mora
Message: I ran a search and found two confirmed collisions and three suspicious cases.

Date: 2026-02-01T08:58:00Z
Author: Javier Ortega Campos
Message: We should not correct only the two visible cases. We need a patch and a complete test.

Date: 2026-02-01T09:01:00Z
Author: Sergio Vidal Cruz
Message: I will remove the truncation rule and generate identifiers from the exact municipal code plus a namespace.

Date: 2026-02-01T09:04:00Z
Author: Mireia Soler Pons
Message: Published identifiers should not change silently. Have any left the internal environment?

Date: 2026-02-01T09:07:00Z
Author: Nuria Castaño Rey
Message: They were only used in the internal technical demo; none have been delivered to the municipality.

Date: 2026-02-01T09:10:00Z
Author: Alba Prieto Mora
Message: Even so, there are references in comments and test cases.

Date: 2026-02-01T09:13:00Z
Author: Sergio Vidal Cruz
Message: I will create an oldId-newId table for traceability and update references automatically.

Date: 2026-02-01T09:16:00Z
Author: Javier Ortega Campos
Message: What regression test do we propose?

Date: 2026-02-01T09:19:00Z
Author: Sergio Vidal Cruz
Message: Global uniqueness, exact correspondence with the source code, stability across runs and no broken references.

Date: 2026-02-01T09:22:00Z
Author: Mireia Soler Pons
Message: Add a test for codes with leading zeros and hyphens.

Date: 2026-02-01T09:25:00Z
Author: Alba Prieto Mora
Message: And another comparing all 62 identifiers with a municipality-approved list.

Date: 2026-02-01T09:28:00Z
Author: Nuria Castaño Rey
Message: I will block deployment of the next image until regression passes.

Date: 2026-02-01T09:31:00Z
Author: Javier Ortega Campos
Message: Sergio will prepare the patch today; Alba will validate the list, and Mireia will check that semantics do not change.

Date: 2026-02-01T09:35:00Z
Author: Alba Prieto Mora
Message: Agreed. I will mark the incident as internally critical, with no confirmed external impact.