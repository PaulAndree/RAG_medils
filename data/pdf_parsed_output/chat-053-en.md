Date: 2026-05-23T09:30:00Z
Author: Sergio Vidal Cruz
Message: The full regression finished overnight: 412 tests passed and 11 failed.

Date: 2026-05-23T09:32:00Z
Author: Javier Ortega Campos
Message: Do the failures affect identifiers, SHACL rules or the API?

Date: 2026-05-23T09:34:00Z
Author: Sergio Vidal Cruz
Message: Three concern historical identifiers, five concern SHACL exceptions and three concern error messages.

Date: 2026-05-23T09:36:00Z
Author: Alba Prieto Mora
Message: The identifier failures occur because two test cases still use the value from before the migration table.

Date: 2026-05-23T09:39:00Z
Author: Mireia Soler Pons
Message: Is the third failure genuine?

Date: 2026-05-23T09:42:00Z
Author: Alba Prieto Mora
Message: Yes. One procedure lost a leading zero during a manual import.

Date: 2026-05-23T09:45:00Z
Author: Nuria Castaño Rey
Message: That should block the image; normalization must preserve the exact literal.

Date: 2026-05-23T09:48:00Z
Author: Sergio Vidal Cruz
Message: The five SHACL exception failures involve non-applicable deadlines without a justification code.

Date: 2026-05-23T09:51:00Z
Author: Mireia Soler Pons
Message: Then they are data errors, not rule errors.

Date: 2026-05-23T09:54:00Z
Author: Javier Ortega Campos
Message: Who can complete the justifications?

Date: 2026-05-23T09:57:00Z
Author: Alba Prieto Mora
Message: Four depend on municipal evidence already received; one needs legal confirmation.

Date: 2026-05-23T10:00:00Z
Author: Sergio Vidal Cruz
Message: The three API failures are differences between Spanish and English message text; the reasonCode is correct.

Date: 2026-05-23T10:03:00Z
Author: Mireia Soler Pons
Message: We should validate equivalent meaning rather than character-for-character literal translation.

Date: 2026-05-23T10:06:00Z
Author: Nuria Castaño Rey
Message: I can change those tests to compare templates and mandatory fields instead of full sentences.

Date: 2026-05-23T10:09:00Z
Author: Javier Ortega Campos
Message: When can we repeat regression?

Date: 2026-05-23T10:12:00Z
Author: Sergio Vidal Cruz
Message: This afternoon we can correct identifiers and templates. The justifications will be ready tomorrow except for the legal case.

Date: 2026-05-23T10:15:00Z
Author: Alba Prieto Mora
Message: The legal case can remain blocked and isolated without preventing testing of the other 61 procedures.

Date: 2026-05-23T10:18:00Z
Author: Mireia Soler Pons
Message: But the final delivery will still require all 62 procedures with no mandatory failures.

Date: 2026-05-23T10:21:00Z
Author: Nuria Castaño Rey
Message: I will retain the image as candidate-not-approved until the second run passes.

Date: 2026-05-23T10:25:00Z
Author: Javier Ortega Campos
Message: Agreed: correct all eleven failures, rerun regression tomorrow and do not approve the image until all 62 procedures are valid.