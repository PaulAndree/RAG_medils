Before the benchmark is released, the following checks must be completed:

- Exact count of semantic items and ES/EN files.
- Zero orphaned bilingual pairs.
- Zero duplicate identifiers.
- Valid version relations with no cycles.
- Current sources correctly marked.
- Reproducible training, development, and test split.
- No semantic duplicates across partitions.
- Licence and provenance for every artifact.
- JSON schema validation.
- Manual review of a sample from every file type.

The package will include the manifest, schemas, corpus, questions, relevance judgments, baselines, limitations report, and checksums. Old results affected by leakage will not be distributed as official results, although they will be described in the methodology report. Sergio will generate checksums, and Clara will review licences. Release will be authorized only when the Spanish and English versions have passed the same version of all tests.