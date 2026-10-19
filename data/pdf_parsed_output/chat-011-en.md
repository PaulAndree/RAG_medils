Date: 2026-02-17T09:10:00Z
Author: Lucía Navarro Gil
Message: I want to review the false positives found in historical names before we finalize the human-review workflow.

Date: 2026-02-17T09:12:00Z
Author: Diego Ramos León
Message: The latest sample contained 240 mentions and achieved 84 percent overall precision.

Date: 2026-02-17T09:14:00Z
Author: Mateo Ruiz Serra
Message: Errors are concentrated in surnames that are also places, institutions or work titles.

Date: 2026-02-17T09:16:00Z
Author: Eva Calderón Gil
Message: There are also historical family names that the system links to specific individuals.

Date: 2026-02-17T09:19:00Z
Author: Yara Ben Salem
Message: Bilingual records contain variants with and without particles such as de, del or van.

Date: 2026-02-17T09:22:00Z
Author: Lucía Navarro Gil
Message: Which threshold are we using now?

Date: 2026-02-17T09:25:00Z
Author: Diego Ramos León
Message: Automatic linking was set to 0.72. At that value, we obtain too many incorrect links.

Date: 2026-02-17T09:28:00Z
Author: Mateo Ruiz Serra
Message: If we raise it to 0.82, precision improves, but automatic coverage decreases.

Date: 2026-02-17T09:31:00Z
Author: Eva Calderón Gil
Message: I prefer fewer automatic links and a clear review queue, especially for personal names.

Date: 2026-02-17T09:34:00Z
Author: Yara Ben Salem
Message: We can use 0.82 for acceptance, 0.65 to 0.82 for review and below 0.65 as unresolved.

Date: 2026-02-17T09:37:00Z
Author: Diego Ramos León
Message: That division matches the validation results we saw last week.

Date: 2026-02-17T09:40:00Z
Author: Lucía Navarro Gil
Message: What evidence will the reviewer see?

Date: 2026-02-17T09:43:00Z
Author: Mateo Ruiz Serra
Message: The mention, context, record dates, entity type and no more than three candidates.

Date: 2026-02-17T09:46:00Z
Author: Eva Calderón Gil
Message: Add the source of the authorized name and any relevant archival relationship.

Date: 2026-02-17T09:49:00Z
Author: Yara Ben Salem
Message: The interface should display language variants without treating them as different entities.

Date: 2026-02-17T09:52:00Z
Author: Diego Ramos León
Message: I will create negative rules for terms that are often places or institutions when person signals are absent.

Date: 2026-02-17T09:55:00Z
Author: Lucía Navarro Gil
Message: Can we review a sample before applying the new threshold to the full batch?

Date: 2026-02-17T09:58:00Z
Author: Mateo Ruiz Serra
Message: Yes. I propose one hundred mentions stratified by language, century and ambiguity type.

Date: 2026-02-17T10:01:00Z
Author: Eva Calderón Gil
Message: The archive can review cases involving families, historical institutions and names with particles.

Date: 2026-02-17T10:05:00Z
Author: Lucía Navarro Gil
Message: Agreed: 0.82 for automatic linking, 0.65–0.82 for human review, and a one-hundred-case sample before full deployment.