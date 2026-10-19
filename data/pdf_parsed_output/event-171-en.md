Fourth ARIADNA retrieval comparison to review post-release v2.2 behavior, evaluate minor corrections over the maintenance set and confirm that neither the official v2.1 snapshot nor its metrics are modified.

Andrés Beltrán: v2.2 has been in internal use for two weeks. We will review feedback and a controlled comparison of the proposed corrections.
Tomás Leal: We added 80 maintenance questions from real incidents, without including any v2.1 test item. The full comparison set contains 380 questions.
Sergio Vidal: Published v2.2 remains frozen. Corrections ran on a separate 2.2.1-candidate branch with separate repository and results.
Tomás Leal: The candidate reaches 86.4 percent correct abstention and 7.9 percent unnecessary abstention. Accuracy on answerable questions is 69.5 percent.
Lucía Navarro: Where does it improve over v2.2?
Tomás Leal: Mainly in conflicting-current-evidence, which rises from 75.0 to 79.2 percent, and in clarifications that previously combined date and unit.
Pablo Herrero: Ninety-one percent of clarifications now propose a single dimension. Remaining errors are overly general formulations.
Nuria Castaño: The interface does not change. Only selection rules and templates are adjusted, so a full new accessibility evaluation is unnecessary.
Andrés Beltrán: Is there any material regression?
Tomás Leal: No. Recall@10 for answerable questions is 80.7 percent, essentially unchanged from the previous cycle.
Sergio Vidal: I confirm that these are maintenance metrics. They do not replace the v2.1 official results: recall@10 of 79.5 percent, MRR of 0.638 and accuracy of 68.2 percent.
Andrés Beltrán: Preparation of 2.2.1 as a minor update is approved, pending final adjudication. v2.1 and v2.2 remain immutable.