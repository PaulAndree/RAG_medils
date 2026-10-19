ORION MIGRATION POSTMORTEM REPORT V1.0

1. Incident summary

Comparison of the original export and migrated database identified forty-three potentially duplicate profile pairs. The main cause was that publication and project systems used different identifiers and linking ran before the complete identifier history was loaded.

The migration also lost 126 old internal identifiers, thirty-eight affiliation end dates, seventeen software URLs, and several bilingual dataset descriptions. The export to ARIADNA stopped before these defects propagated into the corpus.

2. Impact

The original source was not lost, and incorrect profiles were not published outside the internal environment. However, the migrated database was unsuitable for questions about identity, affiliation history, or relations among projects and publications. Results generated during the affected window were marked provisional.

3. Root cause

The migration assumed that one local identifier was sufficient to join records. Load order omitted historical tables needed to resolve equivalences. Some rules treated missing values as ordinary gaps rather than distinguishing loss, non-applicability, and pending data.

Postmortem analysis 1

Causal factor 1 was incorrect load order. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 2

Causal factor 2 was incomplete identifier history. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 3

Causal factor 3 was overly permissive merge rules. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 4

Causal factor 4 was insufficient post-load validation. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 5

Causal factor 5 was optional fields without classification. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 6

Causal factor 6 was tests focused on global counts. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 7

Causal factor 7 was absence of a stratified manual sample. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 8

Causal factor 8 was unfixed software dependencies. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 9

Corrective action 1 is to create a separate identity table. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 10

Corrective action 2 is to load identifier histories first. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 11

Corrective action 3 is to require evidence for every merge. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 12

Corrective action 4 is to retain redirects and equivalences. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 13

Corrective action 5 is to compare fields before and after. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 14

Corrective action 6 is to run tests by entity type. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 15

Corrective action 7 is to manually review ambiguous cases. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 16

Corrective action 8 is to pause exports until approval. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 17

Causal factor 1 was incorrect load order. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 18

Causal factor 2 was incomplete identifier history. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 19

Causal factor 3 was overly permissive merge rules. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 20

Causal factor 4 was insufficient post-load validation. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 21

Causal factor 5 was optional fields without classification. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 22

Causal factor 6 was tests focused on global counts. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 23

Causal factor 7 was absence of a stratified manual sample. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 24

Causal factor 8 was unfixed software dependencies. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 25

Corrective action 1 is to create a separate identity table. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 26

Corrective action 2 is to load identifier histories first. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 27

Corrective action 3 is to require evidence for every merge. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 28

Corrective action 4 is to retain redirects and equivalences. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 29

Corrective action 5 is to compare fields before and after. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 30

Corrective action 6 is to run tests by entity type. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 31

Corrective action 7 is to manually review ambiguous cases. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 32

Corrective action 8 is to pause exports until approval. It has an owner, target date, test, and closure criterion. The result is generated from a clean copy and compared with the original export. An action does not close merely because code changed but when the test demonstrates field recovery and duplicate prevention. Dependent actions run in the recorded order.

Postmortem analysis 33

Causal factor 1 was incorrect load order. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 34

Causal factor 2 was incomplete identifier history. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.

Postmortem analysis 35

Causal factor 3 was overly permissive merge rules. The investigation reconstructed the sequence using logs, scripts, manifests, and copies. Primary cause, contributing condition, and detection signal were distinguished. Correction was not limited to the visible case: the same pattern was searched across all entities and versions. Evidence is retained with the date, owner, and decision.