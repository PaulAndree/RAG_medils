Date: 2026-02-13T10:15:00Z
Author: Lucía Navarro Gil
Message: We need to decide how to represent dates such as circa 1910, before 1936 and the 1920s.

Date: 2026-02-13T10:17:00Z
Author: Mateo Ruiz Serra
Message: The current proposal stores only an approximate year and loses too much information.

Date: 2026-02-13T10:19:00Z
Author: Mireia Soler Pons
Message: I suggest separating original expression, normalized interval, uncertainty type and provenance.

Date: 2026-02-13T10:21:00Z
Author: Eva Calderón Gil
Message: The archive needs to preserve the exact expression from the document or finding aid.

Date: 2026-02-13T10:24:00Z
Author: Diego Ramos León
Message: For search, an interval allows records to be retrieved even when the original expression varies.

Date: 2026-02-13T10:27:00Z
Author: Yara Ben Salem
Message: The bilingual interface must also avoid translating uncertainty as though it were precision.

Date: 2026-02-13T10:30:00Z
Author: Lucía Navarro Gil
Message: Which interval do we assign to circa 1910?

Date: 2026-02-13T10:33:00Z
Author: Mateo Ruiz Serra
Message: We can use 1908–1912 as an initial convention, but it must be identified as a project rule rather than an archival fact.

Date: 2026-02-13T10:36:00Z
Author: Mireia Soler Pons
Message: The width should be configurable by collection. Some use approximately with a different margin.

Date: 2026-02-13T10:39:00Z
Author: Eva Calderón Gil
Message: I agree. Provenance must indicate whether the interval comes from the document, the archivist or an automatic rule.

Date: 2026-02-13T10:42:00Z
Author: Diego Ramos León
Message: For before 1936, we need an open bound rather than an invented starting year.

Date: 2026-02-13T10:45:00Z
Author: Mireia Soler Pons
Message: The model can use end=1935-12-31 and openStart=true.

Date: 2026-02-13T10:48:00Z
Author: Yara Ben Salem
Message: The interface would display Before 1936 without necessarily exposing the technical bound value.

Date: 2026-02-13T10:51:00Z
Author: Mateo Ruiz Serra
Message: For the 1920s, the interval would be 1920-01-01 to 1929-12-31 with uncertaintyType=decade.

Date: 2026-02-13T10:54:00Z
Author: Eva Calderón Gil
Message: How do we represent 1910 or 1911?

Date: 2026-02-13T10:57:00Z
Author: Diego Ramos León
Message: As a discrete set if we want precision, or as an interval with nonContinuous=true.

Date: 2026-02-13T11:00:00Z
Author: Mireia Soler Pons
Message: I prefer a set of candidate values; an interval would imply intermediate dates as well.

Date: 2026-02-13T11:03:00Z
Author: Lucía Navarro Gil
Message: We need validation rules so that the original expression never disappears during normalization.

Date: 2026-02-13T11:06:00Z
Author: Mateo Ruiz Serra
Message: I will prepare twenty examples covering exact date, approximate date, interval, open bound, decade and alternatives.

Date: 2026-02-13T11:10:00Z
Author: Lucía Navarro Gil
Message: Agreed: we retain the literal, normalization, type, method and source; automatic margins will be configurable and explicit.