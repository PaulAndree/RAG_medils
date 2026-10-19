Second infrastructure review to check storage procurement, strengthen ARIADNA isolation after the evaluation incident, and validate initial restoration tests and lifecycle policies.

Clara Ibáñez: The additional 80 terabytes have been awarded and will be installed on 18 April. Let us first review the ARIADNA incident.
Andrés Beltrán: On 26 March, we detected test questions in a file used to tune chunking. Experiments are frozen, and we need additional technical isolation.
Nuria Castaño: I created separate repositories and an encrypted area. The corrected test set will be accessible only to the custodian and external reviewer. The modeling team will not be able to list files or metadata.
Sergio Vidal: We must also prevent accidental copies through tool exports or local caches.
Nuria Castaño: Direct downloads will be blocked, access will be logged, and evaluation jobs will run through a service account without an interactive console.
Elena Martín: Have the incident records been preserved?
Sergio Vidal: Yes. The forensic copy, hashes and access history are in write-once storage.
Javier Ortega: SILEX and LUMEN need project isolation, but not the same restriction level. Can we apply different templates?
Nuria Castaño: Yes. There will be public, internal, restricted and closed-evaluation levels.
Clara Ibáñez: What was the result of the quarterly restoration test?
Nuria Castaño: We restored 2.4 terabytes in an isolated environment. Integrity was complete, although the elapsed time exceeded the target by forty minutes.
Elena Martín: The measures are approved. Adjust the recovery target and repeat the test after installing the expansion.