Date: 2026-04-18T10:00:00Z
Author: Andrés Beltrán Vega
Message: We need to assign tasks to rebuild the split without reusing any decisions from the contaminated set.

Date: 2026-04-18T10:02:00Z
Author: Sergio Vidal Cruz
Message: First, I will remove 61 Spanish and 58 English documents that appeared in demos or examples.

Date: 2026-04-18T10:04:00Z
Author: Tomás Leal Guerra
Message: Then we will regenerate chunks, embeddings and indexes from a clean repository.

Date: 2026-04-18T10:06:00Z
Author: Pablo Herrero Sanz
Message: Deduplication must operate over normalized text, approximate hashes and relationships between versions.

Date: 2026-04-18T10:09:00Z
Author: Lucía Navarro Gil
Message: Language versions of the same question must remain in the same partition.

Date: 2026-04-18T10:12:00Z
Author: Nuria Castaño Rey
Message: I will create a new restricted repository without importing history from the previous area.

Date: 2026-04-18T10:15:00Z
Author: Andrés Beltrán Vega
Message: What sizes do we propose for development, validation and the closed test set?

Date: 2026-04-18T10:18:00Z
Author: Pablo Herrero Sanz
Message: The initial proposal is 312 questions for development, 96 for validation and 100 for the closed test set.

Date: 2026-04-18T10:21:00Z
Author: Tomás Leal Guerra
Message: The test set must remain inaccessible to the modeling team; only the custodian will run evaluation.

Date: 2026-04-18T10:24:00Z
Author: Sergio Vidal Cruz
Message: I will add overlap checks across questions, documents, chunks and examples.

Date: 2026-04-18T10:27:00Z
Author: Lucía Navarro Gil
Message: We also need to preserve distribution by language, procedure type and temporal validity.

Date: 2026-04-18T10:30:00Z
Author: Pablo Herrero Sanz
Message: I will prepare a stratification matrix and assign bilingual pairs as indivisible units.

Date: 2026-04-18T10:33:00Z
Author: Nuria Castaño Rey
Message: Access keys will expire automatically, and every test-set read will be logged.

Date: 2026-04-18T10:36:00Z
Author: Andrés Beltrán Vega
Message: When can we freeze the new split?

Date: 2026-04-18T10:39:00Z
Author: Sergio Vidal Cruz
Message: If the clean documents are ready tomorrow, the corpus can be rebuilt before 28 April.

Date: 2026-04-18T10:42:00Z
Author: Tomás Leal Guerra
Message: I need two additional days to rerun BM25, dense and hybrid baselines without reusing caches.

Date: 2026-04-18T10:45:00Z
Author: Lucía Navarro Gil
Message: The audit must review not only code but also notebooks, screenshots and training material.

Date: 2026-04-18T10:48:00Z
Author: Pablo Herrero Sanz
Message: I will document every exclusion with its reason and relationship to the contaminated artifact.

Date: 2026-04-18T10:51:00Z
Author: Andrés Beltrán Vega
Message: The target freeze date will be 30 April, subject to zero overlap and a favorable audit.

Date: 2026-04-18T10:55:00Z
Author: Nuria Castaño Rey
Message: Agreed: new repository, 312/96/100, closed test set, regenerated indexes and all baselines rerun.