HISTORICAL-PERSON LINKING EVALUATION REPORT

1. Objective

This report evaluates person linking in descriptions of photography, correspondence, posters, minutes, and inventories. The objective is not to resolve every mention but to obtain links precise enough that navigation and identity questions do not propagate errors.

The system generates candidates from the name and uses occupation, dates, places, organizations, collections, and relations. High-confidence cases are accepted; intermediate cases are reviewed; insufficient cases remain unlinked. An open mention is preferable to a false merge.

2. Set

The set contains six hundred mentions. Three hundred have a reference entity, 180 concern known but ambiguous people, and 120 cannot be resolved using available sources. It includes frequent names, initials, variants, transcription errors, collective entities, and role changes.

Two people reviewed every case. Disagreements were adjudicated with support from the Regional Archive. The split is made by entity rather than mention to avoid references to one person appearing in both development and test.

3. Method

Candidate generation normalizes case, punctuation, abbreviations, and accents while retaining the literal. It retrieves up to twenty candidates and calculates name similarity, temporal compatibility, occupation, place, organization, and relations.

Above 0.88 an automatic link is proposed; from 0.65 to 0.88 the case enters review; below that it remains unlinked. Temporal incompatibility blocks automatic acceptance.

4. Results

Overall precision is 0.94 and coverage over resolvable cases is 0.78. Automatic precision reaches 0.98. Twenty-nine percent enter review, and twenty-one percent remain unlinked. Lowering the threshold increases coverage but doubles false merges, so it is rejected.

Analysis 1

Category 1 analyzes complete namesakes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 2

Category 2 analyzes initials. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 3

Category 3 analyzes spelling variants. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 4

Category 4 analyzes surname changes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 5

Category 5 analyzes changing roles. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 6

Category 6 analyzes collective entities. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 7

Case 1, Antonio García, distinguishes a photographer, a councillor, and a printer. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 8

Case 2, María López, distinguishes a letter sender and an actress. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 9

Case 3, J. Martínez, distinguishes four candidates and many mentions without context. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 10

Case 4, Estudio Hermanos Vidal, distinguishes a collective entity initially split as people. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 11

Case 5, Ana de la Fuente / Ana Fuente, distinguishes variants accepted only with a matching occupation or address. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 12

Name similarity provides coverage but disambiguates frequent names poorly. Occupation is the strongest individual signal in photography, posters, and minutes. Time removes impossible candidates but does not distinguish contemporaries. Explanations containing several signals are more useful than a score alone.

Analysis 13

Thirty-four initial failures came from incorrectly normalized dates, twelve from merged places, and nine from collective entities classified as people. Evaluation separates linking defects from defects in normalized data.

Analysis 14

Median review requires forty-two seconds with a clear signal and ninety-six seconds for initials or changing roles. Showing too many candidates increases time without improving decisions. Options are accept, reject, create a provisional entity, or request evidence.

Analysis 15

Approved links support navigation. Unresolved mentions remain visible as text and may be grouped by literal without asserting identity. Pending links are not used in identity questions or open products.

Analysis 16

The recommendation is to retain the 0.88 threshold, require a contextual signal, block temporal incompatibility, classify collective entities before linking, and reevaluate when a collection with a different distribution is added.

Analysis 17

Category 1 analyzes complete namesakes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 18

Category 2 analyzes initials. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 19

Category 3 analyzes spelling variants. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 20

Category 4 analyzes surname changes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 21

Category 5 analyzes changing roles. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 22

Category 6 analyzes collective entities. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 23

Case 1, Antonio García, distinguishes a photographer, a councillor, and a printer. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 24

Case 2, María López, distinguishes a letter sender and an actress. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 25

Case 3, J. Martínez, distinguishes four candidates and many mentions without context. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 26

Case 4, Estudio Hermanos Vidal, distinguishes a collective entity initially split as people. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 27

Case 5, Ana de la Fuente / Ana Fuente, distinguishes variants accepted only with a matching occupation or address. The decision retains discarded candidates and evidence. Mentions without sufficient occupation, date, place, or organization remain open. The system does not turn an activity interval into a birth or death date. Facts in the record link to specific documents. Where a later source provides a new signal, the case may be reopened without losing review history.

Analysis 28

Name similarity provides coverage but disambiguates frequent names poorly. Occupation is the strongest individual signal in photography, posters, and minutes. Time removes impossible candidates but does not distinguish contemporaries. Explanations containing several signals are more useful than a score alone.

Analysis 29

Thirty-four initial failures came from incorrectly normalized dates, twelve from merged places, and nine from collective entities classified as people. Evaluation separates linking defects from defects in normalized data.

Analysis 30

Median review requires forty-two seconds with a clear signal and ninety-six seconds for initials or changing roles. Showing too many candidates increases time without improving decisions. Options are accept, reject, create a provisional entity, or request evidence.

Analysis 31

Approved links support navigation. Unresolved mentions remain visible as text and may be grouped by literal without asserting identity. Pending links are not used in identity questions or open products.

Analysis 32

The recommendation is to retain the 0.88 threshold, require a contextual signal, block temporal incompatibility, classify collective entities before linking, and reevaluate when a collection with a different distribution is added.

Analysis 33

Category 1 analyzes complete namesakes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 34

Category 2 analyzes initials. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 35

Category 3 analyzes spelling variants. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 36

Category 4 analyzes surname changes. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 37

Category 5 analyzes changing roles. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.

Analysis 38

Category 6 analyzes collective entities. The name generates candidates, but the decision requires a contextual signal. Occupation is useful where recorded; period removes impossible candidates; place helps in local collections; and an organization may support a decision. No derived relation is used as the sole justification. Errors are recorded with the signal that produced them, and every correction becomes a regression test. Unresolved cases retain the literal, context, and candidates so they may be reopened where a new source appears.