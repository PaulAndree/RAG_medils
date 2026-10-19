APPROXIMATE DATE AND HISTORICAL PLACE-NAME SCHEMA V0.8

This schema defines how non-exact dates and place names changing over time are represented. It does not replace archival description: source wording is retained and a structured interpretation is added for search.

Every date contains `originalText`, `earliest`, `latest`, `precision`, and `interpretationSource`. An exact date uses the same value for earliest and latest. “1947” represents the complete year. “Spring 1947” retains the literal and uses a seasonal interval; it is not displayed as one day. “c. 1930” uses approximate precision. “Before 1952” has an upper bound and open beginning.

The interface displays the original literal first. Calculated dates must not appear as transcriptions. Where two sources disagree, both assertions and their provenance are retained.

Every place has a stable identifier. Names are stored with language, type, start, and end of use. A historical variant participates in search but leads to the same record. Namesake places must not be merged; disambiguation uses type, jurisdiction, collection, and related places.

The system checks that earliest is not later than latest, every interpretation retains originalText, and precision belongs to the vocabulary. ES/EN pairs share identifiers and relations.

Example 1

“Puerto Viejo, 3 May 1936” is represented as an exact date and a place mention using the name current at the time. “Near Santa Marina, around 1920” retains uncertainty in date and place. “North District, now San Gabriel” creates two temporal names for one entity only where the archive confirms administrative continuity.

Example 2

Approximate coordinates support review but do not replace documentary evidence. A spelling change does not create a new entity; an administrative split may do so where institutional identity changes. Mentions without sufficient context remain unlinked.

Example 3

Every interpretation records its rule, version, and reviewer. A change creates a new version and does not overwrite the literal. Pending cases remain outside exact filters until resolved.

Example 4

“Puerto Viejo, 3 May 1936” is represented as an exact date and a place mention using the name current at the time. “Near Santa Marina, around 1920” retains uncertainty in date and place. “North District, now San Gabriel” creates two temporal names for one entity only where the archive confirms administrative continuity.

Example 5

Approximate coordinates support review but do not replace documentary evidence. A spelling change does not create a new entity; an administrative split may do so where institutional identity changes. Mentions without sufficient context remain unlinked.

Example 6

Every interpretation records its rule, version, and reviewer. A change creates a new version and does not overwrite the literal. Pending cases remain outside exact filters until resolved.

Example 7

“Puerto Viejo, 3 May 1936” is represented as an exact date and a place mention using the name current at the time. “Near Santa Marina, around 1920” retains uncertainty in date and place. “North District, now San Gabriel” creates two temporal names for one entity only where the archive confirms administrative continuity.

Example 8

Approximate coordinates support review but do not replace documentary evidence. A spelling change does not create a new entity; an administrative split may do so where institutional identity changes. Mentions without sufficient context remain unlinked.