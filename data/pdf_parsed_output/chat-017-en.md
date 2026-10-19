Date: 2026-03-13T09:00:00Z
Author: Andrés Beltrán Vega
Message: We need to decide how 15-minute granularity affects connectors, storage and analysis.

Date: 2026-03-13T09:02:00Z
Author: Carmen Rey Palacios
Message: Meters record every 15 minutes; the current system exports only hourly aggregates.

Date: 2026-03-13T09:04:00Z
Author: Inés Ferrer Lozano
Message: For daily balances, hourly data retains nearly all required information.

Date: 2026-03-13T09:06:00Z
Author: Héctor Molina Frías
Message: Fifteen-minute resolution increases the risk of identifying individual patterns.

Date: 2026-03-13T09:09:00Z
Author: Nuria Castaño Rey
Message: It also quadruples volume and changes processing and retention requirements.

Date: 2026-03-13T09:12:00Z
Author: Sergio Vidal Cruz
Message: The connector can receive both resolutions, but we must decide what leaves the provider environment.

Date: 2026-03-13T09:15:00Z
Author: Andrés Beltrán Vega
Message: Which analyses genuinely require 15-minute data?

Date: 2026-03-13T09:18:00Z
Author: Inés Ferrer Lozano
Message: Flexibility coefficients and responses to short events. The main indicators work with hourly data.

Date: 2026-03-13T09:21:00Z
Author: Carmen Rey Palacios
Message: SolCentro accepts local processing of 15-minute data if detailed series are not exported.

Date: 2026-03-13T09:24:00Z
Author: Héctor Molina Frías
Message: That separation must be explicit in the architecture: detailed local data, exportable hourly aggregates and synthetic data for external testing.

Date: 2026-03-13T09:27:00Z
Author: Nuria Castaño Rey
Message: We can deploy a container inside SolCentro to calculate indicators and return only authorized results.

Date: 2026-03-13T09:30:00Z
Author: Sergio Vidal Cruz
Message: We need to record which query was run, its purpose and output controls.

Date: 2026-03-13T09:33:00Z
Author: Andrés Beltrán Vega
Message: What do we store in Atlas-2?

Date: 2026-03-13T09:36:00Z
Author: Inés Ferrer Lozano
Message: Approved hourly data, aggregate results and synthetic data. Not raw 15-minute series.

Date: 2026-03-13T09:39:00Z
Author: Carmen Rey Palacios
Message: The provider will retain detailed data under its existing rules and contracts.

Date: 2026-03-13T09:42:00Z
Author: Héctor Molina Frías
Message: The decision must include group-size minimums and suppression when effective contribution is too small.

Date: 2026-03-13T09:45:00Z
Author: Nuria Castaño Rey
Message: I will create two connector routes: hourly-export and local-15min, with different permissions.

Date: 2026-03-13T09:48:00Z
Author: Sergio Vidal Cruz
Message: External tests will use synthetic data until the security review is closed.

Date: 2026-03-13T09:51:00Z
Author: Andrés Beltrán Vega
Message: Do we retain the phased design?

Date: 2026-03-13T09:55:00Z
Author: Héctor Molina Frías
Message: Yes: hourly first, local processing later and no raw 15-minute export.