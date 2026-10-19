ATLAS-2 OPERATION AND MAINTENANCE MANUAL V1.2

1. Purpose

Atlas-2 is the shared computing and storage infrastructure of the NEXUS group. This manual defines daily operation, accounts, queues, storage, backups, maintenance, updates, monitoring, incidents, and recovery. The purpose is to provide reproducible capacity without compromising other projects or restricted data.

The manual distinguishes administration, research use, and support. Users do not receive administrative permissions by default. Jobs must be identified, use persistent paths, and record the configuration required to reproduce results.

2. Components

Atlas-2 includes CPU nodes, three GPUs, working storage, archival storage, a queue service, authentication, monitoring, and backups. Every component has an owner, version, dependencies, health check, and restoration procedure.

3. Principles

Operation follows least privilege, project separation, quotas, traceability, and planned maintenance. Temporary jobs do not replace the archive. Restricted data is stored in separate directories with specific groups. Updates include testing and rollback.

Technical section 1

Operating area 1, accounts, covers creation, role, project, quota, review, and removal. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 2

Operating area 2, queues, covers priority, limit, resources, cancellation, and logging. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 3

Operating area 3, GPUs, covers reservation, interactive work, overnight execution, and sharing. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 4

Operating area 4, working storage, covers quota, performance, cleanup, and alerts. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 5

Operating area 5, archive, covers retention, checksum, restoration, and access. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 6

Operating area 6, backups, covers frequency, scope, encryption, verification, and recovery. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 7

Operating area 7, monitoring, covers capacity, temperature, errors, health, and notification. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 8

Operating area 8, updates, covers plan, dependency, window, test, and rollback. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 9

Operating area 9, incidents, covers detection, classification, containment, recovery, and closure. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 10

Operating area 10, continuity, covers alternate owners, documentation, and emergency access. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 11

Maintenance step 1 is to prepare the window and notify. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 12

Maintenance step 2 is to stop new submissions. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 13

Maintenance step 3 is to save or cancel jobs. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 14

Maintenance step 4 is to verify backups and rollback. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 15

Maintenance step 5 is to update the system and drivers. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 16

Maintenance step 6 is to restart services in order. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 17

Maintenance step 7 is to test authentication and queues. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 18

Maintenance step 8 is to test CPU, GPU, and storage. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 19

Maintenance step 9 is to restore a sample file. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 20

Maintenance step 10 is to declare service or roll back. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 21

Incident 1 is stalled job. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 22

Incident 2 is disk errors. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 23

Incident 3 is GPU unavailable. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 24

Incident 4 is quota exhausted. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 25

Incident 5 is authentication failure. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 26

Incident 6 is high temperature. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 27

Incident 7 is failed backup. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 28

Incident 8 is file deleted by mistake. It is classified by impact, urgency, and scope. The first action protects data and prevents propagation. Secure records are then collected, service restored, and affected people informed. Closure contains the cause, actions, time, loss or absence of loss, and preventive control. A recurring incident triggers procedure review.

Technical section 29

Operating area 1, accounts, covers creation, role, project, quota, review, and removal. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 30

Operating area 2, queues, covers priority, limit, resources, cancellation, and logging. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 31

Operating area 3, GPUs, covers reservation, interactive work, overnight execution, and sharing. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 32

Operating area 4, working storage, covers quota, performance, cleanup, and alerts. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 33

Operating area 5, archive, covers retention, checksum, restoration, and access. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 34

Operating area 6, backups, covers frequency, scope, encryption, verification, and recovery. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 35

Operating area 7, monitoring, covers capacity, temperature, errors, health, and notification. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 36

Operating area 8, updates, covers plan, dependency, window, test, and rollback. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 37

Operating area 9, incidents, covers detection, classification, containment, recovery, and closure. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 38

Operating area 10, continuity, covers alternate owners, documentation, and emergency access. It has an owner, normal procedure, and emergency route. Configuration is retained in version control and compared with the deployed state. Administrative actions are logged. A check is not successful where only the main service responds while dependencies fail. Changes are tested first in a lower-impact environment or node.

Technical section 39

Maintenance step 1 is to prepare the window and notify. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 40

Maintenance step 2 is to stop new submissions. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 41

Maintenance step 3 is to save or cancel jobs. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 42

Maintenance step 4 is to verify backups and rollback. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 43

Maintenance step 5 is to update the system and drivers. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 44

Maintenance step 6 is to restart services in order. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.

Technical section 45

Maintenance step 7 is to test authentication and queues. The record identifies the time, person, command or tool, result, and evidence. Where a failure appears, the team decides whether to continue, isolate the component, or roll back. The service is not declared operational until authentication, storage, CPU and GPU submission, monitoring, and restoration are complete. Notices state the real status rather than an optimistic estimate.