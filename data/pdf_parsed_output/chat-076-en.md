Date: 2026-05-20T10:00:00Z
Author: Tomás Leal Guerra
Message: I completed the preliminary comparison between BM25 and hybrid retrieval on the rebuilt development and validation sets.

Date: 2026-05-20T10:02:00Z
Author: Andrés Beltrán Vega
Message: Confirm that the closed test set was not opened.

Date: 2026-05-20T10:04:00Z
Author: Tomás Leal Guerra
Message: Correct. We used only 312 development questions and 96 validation questions.

Date: 2026-05-20T10:06:00Z
Author: Sergio Vidal Cruz
Message: Which versions and chunking configuration were used?

Date: 2026-05-20T10:09:00Z
Author: Tomás Leal Guerra
Message: Rebuilt corpus v2.0, 450-token heading-aware chunks and 32-token overlap.

Date: 2026-05-20T10:12:00Z
Author: Nuria Castaño Rey
Message: What is the cost and latency difference?

Date: 2026-05-20T10:15:00Z
Author: Tomás Leal Guerra
Message: BM25 has a 0.42-second p95; hybrid retrieval has 1.18 seconds. The hybrid index uses 2.6 times more storage.

Date: 2026-05-20T10:18:00Z
Author: Lucía Navarro Gil
Message: What about retrieval quality?

Date: 2026-05-20T10:21:00Z
Author: Tomás Leal Guerra
Message: Recall@10 is 78.9 percent with BM25 and 84.6 percent with hybrid retrieval.

Date: 2026-05-20T10:24:00Z
Author: Andrés Beltrán Vega
Message: Is the improvement uniform across categories?

Date: 2026-05-20T10:27:00Z
Author: Tomás Leal Guerra
Message: No. Hybrid improves more on paraphrases and bilingual questions; BM25 remains strong on codes, exact names and figures.

Date: 2026-05-20T10:30:00Z
Author: Sergio Vidal Cruz
Message: How are scores combined?

Date: 2026-05-20T10:33:00Z
Author: Tomás Leal Guerra
Message: Per-query normalization and weights of 0.45 BM25 and 0.55 dense, with document-level deduplication.

Date: 2026-05-20T10:36:00Z
Author: Nuria Castaño Rey
Message: We need to test stability across several seeds and two embedding-model versions.

Date: 2026-05-20T10:39:00Z
Author: Lucía Navarro Gil
Message: We should also review whether hybrid retrieval returns obsolete versions more frequently.

Date: 2026-05-20T10:42:00Z
Author: Tomás Leal Guerra
Message: With temporal filtering, the incorrect-version rate falls from 6.8 percent to 1.4 percent.

Date: 2026-05-20T10:45:00Z
Author: Andrés Beltrán Vega
Message: Which configuration do we take to user evaluation?

Date: 2026-05-20T10:48:00Z
Author: Nuria Castaño Rey
Message: We can use hybrid as the primary system and BM25 as fallback when the dense index is unavailable.

Date: 2026-05-20T10:51:00Z
Author: Sergio Vidal Cruz
Message: The manifest will record both configurations, dependencies, latency and cost per query.

Date: 2026-05-20T10:55:00Z
Author: Andrés Beltrán Vega
Message: Agreed: hybrid as primary because of recall, BM25 as fallback, mandatory temporal filtering and reruns before any official metric.