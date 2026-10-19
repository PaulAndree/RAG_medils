Fourth ARIADNA retrieval evaluation to analyze the robustness of the approved v2.1 configuration against incomplete queries, typographical errors, temporally scoped questions and differences between language versions.

Andrés Beltrán: The final v2.1 metrics are approved. This session does not change those figures; it evaluates where the system fails under more realistic conditions.
Tomás Leal: We created four stress sets from validation data: abbreviated queries, typographical errors, implicit temporal references and questions whose current evidence differs by language.
Sergio Vidal: No item comes from the closed test set. All are labeled as post-evaluation analysis material.
Tomás Leal: Recall@10 falls from 81.7 to 75.2 percent for abbreviated queries and to 72.9 percent for typographical errors. Temporal questions retain 78.4 percent, but fail when dates are expressed relatively.
Lucía Navarro: English has more errors involving administrative names translated non-literally. In Spanish, the main problem is ambiguous acronyms.
Pablo Herrero: We can add acronym expansion and spelling correction, but the interface must show users which reformulation was applied.
Nuria Castaño: I will implement an interpreted-query view and allow reformulation to be disabled.
Andrés Beltrán: Does any improvement require recalculating the published metrics?
Tomás Leal: No, unless we change the main configuration. For now, the improvements will be tested on an experimental branch.
Andrés Beltrán: Approved. v2.1 remains frozen; acronym expansion, typographical normalization and relative-date handling will be evaluated as candidates for v2.2.