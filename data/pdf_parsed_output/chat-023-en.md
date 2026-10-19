Date: 2026-04-06T09:35:00Z
Author: Inés Ferrer Lozano
Message: The preliminary delivery contains 146 negative readings. We need to determine whether they are errors or fed-in energy.

Date: 2026-04-06T09:37:00Z
Author: Carmen Rey Palacios
Message: At two facilities, the meter uses a negative sign when there is net photovoltaic generation.

Date: 2026-04-06T09:39:00Z
Author: Andrés Beltrán Vega
Message: Do all 146 readings belong to those two facilities?

Date: 2026-04-06T09:41:00Z
Author: Inés Ferrer Lozano
Message: One hundred thirty-eight do. Eight appear at a facility with no registered generation.

Date: 2026-04-06T09:44:00Z
Author: Sergio Vidal Cruz
Message: The eight cases coincide with a device restart and have an empty qualityCode.

Date: 2026-04-06T09:47:00Z
Author: Nuria Castaño Rey
Message: We must not apply an absolute value globally; that would destroy the meaning of export.

Date: 2026-04-06T09:50:00Z
Author: Carmen Rey Palacios
Message: The commercial system separates imported and exported energy. We can use those variables as a reference.

Date: 2026-04-06T09:53:00Z
Author: Inés Ferrer Lozano
Message: I propose interpreting a negative value as export only when generationEnabled=true and it corresponds to the exported-energy variable.

Date: 2026-04-06T09:56:00Z
Author: Andrés Beltrán Vega
Message: What do we do with the eight restart cases?

Date: 2026-04-06T09:59:00Z
Author: Sergio Vidal Cruz
Message: Mark them invalid-device-state, retain the original value and exclude them from aggregations.

Date: 2026-04-06T10:02:00Z
Author: Nuria Castaño Rey
Message: I will add a validation requiring qualityCode whenever the value is negative.

Date: 2026-04-06T10:05:00Z
Author: Carmen Rey Palacios
Message: SolCentro can provide a catalogue of meter models and their sign conventions.

Date: 2026-04-06T10:08:00Z
Author: Inés Ferrer Lozano
Message: That will prevent us from assuming all devices represent export in the same way.

Date: 2026-04-06T10:11:00Z
Author: Andrés Beltrán Vega
Message: Do negative readings affect the hourly transfer?

Date: 2026-04-06T10:14:00Z
Author: Inés Ferrer Lozano
Message: The 138 valid readings can be aggregated as export; the eight invalid readings should produce an incomplete hour.

Date: 2026-04-06T10:17:00Z
Author: Sergio Vidal Cruz
Message: The transformation log will include the rule, meter model and commercial evidence.

Date: 2026-04-06T10:20:00Z
Author: Nuria Castaño Rey
Message: I will create tests covering positive consumption, negative export, restart and missing qualityCode.

Date: 2026-04-06T10:23:00Z
Author: Carmen Rey Palacios
Message: The meter-model catalogue will be available on 8 April.

Date: 2026-04-06T10:26:00Z
Author: Andrés Beltrán Vega
Message: We will not publish balances until the calculation is repeated with these rules.

Date: 2026-04-06T10:30:00Z
Author: Inés Ferrer Lozano
Message: Agreed: do not use absolute values, validate export by context and exclude the eight invalid-state cases.