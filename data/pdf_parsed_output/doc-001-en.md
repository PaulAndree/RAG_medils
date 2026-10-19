1. Purpose and scope

This plan defines the organization of the SILEX pilot phase, whose purpose is to determine whether a heterogeneous municipal catalogue can be transformed into an interoperable, bilingual, and verifiable semantic representation. The pilot is jointly conducted by the NEXUS group at Sierra Centro Public University and the Santa Marina City Council. Its scope covers procedure selection, field mapping, ontology publication, data validation, API deployment, and evaluation with municipal staff.

The plan does not itself authorize reuse of every available dataset. Each source retains its own licence and access conditions. In particular, the municipal register of residents is treated as restricted until the municipal legal office confirms permitted uses in writing. Technical availability of an export will not be interpreted as authorization to publish or redistribute it.

Version 1.0 uses 15 September 2026 as the reference date for the start of the pilot. If mappings, licences, or the environment make that date infeasible, project management will prepare a change proposal. An alternative date remains provisional until formally approved by the steering committee and confirmed in writing by the municipality.

2. Delivery principles

SILEX follows five principles. First, values will not be invented to fill missing data. Second, every change will be traceable to a source, responsible person, and date. Third, the Spanish and English versions will share identifiers and meaning. Fourth, validation will occur before publication or deployment. Fifth, legal and organizational decisions take precedence over technical availability.

Data will be classified as present, missing, non-applicable, excluded, or awaiting validation. This distinction is mandatory because it affects SHACL rules, interface presentation, and metric interpretation. An empty field alone is not sufficient to express its status.

3. Governance

Javier Ortega Campos acts as scientific lead and contact point with Santa Marina. Luis Noguera coordinates municipal staff and validates local names, units, and processes. Mireia Soler Pons leads ontology work; Alba Prieto Mora maintains the catalogue and test data; Nuria Castaño Rey manages deployment and security; Sergio Vidal Cruz administers storage, ingestion, and backups; Clara Ibáñez Soto coordinates budget, evidence, and closure.

The steering committee will meet monthly and whenever a critical blocker arises. Decisions will be classified as approved, provisional, or rejected. Provisional proposals do not modify published documentation. Minutes will record participants, facts, alternatives, decision, owner, and review date.

WP1 — Governance and requirements

Owner: Javier Ortega Campos. Consolidate functional, legal, and organizational requirements with the Santa Marina City Council. The package maintains a decision register and separates formal agreements from proposals still awaiting approval. It includes interviews with municipal units, catalogue review, assignment of owners, and validation of acceptance criteria.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP2 — Catalogue and data quality

Owner: Alba Prieto Mora. Prepare the procedure catalogue, classify missing, non-applicable, and pending values, and document every transformation. Quality will be measured through mandatory-field completeness, identifier uniqueness, bilingual-label coverage, and consistency among units, legal bases, channels, and deadlines.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP3 — Ontology and vocabularies

Owner: Mireia Soler Pons. Develop the SILEX ontology and controlled vocabularies. The package covers procedure statuses, responsible units, service-delivery channels, legal bases, deadlines, and version relations. Spanish and English labels will be validated as part of the model rather than as a later editorial task.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP4 — Mapping and validation

Owner: Javier Ortega Campos. Define correspondence rules between municipal systems and the ontology, run SHACL validation, and retain reports before and after each correction. Critical errors will block publication. Warnings will be accepted only where a documented and verifiable exception exists.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP5 — API and deployment

Owner: Nuria Castaño Rey. Implement the API, prepare reproducible packages, and deploy the municipal pre-production environment. Secrets will be managed outside the repository, access will use named accounts, and traces will not contain complete request bodies or sensitive information.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP6 — Pilot and evaluation

Owner: Alba Prieto Mora. Organize test sessions, measure technical and user outcomes, and record incidents. Evaluation will combine verifiable tasks, performance metrics, cross-language equivalence, and qualitative feedback. Problems affecting deadlines, procedure discovery, or bilingual consistency will be treated as blockers.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

WP7 — Transfer and closure

Owner: Clara Ibáñez Soto. Prepare the asset inventory, licences, documentation, final-report acceptance, and transfer to the municipality. Restricted datasets will be identified separately. Scientific and financial closure will follow different schedules and preserve traceable evidence.

