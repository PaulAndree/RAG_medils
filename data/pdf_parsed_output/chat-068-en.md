Date: 2026-05-18T10:00:00Z
Author: Nuria Castaño Rey
Message: The connector certificate expires on 15 June, and we need to rotate it without interrupting testing.

Date: 2026-05-18T10:02:00Z
Author: Bruno Silva
Message: The partner can accept two certificates during an overlap period.

Date: 2026-05-18T10:04:00Z
Author: Sergio Vidal Cruz
Message: I propose issuing the new certificate on 25 May and keeping both active for 48 hours.

Date: 2026-05-18T10:06:00Z
Author: Carmen Rey Palacios
Message: SolCentro needs the fingerprint and full chain five days before the change.

Date: 2026-05-18T10:09:00Z
Author: Héctor Molina Frías
Message: The rotation must include a revocation test rather than only checking that the new one works.

Date: 2026-05-18T10:12:00Z
Author: Andrés Beltrán Vega
Message: Which routes will be used for testing?

Date: 2026-05-18T10:15:00Z
Author: Nuria Castaño Rey
Message: First status and upload-test with synthetic data; then one low-volume authorized hourly query.

Date: 2026-05-18T10:18:00Z
Author: Sergio Vidal Cruz
Message: The old certificate will be marked retiring during the overlap and revoked afterward.

Date: 2026-05-18T10:21:00Z
Author: Bruno Silva
Message: Our container reloads certificates on restart. We can deploy without downtime using two replicas.

Date: 2026-05-18T10:24:00Z
Author: Carmen Rey Palacios
Message: We need evidence that no replica retains the old certificate after revocation.

Date: 2026-05-18T10:27:00Z
Author: Nuria Castaño Rey
Message: I will inventory secrets and verify every image digest.

Date: 2026-05-18T10:30:00Z
Author: Héctor Molina Frías
Message: Is the private key generated at SolCentro or at the partner?

Date: 2026-05-18T10:33:00Z
Author: Sergio Vidal Cruz
Message: It is generated at SolCentro and never leaves the secret store; only the request and certificate are shared.

Date: 2026-05-18T10:36:00Z
Author: Andrés Beltrán Vega
Message: What rollback plan do we have if the new certificate fails?

Date: 2026-05-18T10:39:00Z
Author: Bruno Silva
Message: During the 48 hours, we can return to the old one. After revocation, rollback requires an emergency certificate.

Date: 2026-05-18T10:42:00Z
Author: Nuria Castaño Rey
Message: I will prepare the emergency certificate, but it will remain disabled and require dual approval.

Date: 2026-05-18T10:45:00Z
Author: Carmen Rey Palacios
Message: The proposed window is 27 May from 08:00 to 10:00.

Date: 2026-05-18T10:48:00Z
Author: Sergio Vidal Cruz
Message: I will record issuance, installation, testing, revocation and deletion of the old secret.

Date: 2026-05-18T10:51:00Z
Author: Héctor Molina Frías
Message: Afterward, we will review whether rotation can be automated before the next cycle.

Date: 2026-05-18T10:55:00Z
Author: Andrés Beltrán Vega
Message: Agreed: issuance on the 25th, rotation on the 27th, 48-hour overlap, tested revocation and an emergency certificate under dual approval.