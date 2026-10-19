Date: 2026-04-14T09:00:00Z
Author: Andrés Beltrán Vega
Message: The archived run results remain too high for the actual state of the system. We need to investigate possible contamination.

Date: 2026-04-14T09:02:00Z
Author: Tomás Leal Guerra
Message: Recall@10 appears at 88.6 percent and answer accuracy at 74.2 percent.

Date: 2026-04-14T09:04:00Z
Author: Lucía Navarro Gil
Message: Those figures do not match the errors we saw in bilingual and temporal-validity questions.

Date: 2026-04-14T09:06:00Z
Author: Sergio Vidal Cruz
Message: I compared hashes and found test documents present in the development examples folder.

Date: 2026-04-14T09:09:00Z
Author: Nuria Castaño Rey
Message: Are they exact copies or derived fragments?

Date: 2026-04-14T09:12:00Z
Author: Sergio Vidal Cruz
Message: There are six exact documents and several fragments generated from them.

Date: 2026-04-14T09:15:00Z
Author: Pablo Herrero Sanz
Message: I also found test questions in a notebook used to tune prompts.

Date: 2026-04-14T09:18:00Z
Author: Andrés Beltrán Vega
Message: How many questions are affected?

Date: 2026-04-14T09:21:00Z
Author: Pablo Herrero Sanz
Message: Forty-two questions appear wholly or partially in examples, including twenty-seven bilingual pairs.

Date: 2026-04-14T09:24:00Z
Author: Tomás Leal Guerra
Message: That invalidates both retrieval and answer metrics from that run.

Date: 2026-04-14T09:27:00Z
Author: Lucía Navarro Gil
Message: We cannot only correct the report; we must rebuild the split and repeat the evaluation.

Date: 2026-04-14T09:30:00Z
Author: Nuria Castaño Rey
Message: I will block the dashboard and mark the run as invalidated so nobody reuses it.

Date: 2026-04-14T09:33:00Z
Author: Sergio Vidal Cruz
Message: I will also remove example artifacts containing closed questions or documents.

Date: 2026-04-14T09:36:00Z
Author: Andrés Beltrán Vega
Message: We need to preserve incident evidence without leaving copies accessible to the team.

Date: 2026-04-14T09:39:00Z
Author: Sergio Vidal Cruz
Message: I will store hashes, paths and access logs in an encrypted area managed by the custodian.

Date: 2026-04-14T09:42:00Z
Author: Tomás Leal Guerra
Message: Baselines must be rerun from scratch after indexes and caches are regenerated.

Date: 2026-04-14T09:45:00Z
Author: Pablo Herrero Sanz
Message: The new split must prevent overlap by question, document, fragment and language version.

Date: 2026-04-14T09:48:00Z
Author: Lucía Navarro Gil
Message: Add an independent audit before any corrected figures are released.

Date: 2026-04-14T09:51:00Z
Author: Andrés Beltrán Vega
Message: We confirm that the previous metrics are invalidated and must not be cited.

Date: 2026-04-14T09:55:00Z
Author: Nuria Castaño Rey
Message: Agreed: immediate blocking, full reconstruction, baseline reruns and an audit before results reopen.