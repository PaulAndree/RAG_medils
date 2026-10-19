Fourth VERDANT privacy session to evaluate how missing data affects effective group size, approve enhanced suppression rules and decide whether the hourly pilot may expand from four to six facilities.

Andrés Beltrán: Inés simulated missing data in the pilot groups. What did we learn?
Inés Ferrer: When a facility stops reporting for several hours, a nominal group of three may fall to two effective contributors. The previous rule checked only configured group size.
Héctor Molina: That creates a risk. Suppression must be calculated for each interval using effective contributors, not nominal members.
Sergio Vidal: I prepared a rule that counts facilities with valid values after cleaning. If fewer than three remain for hourly data or fewer than five for local-processing results, the interval is removed.
Carmen Rey: Could removal create gaps that indirectly reveal which facility stopped reporting?
Héctor Molina: Yes. The output must therefore use a generic unavailable-data indicator without explaining the reason or the exact number of contributors.
Nuria Castaño: The connector can apply the rule and record the reason only in the internal audit log.
Inés Ferrer: With this correction, the simulation produces no identifiable intervals and retains 91 percent of the hourly data.
Andrés Beltrán: May we authorize expansion to six facilities?
Héctor Molina: Yes, provided that the new rule is active, temporary codes remain in place and the review is repeated after the first month.
Carmen Rey: SolCentro agrees.
Andrés Beltrán: Dynamic suppression and controlled expansion to six facilities from 10 August are approved.