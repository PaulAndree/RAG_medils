ORION FINAL REPORT AND REUSABLE DATA PACKAGE V1.0

1. Summary

ORION consolidated information about projects, publications, datasets, software, and research profiles within the NEXUS group. The final result is a reusable package with stable identifiers, verified relations, provenance, and sufficient documentation for controlled incorporation into ARIADNA and other internal systems.

The package does not reproduce every field from the original system. Internal metrics, audit records, personal addresses, review notes, and attributes without a clear purpose in the reusable product are excluded. Included fields retain their source system and extraction date.

2. Scope

The delivery contains tables for people, affiliations, projects, publications, datasets, software, organizations, and relations. It also includes identity tables, vocabularies, manifests, checksums, transformation rules, and an exclusion inventory.

Eight profiles remain outside the package because their identity could not be resolved with sufficient evidence. Fifteen historical records are retained as controlled distractors and explicitly marked as superseded versions or earlier states.

3. Principles

Reuse is based on traceability, minimization, version control, and separation between source and derived data. An inferred relation does not replace evidence. Profile merges require a recorded decision and retain earlier identifiers through equivalence relations.

Delivery section 1

Table 1, covering people, contains name, variants, identifiers, affiliations, and provenance. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 2

Table 2, covering affiliations, contains organization, role, start date, end date, and source. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 3

Table 3, covering projects, contains title, acronym, period, funding, status, and participants. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 4

Table 4, covering publications, contains title, date, identifiers, authorship, venue, and version. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 5

Table 5, covering datasets, contains title, version, licence, owners, repository, and relations. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 6

Table 6, covering software, contains name, version, repository, licence, authors, and dependencies. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 7

Table 7, covering organizations, contains official name, variants, type, country, and period. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 8

Table 8, covering relations, contains type, subject, object, date, provenance, and confidence. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 9

Reuse component 1 covers identity table. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 10

Reuse component 2 covers historical redirects. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 11

Reuse component 3 covers field provenance. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 12

Reuse component 4 covers version control. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 13

Reuse component 5 covers superseded records. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 14

Reuse component 6 covers bilingual validation. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 15

Reuse component 7 covers licences and restrictions. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 16

Reuse component 8 covers checksums. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 17

Reuse component 9 covers delivery manifest. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 18

Reuse component 10 covers restoration tests. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 19

Quality test 1 searches for duplicate identifiers. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 20

Quality test 2 searches for orphaned bilingual pairs. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 21

Quality test 3 searches for relations without a target. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 22

Quality test 4 searches for version cycles. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 23

Quality test 5 searches for incompatible affiliation dates. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 24

Quality test 6 searches for publications without an author. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 25

Quality test 7 searches for software without a repository or licence. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 26

Quality test 8 searches for datasets without an owner. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 27

Table 1, covering people, contains name, variants, identifiers, affiliations, and provenance. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 28

Table 2, covering affiliations, contains organization, role, start date, end date, and source. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 29

Table 3, covering projects, contains title, acronym, period, funding, status, and participants. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 30

Table 4, covering publications, contains title, date, identifiers, authorship, venue, and version. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 31

Table 5, covering datasets, contains title, version, licence, owners, repository, and relations. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 32

Table 6, covering software, contains name, version, repository, licence, authors, and dependencies. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 33

Table 7, covering organizations, contains official name, variants, type, country, and period. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 34

Table 8, covering relations, contains type, subject, object, date, provenance, and confidence. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 35

Reuse component 1 covers identity table. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 36

Reuse component 2 covers historical redirects. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 37

Reuse component 3 covers field provenance. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 38

Reuse component 4 covers version control. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 39

Reuse component 5 covers superseded records. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 40

Reuse component 6 covers bilingual validation. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 41

Reuse component 7 covers licences and restrictions. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 42

Reuse component 8 covers checksums. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 43

Reuse component 9 covers delivery manifest. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 44

Reuse component 10 covers restoration tests. It has an owner, version, acceptance criterion, and evidence. Checks run from a clean copy and compare counts, identifiers, and relations. An unexplained difference blocks delivery. Where a correction changes meaning, a new version is created and the earlier one remains as history. Spanish and English versions use the same base identifiers.

Delivery section 45

Quality test 1 searches for duplicate identifiers. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 46

Quality test 2 searches for orphaned bilingual pairs. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 47

Quality test 3 searches for relations without a target. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 48

Quality test 4 searches for version cycles. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 49

Quality test 5 searches for incompatible affiliation dates. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 50

Quality test 6 searches for publications without an author. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 51

Quality test 7 searches for software without a repository or licence. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 52

Quality test 8 searches for datasets without an owner. The report records case count, affected identifiers, severity, and action. Critical errors must be zero. Warnings are accepted only with a documented exception. A correction is executed through versioned scripts and checked not to alter records outside scope. The reviewer signs the result and links the evidence.

Delivery section 53

Table 1, covering people, contains name, variants, identifiers, affiliations, and provenance. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 54

Table 2, covering affiliations, contains organization, role, start date, end date, and source. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 55

Table 3, covering projects, contains title, acronym, period, funding, status, and participants. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 56

Table 4, covering publications, contains title, date, identifiers, authorship, venue, and version. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.

Delivery section 57

Table 5, covering datasets, contains title, version, licence, owners, repository, and relations. Every row uses a stable identifier and retains the source identifier where available. Normalized fields do not replace the original literal. Open, approximate, or pending dates are explicitly represented. The table includes cardinality and validation rules. Records failing criteria are isolated in a report and do not disappear from counts.