Date: 2026-05-05T09:10:00Z
Author: Javier Ortega Campos
Message: We need to finalize the error codes before the municipality begins integration testing.

Date: 2026-05-05T09:12:00Z
Author: Sergio Vidal Cruz
Message: At present, the API returns 400 for invalid filters, missing data and incompatible parameters.

Date: 2026-05-05T09:14:00Z
Author: Alba Prieto Mora
Message: That makes it impossible to know whether the procedure is incomplete or the query is malformed.

Date: 2026-05-05T09:16:00Z
Author: Luis Noguera Sáez
Message: The municipal team needs clear messages for citizen service and technical support.

Date: 2026-05-05T09:19:00Z
Author: Mireia Soler Pons
Message: I propose separating invalid-filter, missing-required-parameter, data-not-available and incompatible-parameters.

Date: 2026-05-05T09:22:00Z
Author: Nuria Castaño Rey
Message: We also need to distinguish recoverable errors from errors that should not be retried.

Date: 2026-05-05T09:25:00Z
Author: Sergio Vidal Cruz
Message: 429 and 503 can include retryAfter; 400 and 404 should not trigger automatic retries.

Date: 2026-05-05T09:28:00Z
Author: Javier Ortega Campos
Message: Do we use standard HTTP codes plus an internal reasonCode?

Date: 2026-05-05T09:31:00Z
Author: Sergio Vidal Cruz
Message: Yes. The response would contain status, reasonCode, message, details, requestId and documentationUrl.

Date: 2026-05-05T09:34:00Z
Author: Alba Prieto Mora
Message: The message should be understandable, while details may contain the field and rule that failed.

Date: 2026-05-05T09:37:00Z
Author: Mireia Soler Pons
Message: reasonCode values remain in English, while visible messages are translated.

Date: 2026-05-05T09:40:00Z
Author: Luis Noguera Sáez
Message: I need Spanish and English examples for the six most frequent errors.

Date: 2026-05-05T09:43:00Z
Author: Nuria Castaño Rey
Message: What do we do when an external dependency fails during a query?

Date: 2026-05-05T09:46:00Z
Author: Sergio Vidal Cruz
Message: We will return 503 dependency-unavailable and log the affected system without exposing internal details.

Date: 2026-05-05T09:49:00Z
Author: Javier Ortega Campos
Message: What if the procedure exists but one mandatory field is not yet available?

Date: 2026-05-05T09:52:00Z
Author: Alba Prieto Mora
Message: It should be 200 with partial status when the record can still be displayed, and data-not-available only when the query requires that field.

Date: 2026-05-05T09:55:00Z
Author: Mireia Soler Pons
Message: That prevents incomplete data quality from becoming a total API failure.

Date: 2026-05-05T09:58:00Z
Author: Luis Noguera Sáez
Message: The municipality also wants a short recommended-action text.

Date: 2026-05-05T10:01:00Z
Author: Sergio Vidal Cruz
Message: I will add userAction for recoverable errors and cases requiring query correction.

Date: 2026-05-05T10:05:00Z
Author: Javier Ortega Campos
Message: Agreed: standard HTTP codes, stable reasonCode values, bilingual messages, retryAfter where applicable and separation between invalid queries and unavailable data.