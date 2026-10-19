First SILEX API technical review to check coverage of all 62 procedures, response times, authentication, versioning and compatibility with ontology version 1.1 approved for the pilot.

Javier Ortega: We will review functional coverage, performance and deployment requirements. Sergio, what does the API currently expose?
Sergio Vidal: There are endpoints for the catalogue, procedure detail, responsible unit, deadlines and documentation. All 62 procedures are available, and 61 meet every mandatory rule.
Alba Prieto: The remaining procedure has a warning because the responsible unit changed its name in June. The identifier is correct, but the historical name is not displayed according to the requested date.
Mireia Soler: Ontology version 1.1 already contains validity intervals. The API must accept a query date and return the corresponding label.
Nuria Castaño: For performance, the 95th percentile is 1.6 seconds for simple queries and 2.3 seconds for searches with multiple filters. The pilot criterion is below two seconds for the agreed queries.
Luis Noguera: Multi-filter searches will be used by the municipality, especially by unit and procedure type.
Javier Ortega: We therefore need optimization before pre-production. What other risks exist?
Nuria Castaño: Token renewal works, but error codes do not yet distinguish missing data from invalid filters.
Sergio Vidal: An explicit version header and a link to the provenance record are also missing.
Javier Ortega: Actions: Mireia and Sergio will resolve the temporal name; Nuria will optimize filters and error codes; Alba will validate responses for all 62 procedures. API 1.0 candidate will be reviewed again in August.