Date: 2026-01-20T08:55:00Z
Author: Javier Ortega Campos
Message: Last night's SHACL run produced 137 violations. We need to separate real errors from false positives.

Date: 2026-01-20T08:57:00Z
Author: Sergio Vidal Cruz
Message: Eighty-nine are concentrated in cardinality rules for deadlines and documentation.

Date: 2026-01-20T08:59:00Z
Author: Alba Prieto Mora
Message: Some procedures have no deadline because they depend on an external decision. The absence is documented and is not an error.

Date: 2026-01-20T09:01:00Z
Author: Mireia Soler Pons
Message: The current rule requires exactly one deadline. It should allow zero when a non-applicable justification exists.

Date: 2026-01-20T09:04:00Z
Author: Nuria Castaño Rey
Message: Does that turn a requirement into an exception that is too broad?

Date: 2026-01-20T09:07:00Z
Author: Mireia Soler Pons
Message: We can require the exception to have a controlled code, provenance note and validating unit.

Date: 2026-01-20T09:10:00Z
Author: Sergio Vidal Cruz
Message: There are another 22 warnings because documentation appears as an empty list rather than a missing value.

Date: 2026-01-20T09:13:00Z
Author: Alba Prieto Mora
Message: That is a transformation problem. An empty list does not explain whether documentation is not required or data is missing.

Date: 2026-01-20T09:16:00Z
Author: Javier Ortega Campos
Message: Then we do not relax that rule; we correct the transformation.

Date: 2026-01-20T09:19:00Z
Author: Nuria Castaño Rey
Message: I also see twelve date-format errors. The source uses day/month/year as text.

Date: 2026-01-20T09:22:00Z
Author: Sergio Vidal Cruz
Message: I can normalize them to ISO and retain the original literal in provenance.

Date: 2026-01-20T09:25:00Z
Author: Mireia Soler Pons
Message: Fourteen cases of multiple responsible units remain. Some procedures have an instructing unit and a deciding unit.

Date: 2026-01-20T09:28:00Z
Author: Alba Prieto Mora
Message: The shape should distinguish roles rather than limiting the total to one.

Date: 2026-01-20T09:31:00Z
Author: Javier Ortega Campos
Message: How many genuine violations do we expect after these adjustments?

Date: 2026-01-20T09:34:00Z
Author: Sergio Vidal Cruz
Message: Approximately thirty-four: empty lists, invalid dates and units without roles.

Date: 2026-01-20T09:37:00Z
Author: Nuria Castaño Rey
Message: I propose running two profiles: strict for delivery and diagnostic for development.

Date: 2026-01-20T09:40:00Z
Author: Mireia Soler Pons
Message: Agreed, provided both profiles share rule identifiers and version information.

Date: 2026-01-20T09:43:00Z
Author: Alba Prieto Mora
Message: I will prepare examples of a valid exception and genuinely missing data to avoid different interpretations.

Date: 2026-01-20T09:46:00Z
Author: Javier Ortega Campos
Message: The deadline rule will be adjusted with a controlled exception; empty documentation remains an error, and units will use roles.

Date: 2026-01-20T09:50:00Z
Author: Sergio Vidal Cruz
Message: I will run validation again this afternoon and publish details by rule, procedure and severity.