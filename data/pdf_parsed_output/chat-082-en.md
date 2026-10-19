Date: 2026-07-13T10:00:00Z
Author: Andrés Beltrán Vega
Message: The corpus review found inconsistent relationships among policy versions.

Date: 2026-07-13T10:02:00Z
Author: Sergio Vidal Cruz
Message: There are 46 documents with previous_version, 39 with next_version and only 31 reciprocal pairs.

Date: 2026-07-13T10:04:00Z
Author: Lucía Navarro Gil
Message: Parallel translations are also being mixed with superseded versions.

Date: 2026-07-13T10:06:00Z
Author: Mireia Soler Pons
Message: We need to distinguish document version, translation, editorial correction and derivation.

Date: 2026-07-13T10:09:00Z
Author: Tomás Leal Guerra
Message: The retriever uses those relationships to order historical and current evidence.

Date: 2026-07-13T10:12:00Z
Author: Andrés Beltrán Vega
Message: Which rules do we adopt for previous_version and next_version?

Date: 2026-07-13T10:15:00Z
Author: Sergio Vidal Cruz
Message: Both must be reciprocal, belong to the same documentFamilyId and form no cycles.

Date: 2026-07-13T10:18:00Z
Author: Lucía Navarro Gil
Message: Translations will use parallel_version even when their publication dates differ.

Date: 2026-07-13T10:21:00Z
Author: Mireia Soler Pons
Message: A minor editorial correction may use derived_from and editorial changeType when it does not supersede the policy.

Date: 2026-07-13T10:24:00Z
Author: Tomás Leal Guerra
Message: What do we do with a consolidated policy integrating several amendments?

Date: 2026-07-13T10:27:00Z
Author: Mireia Soler Pons
Message: The consolidated version derives from source versions and may become currentVersion, but it does not erase the historical chain.

Date: 2026-07-13T10:30:00Z
Author: Sergio Vidal Cruz
Message: I will add supersedes and superseded_by for cases where a linear relationship is insufficient.

Date: 2026-07-13T10:33:00Z
Author: Andrés Beltrán Vega
Message: How do we validate dates?

Date: 2026-07-13T10:36:00Z
Author: Lucía Navarro Gil
Message: validFrom must precede validTo, and a superseded version cannot remain open except during a documented transition.

Date: 2026-07-13T10:39:00Z
Author: Tomás Leal Guerra
Message: The date must be evaluated by language when a translation takes effect later.

Date: 2026-07-13T10:42:00Z
Author: Sergio Vidal Cruz
Message: I will create validation for cycles, reciprocity, overlaps and multiple active documents.

Date: 2026-07-13T10:45:00Z
Author: Mireia Soler Pons
Message: We need a correction table for the 54 inconsistent links.

Date: 2026-07-13T10:48:00Z
Author: Lucía Navarro Gil
Message: Every correction will have a reason, evidence, owner and review date.

Date: 2026-07-13T10:51:00Z
Author: Andrés Beltrán Vega
Message: We will not change text or partitions; only versioned relations and metadata.

Date: 2026-07-13T10:55:00Z
Author: Sergio Vidal Cruz
Message: Agreed: reciprocal cycle-free relations, parallel translations, preserved historical chains and 54 corrected links before closure.