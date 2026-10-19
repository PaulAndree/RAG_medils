Date: 2026-03-29T09:15:00Z
Author: Andrés Beltrán Vega
Message: The international partner reports 401 and 403 errors in the synthetic test. We need to share traces and isolate the cause.

Date: 2026-03-29T09:17:00Z
Author: Bruno Silva
Message: The 401 errors occur when requesting the token; the 403 errors arrive later when calling the load endpoint.

Date: 2026-03-29T09:19:00Z
Author: Nuria Castaño Rey
Message: Which client identifier and certificate fingerprint is the partner using?

Date: 2026-03-29T09:21:00Z
Author: Bruno Silva
Message: Client verdant-partner-test and a certificate ending in 7A:4C. I can send the full chain through the secure channel.

Date: 2026-03-29T09:24:00Z
Author: Sergio Vidal Cruz
Message: Our traces show that two requests use an old audience value and three arrive with a one-hour clock offset.

Date: 2026-03-29T09:27:00Z
Author: Carmen Rey Palacios
Message: The SolCentro environment changed to UTC last week. Is the partner still signing in local time?

Date: 2026-03-29T09:30:00Z
Author: Bruno Silva
Message: The server is in UTC, but the container retains a Europe/Lisbon variable.

Date: 2026-03-29T09:33:00Z
Author: Nuria Castaño Rey
Message: The signature must use UTC with a maximum five-minute tolerance. A one-hour offset invalidates the token.

Date: 2026-03-29T09:36:00Z
Author: Héctor Molina Frías
Message: Before changing anything, confirm that access is not being expanded to real-data routes.

Date: 2026-03-29T09:39:00Z
Author: Sergio Vidal Cruz
Message: The credential is limited to the synthetic environment and the status and upload-test endpoints.

Date: 2026-03-29T09:42:00Z
Author: Andrés Beltrán Vega
Message: What is causing the 403 error?

Date: 2026-03-29T09:45:00Z
Author: Nuria Castaño Rey
Message: The policy expects the connector.synthetic.write scope, but the token contains connector.test.write.

Date: 2026-03-29T09:48:00Z
Author: Bruno Silva
Message: That comes from our previous template. We can correct the audience, scope and time zone in one image.

Date: 2026-03-29T09:51:00Z
Author: Carmen Rey Palacios
Message: Do we need to issue a new certificate?

Date: 2026-03-29T09:54:00Z
Author: Nuria Castaño Rey
Message: It does not appear necessary. The chain is valid; only the correct intermediate certificate must be installed in the container.

Date: 2026-03-29T09:57:00Z
Author: Sergio Vidal Cruz
Message: I will prepare a matrix with each error, hypothesis, evidence and confirmation test.

Date: 2026-03-29T10:00:00Z
Author: Héctor Molina Frías
Message: Include a revocation test and another test proving that the credential cannot access real hourly routes.

Date: 2026-03-29T10:03:00Z
Author: Bruno Silva
Message: We can deploy the corrected image tomorrow at 08:00 and repeat the test at 10:00.

Date: 2026-03-29T10:06:00Z
Author: Andrés Beltrán Vega
Message: The repeat will remain synthetic and does not replace the pending security review.

Date: 2026-03-29T10:10:00Z
Author: Nuria Castaño Rey
Message: Agreed: we correct the audience, scope, UTC and intermediate certificate; Sergio validates traces, and real data remains blocked.