Date: 2026-06-14T09:10:00Z
Author: Andrés Beltrán Vega
Message: Federated search is too slow when combining the local catalogue with the partner. We need to compare traces and optimizations.

Date: 2026-06-14T09:12:00Z
Author: Nuria Castaño Rey
Message: Across 120 queries, local median latency is 0.8 seconds and federated median latency is 2.7 seconds.

Date: 2026-06-14T09:14:00Z
Author: Bruno Silva
Message: At our end, the query averages 1.1 seconds; the remaining time appears to be negotiation and merging.

Date: 2026-06-14T09:16:00Z
Author: Sergio Vidal Cruz
Message: I see two authentication calls per query and a full schema download in every session.

Date: 2026-06-14T09:19:00Z
Author: Carmen Rey Palacios
Message: Can the cache be reused without retaining consumption data or individual results?

Date: 2026-06-14T09:22:00Z
Author: Nuria Castaño Rey
Message: Yes. We can cache the token, schema and vocabulary, but not detailed responses.

Date: 2026-06-14T09:25:00Z
Author: Inés Ferrer Lozano
Message: Scientific queries often repeat facilities, periods and variables within the same session.

Date: 2026-06-14T09:28:00Z
Author: Andrés Beltrán Vega
Message: What is the current p95?

Date: 2026-06-14T09:31:00Z
Author: Nuria Castaño Rey
Message: Local p95 is 1.6 seconds and federated p95 is 6.4 seconds.

Date: 2026-06-14T09:34:00Z
Author: Bruno Silva
Message: We can add a batch operation to resolve several variables in one request.

Date: 2026-06-14T09:37:00Z
Author: Sergio Vidal Cruz
Message: That reduces calls, but we need limits to prevent oversized queries.

Date: 2026-06-14T09:40:00Z
Author: Carmen Rey Palacios
Message: The limit should be expressed by period, facilities and authorized purpose, not only row count.

Date: 2026-06-14T09:43:00Z
Author: Inés Ferrer Lozano
Message: For evaluation, a typical query covers up to six facilities and thirty days.

Date: 2026-06-14T09:46:00Z
Author: Nuria Castaño Rey
Message: I propose caching the schema for six hours, the token for fifty minutes and using batch for up to ten variables.

Date: 2026-06-14T09:49:00Z
Author: Bruno Silva
Message: We can also compress the response and return only requested fields.

Date: 2026-06-14T09:52:00Z
Author: Sergio Vidal Cruz
Message: I will add separate traces for authentication, resolution, transfer and merging.

Date: 2026-06-14T09:55:00Z
Author: Andrés Beltrán Vega
Message: Which performance target do we set?

Date: 2026-06-14T09:58:00Z
Author: Nuria Castaño Rey
Message: Median below 1.8 seconds and p95 below 4 seconds for the typical query.

Date: 2026-06-14T10:01:00Z
Author: Carmen Rey Palacios
Message: The cache will be invalidated when permissions, schema or certificate change.

Date: 2026-06-14T10:05:00Z
Author: Andrés Beltrán Vega
Message: Agreed: limited caching, controlled batching, compression and phase-level traces; we will repeat the 120 queries before the partner review.