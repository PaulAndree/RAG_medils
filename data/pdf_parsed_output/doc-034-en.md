LUMEN SECOND INGESTION AND DATA QUALITY REPORT V1.0

1. Summary

The second LUMEN ingestion added 1,180 municipal correspondence letters and updated records from photography, posters, and person authorities. The batch was processed after applying terminology guide v1.1, the approximate-date schema, and corrections arising from the first linking evaluation.

The run received 1,180 letter records and 1,164 digital files. Sixteen letters had no associated image but retained authorized metadata. The system processed every record and isolated errors without silently reducing counts.

2. Results

Initial validation identified forty-seven non-normalized dates, twenty-nine ambiguous senders, eighteen place names without a sufficient candidate, twelve files with checksums differing from the manifest, and nine pending rights values. The twelve files were replaced with verified copies before processing continued.

After correction, zero critical errors remained. Twenty-four person mentions remain unlinked, eleven places remain open, and nine objects remain outside the demonstrator because rights are pending.

3. Method

The pipeline ran receipt, checksum, profiling, normalization, mapping, validation, loading, and post-load checks. Every stage retains its version, counts, and results. Reingestion was limited to failed records where the rest of the batch had already been accepted.

Ingestion result 1

Quality analysis 1, dates, covers approximate expressions and open intervals. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 2

Quality analysis 2, people, covers namesakes, initials, and variants. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 3

Quality analysis 3, places, covers historical names and namesake localities. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 4

Quality analysis 4, rights, covers objects without a decision or with limited use. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 5

Quality analysis 5, files, covers absence, checksums, and formats. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 6

Quality analysis 6, terminology, covers creator, author, and producer roles. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 7

Quality analysis 7, bilingualism, covers labels, definitions, and pairs. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 8

Quality analysis 8, provenance, covers source, transformation, and review. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 9

Post-load comparison verified 1,180 records, 1,164 files, 1,180 source-identifier pairs, and 2,360 language records. No orphaned bilingual pairs, duplicate identifiers, or version cycles were identified.

Ingestion result 10

The public load was generated from a positive list of 1,131 approved letters. Forty records remain internal only, and nine are pending. Counts and reasons appear in the manifest.

Ingestion result 11

The recommendation is to add an automated checksum-change test, extend the place vocabulary, and retain the conservative person-link threshold. The next ingestion should reuse this set as regression data.

Ingestion result 12

Quality analysis 1, dates, covers approximate expressions and open intervals. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 13

Quality analysis 2, people, covers namesakes, initials, and variants. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 14

Quality analysis 3, places, covers historical names and namesake localities. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 15

Quality analysis 4, rights, covers objects without a decision or with limited use. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 16

Quality analysis 5, files, covers absence, checksums, and formats. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 17

Quality analysis 6, terminology, covers creator, author, and producer roles. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 18

Quality analysis 7, bilingualism, covers labels, definitions, and pairs. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 19

Quality analysis 8, provenance, covers source, transformation, and review. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 20

Post-load comparison verified 1,180 records, 1,164 files, 1,180 source-identifier pairs, and 2,360 language records. No orphaned bilingual pairs, duplicate identifiers, or version cycles were identified.

Ingestion result 21

The public load was generated from a positive list of 1,131 approved letters. Forty records remain internal only, and nine are pending. Counts and reasons appear in the manifest.

Ingestion result 22

The recommendation is to add an automated checksum-change test, extend the place vocabulary, and retain the conservative person-link threshold. The next ingestion should reuse this set as regression data.

Ingestion result 23

Quality analysis 1, dates, covers approximate expressions and open intervals. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 24

Quality analysis 2, people, covers namesakes, initials, and variants. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 25

Quality analysis 3, places, covers historical names and namesake localities. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 26

Quality analysis 4, rights, covers objects without a decision or with limited use. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 27

Quality analysis 5, files, covers absence, checksums, and formats. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 28

Quality analysis 6, terminology, covers creator, author, and producer roles. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 29

Quality analysis 7, bilingualism, covers labels, definitions, and pairs. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 30

Quality analysis 8, provenance, covers source, transformation, and review. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 31

Post-load comparison verified 1,180 records, 1,164 files, 1,180 source-identifier pairs, and 2,360 language records. No orphaned bilingual pairs, duplicate identifiers, or version cycles were identified.

Ingestion result 32

The public load was generated from a positive list of 1,131 approved letters. Forty records remain internal only, and nine are pending. Counts and reasons appear in the manifest.

Ingestion result 33

The recommendation is to add an automated checksum-change test, extend the place vocabulary, and retain the conservative person-link threshold. The next ingestion should reuse this set as regression data.

Ingestion result 34

Quality analysis 1, dates, covers approximate expressions and open intervals. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 35

Quality analysis 2, people, covers namesakes, initials, and variants. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 36

Quality analysis 3, places, covers historical names and namesake localities. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.

Ingestion result 37

Quality analysis 4, rights, covers objects without a decision or with limited use. The rule records the source value, transformed value, severity, action, and owner. Unresolvable cases remain open and are not replaced by an inference. A correction runs through the pipeline and is compared with the earlier report. The manual sample contains objects from several collections and both languages.