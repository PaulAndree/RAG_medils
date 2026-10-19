Date: 2026-05-12T10:00:00Z
Author: Andrés Beltrán Vega
Message: Obsolete versions still appear among the top results and displace current sources.

Date: 2026-05-12T10:02:00Z
Author: Tomás Leal Guerra
Message: The index treats all versions as independent documents with the same weight.

Date: 2026-05-12T10:04:00Z
Author: Lucía Navarro Gil
Message: We cannot hide old versions because they are necessary for historical questions.

Date: 2026-05-12T10:06:00Z
Author: Sergio Vidal Cruz
Message: Each document already has validFrom, validTo, supersedes and language.

Date: 2026-05-12T10:09:00Z
Author: Nuria Castaño Rey
Message: We can apply a pre-filter when the question has an identifiable date and language.

Date: 2026-05-12T10:12:00Z
Author: Andrés Beltrán Vega
Message: What happens when the question includes no date?

Date: 2026-05-12T10:15:00Z
Author: Tomás Leal Guerra
Message: By default, we would prioritize the current version while retaining historical versions in lower positions.

Date: 2026-05-12T10:18:00Z
Author: Lucía Navarro Gil
Message: The interface should indicate that earlier versions exist rather than simply hiding them.

Date: 2026-05-12T10:21:00Z
Author: Sergio Vidal Cruz
Message: We can return currentVersion=true and historicalAlternatives with identifiers and dates.

Date: 2026-05-12T10:24:00Z
Author: Nuria Castaño Rey
Message: That adds cost. Do we need to retrieve alternatives for every query?

Date: 2026-05-12T10:27:00Z
Author: Tomás Leal Guerra
Message: Only when the document group has more than one version or the query contains temporal signals.

Date: 2026-05-12T10:30:00Z
Author: Andrés Beltrán Vega
Message: How do we prevent the new English translation from answering questions predating its publication?

Date: 2026-05-12T10:33:00Z
Author: Lucía Navarro Gil
Message: The filter must use language-specific validity rather than inheriting the Spanish version date.

Date: 2026-05-12T10:36:00Z
Author: Sergio Vidal Cruz
Message: I will add documentFamilyId to group versions and translations without conflating them.

Date: 2026-05-12T10:39:00Z
Author: Tomás Leal Guerra
Message: I will test three strategies: hard filtering, temporal reranking and a combination of both.

Date: 2026-05-12T10:42:00Z
Author: Nuria Castaño Rey
Message: We need an explainable output showing which version was used and why.

Date: 2026-05-12T10:45:00Z
Author: Andrés Beltrán Vega
Message: Include tests with a current rule, historical question, missing date and translation not yet available.

Date: 2026-05-12T10:48:00Z
Author: Lucía Navarro Gil
Message: Superseded versions may be cited but must never be presented as current answers without warning.

Date: 2026-05-12T10:51:00Z
Author: Tomás Leal Guerra
Message: I will prepare validation results separated by query type and strategy.

Date: 2026-05-12T10:55:00Z
Author: Andrés Beltrán Vega
Message: Agreed: current-version priority by default, date and language filters when available and explicit access to historical evidence.