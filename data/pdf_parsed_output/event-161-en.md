Second ARIADNA retrieval comparison to evaluate abstention strategies over the v2.2 maintenance set, compare thresholds and classifiers and confirm that improvements do not alter the official v2.1 snapshot.

Andrés Beltrán: This comparison uses development, validation and the maintenance set created after v2.1. The official test set remains closed.
Tomás Leal: We compare three strategies: a similarity threshold, an answerability classifier and a combination of the classifier with current-evidence verification.
Sergio Vidal: The set contains 240 questions: 144 answerable and 96 unanswerable, balanced across Spanish and English.
Tomás Leal: The simple threshold achieves 71.4 percent correct abstention but rejects 14.6 percent of answerable questions. The classifier reaches 79.8 percent and reduces unnecessary rejection to 10.2 percent.
Lucía Navarro: What happens when validity is verified?
Tomás Leal: The combined strategy reaches 82.6 percent correct abstention and 8.9 percent unnecessary rejection. It improves especially for out-of-validity and language-unavailable cases.
Pablo Herrero: For underspecified-scope, the system should abstain and propose a clarification, not merely display a refusal.
Nuria Castaño: The interface can show the reason, consulted evidence and a clarification question, but we must avoid overly long messages.
Andrés Beltrán: Does recall change for answerable questions?
Tomás Leal: Recall@10 remains at 80.8 percent, within four tenths of the candidate without abstention.
Sergio Vidal: No configuration has accessed the v2.1 test set.
Andrés Beltrán: We select the combined strategy for adjudication and user testing. These figures come from validation and maintenance data, not official benchmark metrics.