ARIADNA CHUNKING AND INDEXING CONFIGURATION REGISTER V1.0

Purpose

This register defines reproducible configurations used to chunk and index the ARIADNA corpus. It does not contain final results; it identifies parameters that must accompany every experiment.

Units

Documents are divided using headings, paragraphs, and structural boundaries. The system avoids splitting identifiers, dates, lists, and version relations. Emails, chats, notes, and events use type-specific rules preserving participants, subject, date, and sequence.

Configurations

Configuration C256 uses chunks of up to 256 tokens with an overlap of forty-eight. Configuration C512 uses up to 512 tokens with an overlap of ninety-six. Both retain the source identifier, language, position, version, and validity date.

Indexes

BM25 uses title, tag, and text fields with separate analyzers for Spanish and English. The dense index uses multilingual representations. The hybrid system normalizes scores and combines lexical and dense retrieval before reranking.

Versions

Every run records the freeze date, corpus version, configuration, model, seed, and checksum. A chunking change requires index reconstruction and repetition of affected results.

Rule 1

Chunks that are too short may lose context and increase the number of required results. Long chunks may mix separate facts and make exact citation difficult. Comparison uses the same questions, indexes built from a clean copy, and three seeds where randomness exists.

Rule 2

A `previous_version` or `next_version` relation remains inside the chunk where possible. If a table or list exceeds the limit, the heading is repeated and a block identifier recorded. Citations must return to the original passage.

Rule 3

Output includes chunk count, mean length, percentiles, documents without chunks, and ES/EN pairs. Zero orphaned pairs and zero sources without representation are acceptance criteria.

Rule 4

Chunks that are too short may lose context and increase the number of required results. Long chunks may mix separate facts and make exact citation difficult. Comparison uses the same questions, indexes built from a clean copy, and three seeds where randomness exists.

Rule 5

A `previous_version` or `next_version` relation remains inside the chunk where possible. If a table or list exceeds the limit, the heading is repeated and a block identifier recorded. Citations must return to the original passage.

Rule 6

Output includes chunk count, mean length, percentiles, documents without chunks, and ES/EN pairs. Zero orphaned pairs and zero sources without representation are acceptance criteria.

Rule 7

Chunks that are too short may lose context and increase the number of required results. Long chunks may mix separate facts and make exact citation difficult. Comparison uses the same questions, indexes built from a clean copy, and three seeds where randomness exists.

Rule 8

A `previous_version` or `next_version` relation remains inside the chunk where possible. If a table or list exceeds the limit, the heading is repeated and a block identifier recorded. Citations must return to the original passage.

Rule 9

Output includes chunk count, mean length, percentiles, documents without chunks, and ES/EN pairs. Zero orphaned pairs and zero sources without representation are acceptance criteria.

Rule 10

Chunks that are too short may lose context and increase the number of required results. Long chunks may mix separate facts and make exact citation difficult. Comparison uses the same questions, indexes built from a clean copy, and three seeds where randomness exists.