ARIADNA EVALUATION REPORT V1.0

Document status

This report records the first complete ARIADNA evaluation. After it was prepared, possible leakage across tuning and test splits was identified. Version 1.0 therefore remains archived and must not be used as the official performance reference.

The original run reported recall@10 of 0.94 for the hybrid baseline. No model or index change justified such a large improvement over earlier results. Review found translations, paraphrases, and questions sharing an answer in different partitions.

Original methodology

The split was initially created by question identifier. This kept technical records separate but did not correctly group semantically equivalent intents. Spanish and English versions shared a parallel relation, although some additional reformulations were not connected.

Consequence

Question proximity allowed decisions made during tuning to directly benefit test cases. The value of 0.94 does not represent independent generalization. Run files are retained with an affected-result label to support auditing and reproduction of the incident.

Incident record 1

Finding 1 affects separated ES/EN translations. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 2

Finding 2 affects minor paraphrases. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 3

Finding 3 affects questions sharing the same answer and evidence. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 4

Finding 4 affects variants created during annotation. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 5

Finding 5 affects temporal cases with different wording. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 6

Finding 6 affects simplified multi-hop questions. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 7

Corrective action 1 is to suspend dissemination of metrics. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 8

Corrective action 2 is to rebuild semantic groups. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 9

Corrective action 3 is to assign every group to one split. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 10

Corrective action 4 is to rerun baselines. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 11

Corrective action 5 is to replace report tables. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 12

Corrective action 6 is to update limitations and the manifest. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 13

Finding 1 affects separated ES/EN translations. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 14

Finding 2 affects minor paraphrases. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 15

Finding 3 affects questions sharing the same answer and evidence. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 16

Finding 4 affects variants created during annotation. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 17

Finding 5 affects temporal cases with different wording. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 18

Finding 6 affects simplified multi-hop questions. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 19

Corrective action 1 is to suspend dissemination of metrics. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 20

Corrective action 2 is to rebuild semantic groups. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 21

Corrective action 3 is to assign every group to one split. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 22

Corrective action 4 is to rerun baselines. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 23

Corrective action 5 is to replace report tables. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 24

Corrective action 6 is to update limitations and the manifest. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 25

Finding 1 affects separated ES/EN translations. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 26

Finding 2 affects minor paraphrases. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 27

Finding 3 affects questions sharing the same answer and evidence. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 28

Finding 4 affects variants created during annotation. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 29

Finding 5 affects temporal cases with different wording. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 30

Finding 6 affects simplified multi-hop questions. Review uses automatic similarity and manual checking. Confirmed cases are grouped under one intent. The affected splits, experiments using the data, and potential effect on conclusions are recorded. The report does not delete the earlier result: it retains it with archived status and a visible explanation.

Incident record 31

Corrective action 1 is to suspend dissemination of metrics. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 32

Corrective action 2 is to rebuild semantic groups. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 33

Corrective action 3 is to assign every group to one split. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.

Incident record 34

Corrective action 4 is to rerun baselines. It has an owner, date, and evidence. The correction is applied from a clean copy and retains checksums. New results do not overwrite earlier ones until validation is complete. Final review checks counts, bilingual pairs, distribution, and absence of split groups.