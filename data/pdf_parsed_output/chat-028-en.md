Date: 2026-04-26T10:15:00Z
Author: Tomás Leal Guerra
Message: I completed the preliminary comparison between 256-token and 512-token chunks.

Date: 2026-04-26T10:17:00Z
Author: Andrés Beltrán Vega
Message: Which set did you use?

Date: 2026-04-26T10:19:00Z
Author: Tomás Leal Guerra
Message: Only the rebuilt development and validation sets. The closed test set was not opened.

Date: 2026-04-26T10:21:00Z
Author: Sergio Vidal Cruz
Message: Also confirm that indexes were regenerated without previous caches.

Date: 2026-04-26T10:24:00Z
Author: Tomás Leal Guerra
Message: Yes. Each configuration has an independent repository, index and run.

Date: 2026-04-26T10:27:00Z
Author: Nuria Castaño Rey
Message: What is the storage and runtime difference?

Date: 2026-04-26T10:30:00Z
Author: Tomás Leal Guerra
Message: With 256 tokens, we generate 71 percent more chunks and the index uses 48 percent more storage.

Date: 2026-04-26T10:33:00Z
Author: Lucía Navarro Gil
Message: Does retrieval improve for questions requiring a specific detail?

Date: 2026-04-26T10:36:00Z
Author: Tomás Leal Guerra
Message: Yes. Recall@10 is 82.1 percent with 256 versus 80.9 percent with 512.

Date: 2026-04-26T10:39:00Z
Author: Andrés Beltrán Vega
Message: What about answer quality?

Date: 2026-04-26T10:42:00Z
Author: Tomás Leal Guerra
Message: With 512, it improves slightly on questions requiring context across several clauses.

Date: 2026-04-26T10:45:00Z
Author: Sergio Vidal Cruz
Message: Did you test chunk overlap?

Date: 2026-04-26T10:48:00Z
Author: Tomás Leal Guerra
Message: I tested 32 and 64 tokens. A 64-token overlap improves continuity but increases cost and duplicate retrieval.

Date: 2026-04-26T10:51:00Z
Author: Nuria Castaño Rey
Message: We need a configuration that is reproducible and reasonable for the pilot.

Date: 2026-04-26T10:54:00Z
Author: Lucía Navarro Gil
Message: Administrative documents have very different structures. Can we use adaptive sizing?

Date: 2026-04-26T10:57:00Z
Author: Tomás Leal Guerra
Message: We can compare a third configuration of 450 tokens with heading-aware boundaries.

Date: 2026-04-26T11:00:00Z
Author: Andrés Beltrán Vega
Message: Do not select only by recall; include MRR, accuracy, cost and errors by question type.

Date: 2026-04-26T11:03:00Z
Author: Sergio Vidal Cruz
Message: The report must state that these are validation results, not official test metrics.

Date: 2026-04-26T11:06:00Z
Author: Nuria Castaño Rey
Message: I will reserve capacity to repeat all three configurations with the same versions and seeds.

Date: 2026-04-26T11:10:00Z
Author: Tomás Leal Guerra
Message: Agreed: we retain 256 and 512 as baselines and add 450 with structural boundaries for the final decision.