Each work package will maintain verifiable outputs, dependencies, exit criteria, and review evidence. Completion will not be based only on a statement that work is finished: there must be a file, test run, recorded approval, or reproducible metric.

4. Reference schedule

January and February are dedicated to requirements, the catalogue, the ontology, and initial validation. From March to May, mappings are corrected, the API is defined, and the environment is prepared. June and July are reserved for regression, integration, and deliverable D3 review. August is the deadline for closing mappings and loading the candidate version. The two weeks before the pilot will be used for operational tests, training, and final corrections.

Milestones are: revised catalogue, candidate ontology, batch 3 validation, API specification, pre-production deployment, internal evaluation, municipal preparation, pilot start, results report, and transfer. Every milestone will have a planned date and a confirmed date. External dependencies will be shown separately.

5. Data management and security

Municipal exports will be received through authorized channels and stored in access-controlled project spaces. Secrets will not appear in repositories, emails, or reports. Accounts will be named and removed when no longer required. Technical logs will retain request identifiers and outcomes but not complete bodies that might contain sensitive information.

Every load will have a manifest, checksum, date, licence, source system, and owner. Transformations will preserve the original value where normalization changes its form. Corrected errors will remain linked to the earlier version for auditing.

6. Validation and acceptance

Validation will combine schema checks, SHACL shapes, regression tests, and manual review. Minimum criteria are zero duplicate identifiers, zero critical errors, complete language labels, at least 95% completeness for mandatory fields, and ES/EN result equivalence of at least 98%. Accepted warnings must correspond to known exceptions.

The API must respond in less than two seconds at the 95th percentile for the agreed queries. Users will complete six tasks. A defect is considered blocking if it prevents discovery of a procedure, displays an incorrect deadline, loses context when language changes, or exposes unauthorized data.

7. Communication and change control

Formal communications will use email and remain linked to the corresponding document or decision. Chats support coordination but do not replace approval. Changes to scope, date, licence, or acceptance criteria require a request containing reason, impact, alternatives, and owners.

The current plan will remain available when a revision is published. A new version will state which sections changed and from what date they apply. History will not be rewritten to make a provisional proposal appear to have been approved from the beginning.

R1. Incomplete mappings

Fields without a responsible unit or legal basis may prevent transformation. Mitigation consists of requesting a new export, explicitly marking pending values, and not inferring information absent from an authorized source.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R2. Duplicate identifiers

Reuse of local codes may cause collisions. Identifiers will combine the source system, procedure type, and local number, and a regression test will prevent recurrence.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R3. Registration-data licence

Lack of formal confirmation limits scope. Registration data will remain outside the public pilot and will be used in internal tests only where written authorization exists.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R4. Bilingual inconsistency

Divergent labels or messages may produce different results. Every class, property, status, and API message will be reviewed in parallel and use a shared language-independent identifier.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R5. Environment delay

Unavailability of municipal infrastructure may shorten testing. An equivalent UPSC environment will be retained, but final acceptance requires repeating checks on the municipal network.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R6. SHACL false positives

Overly general rules may flag informational procedures as errors. Shapes will be conditional on procedure type, and accepted warnings will include justification.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R7. Pilot-date change

A provisional date must not be presented as approved. Every change will follow the control procedure, include impact and dependencies, and require formal confirmation from both organizations.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R8. Participant availability

Testing requires municipal staff with different profiles. Luis Noguera will confirm participants and substitutes, and tasks will be distributed across several sessions to reduce absence risk.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R9. Differences between source and PDF

Deliverable generation may introduce discrepancies. Final review will cover both the PDF and editable source and use an approved figures table.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

R10. Incomplete closure

Missing inventories, licences, or signatures may delay closure. Every item of evidence will have an owner and date, and the closure register will distinguish complete, pending, and non-applicable items.

The risk will be reviewed at every steering meeting until closure. The owner will document probability, impact, action, target date, and evidence. A risk will close only when the condition has disappeared or a tested control reduces impact to the accepted level.

Annex A. Readiness criteria

Before the municipal load, there must be an identified ontology version, a catalogue with field statuses, a validation report, named credentials, verified backups, and a rollback plan. Before evaluation, tasks, expected answers, participant information, and an incident mechanism must be available.

Before transfer, repositories, versions, licences, included and excluded datasets, operational documentation, results, and signatures will be checked. The university will retain reproducible sources, and the municipality will receive authorized products and the documentation required to operate the pilot.