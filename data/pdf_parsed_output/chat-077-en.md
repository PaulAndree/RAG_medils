Date: 2026-05-29T09:20:00Z
Author: Lucía Navarro Gil
Message: The review of 120 answers found 34 incomplete or insufficient citations.

Date: 2026-05-29T09:22:00Z
Author: Andrés Beltrán Vega
Message: What do we consider incomplete?

Date: 2026-05-29T09:24:00Z
Author: Lucía Navarro Gil
Message: A citation that supports part of the answer but not the date, exception, amount or main condition.

Date: 2026-05-29T09:26:00Z
Author: Tomás Leal Guerra
Message: Nineteen cases retrieved the correct passage, but the generator cited only the first clause.

Date: 2026-05-29T09:29:00Z
Author: Pablo Herrero Sanz
Message: Eight answers used two documents and cited only one.

Date: 2026-05-29T09:32:00Z
Author: Sergio Vidal Cruz
Message: The remaining seven cite a superseded version even though the answer uses the current one.

Date: 2026-05-29T09:35:00Z
Author: Mireia Soler Pons
Message: The citation should identify document, version, language and passage, not only a generic link.

Date: 2026-05-29T09:38:00Z
Author: Andrés Beltrán Vega
Message: Can we correct this through instructions, or do we need to change retriever output?

Date: 2026-05-29T09:41:00Z
Author: Tomás Leal Guerra
Message: Both. The retriever should group complementary evidence, and the generator should cite every verifiable claim.

Date: 2026-05-29T09:44:00Z
Author: Lucía Navarro Gil
Message: We do not want a citation after every word. We need a readable rule.

Date: 2026-05-29T09:47:00Z
Author: Pablo Herrero Sanz
Message: One citation per sentence or claim block sharing the same evidence, and multiple citations when sources are combined.

Date: 2026-05-29T09:50:00Z
Author: Sergio Vidal Cruz
Message: The schema can store supportedClaims and citationTargets to validate coverage.

Date: 2026-05-29T09:53:00Z
Author: Mireia Soler Pons
Message: For temporal validity, the citation must include the source establishing the date, even if the rule appears in another passage.

Date: 2026-05-29T09:56:00Z
Author: Andrés Beltrán Vega
Message: How do we score correct answers with partial citations?

Date: 2026-05-29T09:59:00Z
Author: Lucía Navarro Gil
Message: Content accuracy may be correct, but citation-completeness should fail separately.

Date: 2026-05-29T10:02:00Z
Author: Tomás Leal Guerra
Message: I will add an automatic check covering mentioned entities, dates, figures and exceptions.

Date: 2026-05-29T10:05:00Z
Author: Pablo Herrero Sanz
Message: I will prepare twenty examples: complete, incomplete, redundant and wrong-version citations.

Date: 2026-05-29T10:08:00Z
Author: Sergio Vidal Cruz
Message: The seven superseded-version cases will remain blocked until the document filter is applied.

Date: 2026-05-29T10:11:00Z
Author: Andrés Beltrán Vega
Message: We will rerun all 120 answers and compare accuracy, coverage and readability.

Date: 2026-05-29T10:15:00Z
Author: Lucía Navarro Gil
Message: Agreed: citations per verifiable claim block, separate coverage scoring, multiple sources where needed and explicit version and language.