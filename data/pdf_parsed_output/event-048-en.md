Third VERDANT privacy session to review the local-processing trial over 15-minute data, assess the resulting aggregated coefficients and establish minimum controls for future runs.

Andrés Beltrán: The local execution finished yesterday. Inés, summarize the results.
Inés Ferrer: The container processed 15-minute data from twelve facilities and produced daily coefficients for three groups. It generated no individual series or persistent identifiers.
Carmen Rey: SolCentro reviewed the code and blocked network access. The container was deleted after execution.
Sergio Vidal: The audit record includes the container image, parameters, data period, groups used and output hashes.
Héctor Molina: I reviewed the coefficients. Two groups meet the minimum of five facilities; the third contains only four on three specific days.
Inés Ferrer: We can suppress those three results or merge the group with another.
Héctor Molina: I prefer suppression. Merging would change the scientific interpretation.
Nuria Castaño: I can automate a rule preventing release of any result whose effective group size is below five.
Andrés Beltrán: Does the trial justify approving this mechanism generally?
Héctor Molina: Yes, with controls: reviewed code, blocked network, data remaining at the provider, groups of at least five, inspected output and deletion of the temporary environment.
Carmen Rey: SolCentro accepts those conditions.
Andrés Beltrán: Local processing is approved as a permitted mechanism. Export of raw 15-minute data remains prohibited.