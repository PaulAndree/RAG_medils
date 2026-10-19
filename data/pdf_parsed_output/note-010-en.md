Five minimum patterns are proposed for archival dates: exact date, known year, range, date before or after a boundary, and approximate date. Each must preserve the original source wording in addition to a normalized representation that supports queries.

Examples:
- “14 May 1932”: exact date.
- “1936”: an interval from 1 January to 31 December 1936, with year-level precision.
- “1930–1934”: closed range.
- “before 1925”: open upper boundary.
- “c. 1948”: estimated interval from 1947 to 1949, marked as approximate.

An approximate date must not be converted into an exact date during ingestion. The width used for “circa” must be configurable by collection and recorded in provenance. Mateo will prepare examples involving letters, photographs, and posters to validate that the model covers the Regional Archive's cases.