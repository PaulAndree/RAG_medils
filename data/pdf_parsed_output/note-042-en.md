The Atlas-2 maintenance window is scheduled for 23 May from 08:00 to 14:00. Before shutdown, active jobs must be completed or cancelled, non-reproducible results must be copied, and the queues must be prevented from accepting new runs.

Pre-maintenance checklist:
- Confirm a backup of project directories and metadata databases.
- Save the scheduler and GPU-controller configuration.
- Verify at least 4 TB of free recovery storage.
- Notify the group and partners using the environment.
- Record the jobs that must be resumed after the intervention.

During maintenance, the operating system, drivers, and queue service will be updated. Afterwards, the team will test authentication, storage access, submission of one CPU job, submission of one GPU job, and restoration of a file. Nuria will lead the intervention. The service will not be declared operational until all five post-maintenance tests have passed.