ARIADNA EVALUATION REPORT V1.1

1. Status

Version 1.1 supersedes report 1.0 and presents results obtained from the corrected split. The earlier report remains archived because it documents the leakage incident and supports reconstruction of decisions. Its metrics must not be used to compare systems.

The official benchmark count is 2,302 semantic questions and 4,604 ES/EN records. The corpus freeze date is 31 May 2026. The pilot is planned for 15 September 2026.

2. Split correction

Questions were grouped by semantic intent before assignment to a split. Every group contains translations, paraphrases, variants sharing the same answer, and cases sharing essential evidence. All group members remain together.

Reconstruction produced 1,840 training semantic questions, 230 development questions, and 232 test questions. Spanish and English versions remain in the same split. Validation identifies zero orphaned pairs and zero divided groups.

3. Baselines

BM25 achieves recall@10 of 0.69 and MRR of 0.52. The hybrid system achieves recall@10 of 0.80 and MRR of 0.63. The earlier value of 0.94 is identified as affected by leakage and is not an official result.

Hybrid retrieval improves semantic, multi-hop, and temporal questions in particular. BM25 remains competitive for exact identifiers and low-ambiguity strings. The main configuration uses 256-token chunks.

Results section 1

Section 1 analyzes corpus composition. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 2

Section 2 analyzes distribution by artifact type. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 3

Section 3 analyzes category balance. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 4

Section 4 analyzes difficulty balance. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 5

Section 5 analyzes temporal distribution. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 6

Section 6 analyzes project coverage. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 7

Section 7 analyzes bilingual pairs. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 8

Section 8 analyzes superseded sources. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 9

Section 9 analyzes unanswerable questions. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 10

Section 10 analyzes reference citations. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 11

Evaluation 1 uses recall@10. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 12

Evaluation 2 uses MRR. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 13

Evaluation 3 uses latency. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 14

Evaluation 4 uses citation precision. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 15

Evaluation 5 uses claim coverage. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 16

Evaluation 6 uses bilingual consistency. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 17

Evaluation 7 uses temporal-version selection. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 18

Evaluation 8 uses unanswerable responses. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 19

Finding 1 indicates that hybrid retrieval improves semantic retrieval. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 20

Finding 2 indicates that BM25 locates exact identifiers better. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 21

Finding 3 indicates that version filters reduce outdated answers. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 22

Finding 4 indicates that multi-hop cases require more than one source. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 23

Finding 5 indicates that neighboring citations may be incomplete. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 24

Finding 6 indicates that unanswerable questions must distinguish absence from failure. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 25

Finding 7 indicates that translations maintain similar results. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 26

Finding 8 indicates that hybrid latency remains within the pilot target. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 27

Limitation 1 is a corpus centered on NEXUS. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 28

Limitation 2 is a limited number of external users. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 29

Limitation 3 is document changes after the freeze date. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 30

Limitation 4 is dependence on particular multilingual models. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 31

Limitation 5 is difficulty adjudicating some temporal cases. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 32

Limitation 6 is incomplete coverage of administrative domains. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 33

Section 1 analyzes corpus composition. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 34

Section 2 analyzes distribution by artifact type. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 35

Section 3 analyzes category balance. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 36

Section 4 analyzes difficulty balance. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 37

Section 5 analyzes temporal distribution. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 38

Section 6 analyzes project coverage. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 39

Section 7 analyzes bilingual pairs. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 40

Section 8 analyzes superseded sources. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 41

Section 9 analyzes unanswerable questions. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 42

Section 10 analyzes reference citations. It contains counts, percentages, criteria, and limitations. Tables are generated from structured files and are not manually edited. A second person reproduces totals and compares a sample with the sources. Differences from the earlier version are explained. ES and EN results are presented together to identify any deviation across parallel versions.

Results section 43

Evaluation 1 uses recall@10. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 44

Evaluation 2 uses MRR. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 45

Evaluation 3 uses latency. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 46

Evaluation 4 uses citation precision. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 47

Evaluation 5 uses claim coverage. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 48

Evaluation 6 uses bilingual consistency. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 49

Evaluation 7 uses temporal-version selection. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 50

Evaluation 8 uses unanswerable responses. The analysis unit, calculation, and excluded cases are defined. Results contain the mean, variation, and category analysis. Manual review examines a sample of successes and errors. An aggregate metric does not replace behavioral analysis. Intervals and configurations are retained to support repetition.

Results section 51

Finding 1 indicates that hybrid retrieval improves semantic retrieval. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 52

Finding 2 indicates that BM25 locates exact identifiers better. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 53

Finding 3 indicates that version filters reduce outdated answers. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 54

Finding 4 indicates that multi-hop cases require more than one source. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 55

Finding 5 indicates that neighboring citations may be incomplete. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 56

Finding 6 indicates that unanswerable questions must distinguish absence from failure. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 57

Finding 7 indicates that translations maintain similar results. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 58

Finding 8 indicates that hybrid latency remains within the pilot target. The conclusion is supported by metrics and example review. Exceptions, categories with a smaller effect, and alternative explanations are documented. The finding is not generalized beyond the corpus without additional evaluation. Resulting actions have an owner and are added to the guide, index, or protocol as appropriate.

Results section 59

Limitation 1 is a corpus centered on NEXUS. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 60

Limitation 2 is a limited number of external users. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 61

Limitation 3 is document changes after the freeze date. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 62

Limitation 4 is dependence on particular multilingual models. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 63

Limitation 5 is difficulty adjudicating some temporal cases. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.

Results section 64

Limitation 6 is incomplete coverage of administrative domains. The report explains its likely effect and avoids presenting the benchmark as a universal measure. Extensions are proposed but are not mixed with the evaluated version. A new collection or rule change requires a corpus version, index regeneration, and baseline reruns. The limitation remains visible in the model card and release documentation.