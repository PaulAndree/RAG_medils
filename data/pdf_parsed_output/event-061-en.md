Second ARIADNA retrieval evaluation to restart baselines and chunking selection from scratch, using only the new development and validation partitions after the leakage incident.

Andrés Beltrán: This evaluation must be treated as a complete restart. No configuration selected before the incident may be accepted without retesting.
Sergio Vidal: The new development partition contains 312 questions, and validation contains 96. Corrected test identifiers remain encrypted and are not available here.
Tomás Leal: I ran BM25, dense retrieval and a hybrid system with three chunk sizes. The 450-token hybrid achieves the best validation recall@10 at 81.7 percent.
Nuria Castaño: All experiments ran in a new repository. No configuration files or caches from the previous cycle were imported.
Lucía Navarro: Is the result balanced across Spanish and English?
Tomás Leal: Recall@10 is 82.4 percent in Spanish and 80.9 percent in English. The difference is concentrated in English documents whose translations were published later.
Sergio Vidal: The overlap audit finds no matches among development, validation and the reserved identifiers of the new test set.
Andrés Beltrán: These results are only for configuration selection. They are not final metrics and must not be compared directly with the invalidated March figures.
Tomás Leal: We will retain BM25 and dense retrieval as baselines and the 450-token hybrid as the main candidate.
Andrés Beltrán: Approved. The configuration is selected exclusively with development and validation data.