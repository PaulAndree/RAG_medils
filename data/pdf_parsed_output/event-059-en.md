First formal ARIADNA results review. The session records the detection of contamination between development and evaluation, invalidates the affected metrics and defines the actions required before publishing a revised report.

Andrés Beltrán: The draft reports recall@10 of 88.6 percent and answer accuracy of 74.2 percent. Before approval, Sergio identified an anomaly.
Sergio Vidal: I compared question identifiers with repository records. Forty-two test questions also appear in an examples file used to tune chunking.
Tomás Leal: That file was generated from an early export. I believed it contained only development questions.
Lucía Navarro: Do the duplicated items include answers, or only the query text?
Sergio Vidal: They include the query, relevant document and expected passage. There is therefore direct evidence leakage.
Nuria Castaño: Experiments from 12 through 18 March used that file to compare configurations. The generative models were not trained on it, but the retrieval system was tuned after observing those cases.
Elena Martín: The metrics therefore cannot be presented as an independent evaluation.
Andrés Beltrán: Correct. Recall, MRR and answer metrics calculated over that set are invalidated. The report will not be published.
Tomás Leal: I can remove the 42 questions and recalculate on the remainder.
Sergio Vidal: That is not sufficient. The configuration was selected using test-set information. We need a new partition and must rerun selection from the beginning.
Lucía Navarro: We must also review bilingual equivalence to ensure that a contaminated Spanish question does not remain in English.
Andrés Beltrán: Actions: freeze experiments, preserve logs, open a corpus review, generate a new bilingual-pair test set and document the incident. None of the draft figures is approved.
Elena Martín: Group leadership supports a complete correction. The revised report must clearly distinguish invalidated and corrected results.