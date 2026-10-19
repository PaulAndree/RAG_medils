Second ARIADNA corpus review to investigate the scope of the detected leakage, remove contaminated bilingual pairs, rebuild the partitions and establish access controls and a new freeze before rerunning experiments.

Andrés Beltrán: The objective is to close the incident scope and approve a reconstruction procedure.
Sergio Vidal: The 42 identified questions correspond to 27 bilingual pairs and 15 monolingual items from early development. In addition, six test documents appear in a demonstration package accessible to the team.
Lucía Navarro: Even where questions are not duplicated, having seen those documents may influence query design and retrieval decisions.
Tomás Leal: I propose removing all documents from the package and their associated questions.
Sergio Vidal: Agreed. In total, we will remove 61 Spanish questions and 58 English questions. None may return to the corrected test set.
Pablo Herrero: How will we generate replacements?
Lucía Navarro: New questions will be created by annotators who did not participate in the experiments. Bilingual pairs will be assigned together, and no member of the modeling team will see their identifiers.
Nuria Castaño: I will create separate repositories. Development and validation will be accessible to the team; the corrected test set will be encrypted and accessible only to Sergio and the external reviewer.
Tomás Leal: We also need to restart the configuration history so that previous decisions are not reused without review.
Andrés Beltrán: Correct. Baselines, chunking selection and generative evaluation will be rerun from the beginning. Previous results will remain archived as invalid.
Sergio Vidal: The new freeze is proposed for 30 April, with overlap auditing by text, identifier, document and bilingual pair.
Andrés Beltrán: Approved. The corpus is reopened exclusively for reconstruction and will be frozen again on 30 April if it passes the audit.