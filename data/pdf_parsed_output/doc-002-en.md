MUNICIPAL PROCEDURE CATALOGUE FOR MAPPING — VERSION 0.9

This working file contains a representative selection of Santa Marina City Council procedures for SILEX mapping. It is not a citizen-facing publication and contains no individual cases. Its purpose is to describe fields, statuses, and exceptions that must be transformed into the ontology.

Identifiers must be stable and unique. The source-system code is preserved, but where several systems reuse the same number, a compound identifier is created. Display names may change without altering procedure identity.

Common fields

Every record contains an identifier, title, description, competent unit, legal basis, channel, deadline, publication status, language, and provenance. Fields are classified as present, non-applicable, excluded, or pending. An empty value without classification is a quality defect.

The competent unit is represented by a stable code and display name. The deadline is retained as both a normalized duration and a readable label. Versioned legal bases include a validity date and relation to the superseded text.

SM-REG-001 — Registration certificate

Competent unit: Municipal Register Office. Channel: In person and online. Deadline: Ten working days.

Request for a certificate confirming that a person is registered in the municipal register. Personal registration data remains restricted; the public catalogue describes only the procedure, requirements, and channel.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-URB-014 — Minor building permit

Competent unit: Urban Permits Unit. Channel: Online and in person. Deadline: One month.

Authorizes small-scale work that does not affect the building structure. It requires an application form, short description, budget, and, where applicable, authorization from the owners' association.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-URB-042 — Terrace authorization

Competent unit: Public-Space Occupation Unit. Channel: Online. Deadline: Three months.

Allows tables and chairs to be placed in public space. The earlier code collided with a market-stall permit and must be replaced by a compound identifier containing the system and procedure type.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-MKT-042 — Market-stall permit

Competent unit: Trade Service. Channel: Online and in person. Deadline: Two months.

Authorizes temporary occupation of a stall in the municipal market. It must remain separate from the terrace authorization even though both source systems used local number 042.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-ENV-008 — Noise complaint

Competent unit: Environmental Unit. Channel: Online, telephone, and in person. Deadline: No single statutory deadline.

Notification of noise nuisance for municipal inspection. A person may provide dates, time periods, and files, but the catalogue must not expose attachments or third-party data.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-SUB-019 — Grant application for associations

Competent unit: Citizen Participation Unit. Channel: Online. Deadline: According to the call.

Procedure governed by a call for applications. The legal basis, submission period, and amount depend on the current call and must be linked to a specific version rather than copied as permanent values.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-INF-003 — Information on recycling centres

Competent unit: Waste Service. Channel: Web and telephone. Deadline: Not applicable.

Information record describing locations and opening hours. It does not require an application, so fields such as case status or resolution period are non-applicable rather than missing.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

SM-CIV-011 — Civil-wedding date reservation

Competent unit: General Secretariat. Channel: Online and in person. Deadline: Fifteen days to confirm availability.

Allows a person to request an available date and provide documents later. The initial reservation is not equivalent to final approval and must be distinguished from the complete case.

Review status: candidate for the mapping batch. Before publication, the legal basis, link validity, and equivalence of the Spanish and English labels must be checked.

Processing rules

A legal basis will not be inferred from a title, nor a competent unit from a visible political department. Political names may change, whereas administrative codes should remain stable. Office-specific instructions will be included only where they are current and visible to citizens.

Informational records are not required to have an application status or resolution period. Procedures governed by a call will link to the current call. Local presentation fields, such as color or form position, will be excluded with a documented reason.