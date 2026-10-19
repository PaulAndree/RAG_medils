Date: 2026-03-17T10:00:00Z
Author: Andrés Beltrán Vega
Message: The privacy recommendation says aggregation before export. We need to interpret exactly where it occurs.

Date: 2026-03-17T10:02:00Z
Author: Héctor Molina Frías
Message: Aggregation must run inside the SolCentro-controlled environment before any transfer.

Date: 2026-03-17T10:04:00Z
Author: Carmen Rey Palacios
Message: That is feasible for hourly data, but the current system aggregates after copying to an intermediate area.

Date: 2026-03-17T10:06:00Z
Author: Nuria Castaño Rey
Message: The intermediate area is inside SolCentro, although it uses infrastructure managed by the connector provider.

Date: 2026-03-17T10:09:00Z
Author: Héctor Molina Frías
Message: We need to confirm legal and technical control, not only physical location.

Date: 2026-03-17T10:12:00Z
Author: Sergio Vidal Cruz
Message: I can document the owner, administrators, network, encryption and permissions for that area.

Date: 2026-03-17T10:15:00Z
Author: Inés Ferrer Lozano
Message: Hourly aggregation should combine four intervals and record whether any are missing.

Date: 2026-03-17T10:18:00Z
Author: Andrés Beltrán Vega
Message: Can an hour be exported with only two available intervals?

Date: 2026-03-17T10:21:00Z
Author: Inés Ferrer Lozano
Message: Not as a complete value. It must be marked incomplete or suppressed according to the quality rule.

Date: 2026-03-17T10:24:00Z
Author: Carmen Rey Palacios
Message: We also need to group facilities to avoid overly small series.

Date: 2026-03-17T10:27:00Z
Author: Héctor Molina Frías
Message: For hourly data, I propose a minimum of three effective contributors per interval.

Date: 2026-03-17T10:30:00Z
Author: Nuria Castaño Rey
Message: The connector can calculate that number without exporting it and hide the interval when it is lower.

Date: 2026-03-17T10:33:00Z
Author: Sergio Vidal Cruz
Message: The audit log should indicate suppressed rather than the exact number of contributors.

Date: 2026-03-17T10:36:00Z
Author: Andrés Beltrán Vega
Message: What happens with local 15-minute analyses?

Date: 2026-03-17T10:39:00Z
Author: Héctor Molina Frías
Message: They run inside SolCentro, and only results meeting a higher minimum, such as five contributors, may leave.

Date: 2026-03-17T10:42:00Z
Author: Inés Ferrer Lozano
Message: We need to retain quality metadata to know whether a difference comes from missing data or suppression.

Date: 2026-03-17T10:45:00Z
Author: Carmen Rey Palacios
Message: SolCentro can accept those rules if they are incorporated into the processing agreement and operational procedure.

Date: 2026-03-17T10:48:00Z
Author: Nuria Castaño Rey
Message: I will modify the architecture so no export route can access 15-minute data without aggregation.

Date: 2026-03-17T10:51:00Z
Author: Sergio Vidal Cruz
Message: I will add negative tests: detailed export, insufficient group and unauthorized purpose.

Date: 2026-03-17T10:55:00Z
Author: Andrés Beltrán Vega
Message: Agreed: aggregation under SolCentro control, minimum three for hourly data, five for local results and suppression before transfer.