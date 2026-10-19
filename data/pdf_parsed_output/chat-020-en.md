Date: 2026-03-25T10:30:00Z
Author: Andrés Beltrán Vega
Message: The latest SolCentro delivery is still incomplete. We need to list variables, owners and the next date.

Date: 2026-03-25T10:32:00Z
Author: Inés Ferrer Lozano
Message: Time zone, interval quality, exported energy, imported energy and temporary facility code are missing.

Date: 2026-03-25T10:34:00Z
Author: Carmen Rey Palacios
Message: Time zone and codes depend on the metering team; imported and exported energy depend on the commercial system.

Date: 2026-03-25T10:36:00Z
Author: Sergio Vidal Cruz
Message: Without a time zone, we cannot validate daylight-saving changes or aggregate correctly.

Date: 2026-03-25T10:39:00Z
Author: Nuria Castaño Rey
Message: The connector can assume Europe/Madrid, but I do not want to turn an assumption into source data.

Date: 2026-03-25T10:42:00Z
Author: Héctor Molina Frías
Message: It must be explicit or documented as a temporary rule validated by SolCentro.

Date: 2026-03-25T10:45:00Z
Author: Andrés Beltrán Vega
Message: How many records are affected?

Date: 2026-03-25T10:48:00Z
Author: Inés Ferrer Lozano
Message: The delivery contains 8,640 intervals from four facilities. All lack those five fields.

Date: 2026-03-25T10:51:00Z
Author: Carmen Rey Palacios
Message: I can confirm Europe/Madrid for all four facilities and deliver a code table tomorrow.

Date: 2026-03-25T10:54:00Z
Author: Sergio Vidal Cruz
Message: We need the codes not to allow public identification of the facilities.

Date: 2026-03-25T10:57:00Z
Author: Carmen Rey Palacios
Message: We will use random temporary codes and retain the mapping only inside SolCentro.

Date: 2026-03-25T11:00:00Z
Author: Nuria Castaño Rey
Message: Interval quality must distinguish measured, estimated, corrected and missing.

Date: 2026-03-25T11:03:00Z
Author: Inés Ferrer Lozano
Message: Without that variable, an imputed value could appear to be a real measurement.

Date: 2026-03-25T11:06:00Z
Author: Andrés Beltrán Vega
Message: When will imported and exported energy be separated?

Date: 2026-03-25T11:09:00Z
Author: Carmen Rey Palacios
Message: The commercial team can generate the extract on 31 March.

Date: 2026-03-25T11:12:00Z
Author: Héctor Molina Frías
Message: Until then, we must not calculate net balances as though they were separate flows.

Date: 2026-03-25T11:15:00Z
Author: Sergio Vidal Cruz
Message: I will mark the current delivery as incomplete-source and block external transfer.

Date: 2026-03-25T11:18:00Z
Author: Nuria Castaño Rey
Message: We can use it to test structure, but not for scientific results or governance decisions.

Date: 2026-03-25T11:21:00Z
Author: Carmen Rey Palacios
Message: I will make two deliveries: time zone and codes on the 26th, and the complete dataset on 31 March.

Date: 2026-03-25T11:25:00Z
Author: Andrés Beltrán Vega
Message: Agreed: five fields remain pending, owners are identified and the next complete delivery is due on 31 March.