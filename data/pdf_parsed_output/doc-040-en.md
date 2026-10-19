VERDANT PILOT FINAL REPORT V1.0

1. Executive summary

The VERDANT pilot evaluated federated exchange of energy products among SolCentro, NEXUS, and Instituto Técnico do Norte. The architecture retained original fifteen-minute readings within SolCentro and delivered hourly or daily products subject to policy, purpose, minimum group size, and expiry.

The pilot processed data from sixty-two installations over eighty-nine days. Hourly products were generated where four valid intervals and at least three meters were available. Consumers received metadata, coverage, quality, and provenance together with the aggregate value.

All critical authentication, authorization, revocation, network, logging, and minimum-group tests passed. No exposure of individual readings, names, addresses, contracts, or secrets was identified. Product-request p95 latency was 1.68 seconds in the pre-production environment.

2. Objectives

Objectives were to demonstrate interoperability across connectors, enforce access policies, produce reproducible aggregates, preserve provenance, measure quality, and assess the usefulness of products for energy analysis.

Evaluation does not cover billing, automated installation control, or citizen use. Results apply to the versions, organizations, and period recorded in the manifest.

3. Governance

Andrés Beltrán Vega led VERDANT. Inés Ferrer Lozano maintained the model and quality. Sergio Vidal Cruz managed storage and pipelines. Nuria Castaño Rey coordinated infrastructure. Héctor Molina Frías reviewed privacy and security. Carmen Rey represented SolCentro. Bruno Almeida coordinated Instituto Técnico do Norte.

Decisions were recorded with their purpose, alternatives, owner, date, and artifacts. Exceptions had an expiry. Proposals were not treated as approved until confirmation was received.

Final section 1

Pilot area 1 is federated architecture. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 2

Pilot area 2 is product catalogue. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 3

Pilot area 3 is connectors. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 4

Pilot area 4 is authentication. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 5

Pilot area 5 is authorization. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 6

Pilot area 6 is policies. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 7

Pilot area 7 is aggregation. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 8

Pilot area 8 is quality. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 9

Pilot area 9 is security. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 10

Pilot area 10 is audit. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 11

Pilot area 11 is performance. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 12

Pilot area 12 is transfer. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 13

Final test 1 covers product discovery. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 14

Final test 2 covers authorized request. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 15

Final test 3 covers denied request. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 16

Final test 4 covers revoked certificate. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 17

Final test 5 covers expired policy. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 18

Final test 6 covers minimum group. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 19

Final test 7 covers hourly product. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 20

Final test 8 covers daily product. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 21

Final test 9 covers withdrawal. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 22

Final test 10 covers rollback. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 23

Final test 11 covers latency. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 24

Final test 12 covers temporary-data deletion. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 25

Finding 1 indicates that federation avoided centralizing original readings. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 26

Finding 2 indicates that policies were enforced consistently. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 27

Finding 3 indicates that declared quality improved interpretation. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 28

Finding 4 indicates that coverage must always accompany the aggregate. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 29

Finding 5 indicates that daily products are sufficient for some analyses. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 30

Finding 6 indicates that hourly products provide value with controls. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 31

Finding 7 indicates that revocation worked within target. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 32

Finding 8 indicates that logs were useful without containing bodies. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 33

Finding 9 indicates that administration configuration requires discipline. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 34

Finding 10 indicates that exceptions need additional automation. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 35

Finding 11 indicates that interoperability across partners was reproducible. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 36

Finding 12 indicates that documentation supported environment restoration. The conclusion combines metrics, tests, interviews, and evidence review. Exceptions, scope, and possible alternative explanations are documented. The finding is not generalized to other sectors without additional evaluation. The resulting action has an owner, priority, and closure criterion. Future changes require a new version and regression tests.

Final section 37

Stakeholder evaluation 1 covers SolCentro. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 38

Stakeholder evaluation 2 covers NEXUS. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 39

Stakeholder evaluation 3 covers Instituto Técnico do Norte. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 40

Stakeholder evaluation 4 covers security team. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 41

Stakeholder evaluation 5 covers quality team. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 42

Stakeholder evaluation 6 covers analysts. Usefulness, clarity, effort, risks, and continuity conditions were collected. Responses are aggregated to avoid attributing individual opinions. Differences are presented as perspectives rather than facts. Operational needs are separated from scientific changes. Final decisions retain their owner and date.

Final section 43

Recommendation 1 is to automate exception expiry. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 44

Recommendation 2 is to retain revocation tests. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 45

Recommendation 3 is to publish coverage and quality. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 46

Recommendation 4 is to block unexpected unit changes. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 47

Recommendation 5 is to review accounts quarterly. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 48

Recommendation 6 is to retain administration separation. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 49

Recommendation 7 is to extend the catalogue with documented products. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 50

Recommendation 8 is to repeat evaluation in another season. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 51

Recommendation 9 is to retain original data at the source. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 52

Recommendation 10 is to formalize transfer. It is classified as immediate, transfer-related, or future. It has an owner, date, artifact, and test. The improvement does not retrospectively change results. It closes where a test demonstrates the expected behavior without regressions. Open recommendations remain visible in the continuity inventory.

Final section 53

Limitation 1 is limited installation count. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 54

Limitation 2 is an eighty-nine-day period. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 55

Limitation 3 is specific partners. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 56

Limitation 4 is defined aggregate products. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 57

Limitation 5 is pre-production environment. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 58

Limitation 6 is absence of billing. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 59

Limitation 7 is no coverage of automated decisions. The report explains its likely effect and avoids presenting the pilot as universal validation. An extension requires new legal, technical, and quality evaluation. Additional data or rules are not mixed with the closed version. The limitation remains visible in transfer documentation and any derived publication.

Final section 60

Pilot area 1 is federated architecture. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 61

Pilot area 2 is product catalogue. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 62

Pilot area 3 is connectors. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 63

Pilot area 4 is authentication. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 64

Pilot area 5 is authorization. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 65

Pilot area 6 is policies. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 66

Pilot area 7 is aggregation. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 67

Pilot area 8 is quality. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 68

Pilot area 9 is security. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 69

Pilot area 10 is audit. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 70

Pilot area 11 is performance. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 71

Pilot area 12 is transfer. The report describes its objective, design, versions, tests, results, incidents, and limitations. Figures are generated from structured files, and a second person reproduces totals. Changes from the plan are explained. A passed test does not remove risks outside its scope. Evidence is retained with the date, environment, configuration, and owner.

Final section 72

Final test 1 covers product discovery. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 73

Final test 2 covers authorized request. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 74

Final test 3 covers denied request. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 75

Final test 4 covers revoked certificate. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 76

Final test 5 covers expired policy. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 77

Final test 6 covers minimum group. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 78

Final test 7 covers hourly product. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 79

Final test 8 covers daily product. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 80

Final test 9 covers withdrawal. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 81

Final test 10 covers rollback. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 82

Final test 11 covers latency. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.

Final section 83

Final test 12 covers temporary-data deletion. It defines preconditions, identity, product, operation, expected result, audit, and cleanup. Positive and negative cases are executed. An authorization error, granular-data exposure, acceptance of a revoked certificate, or generation from fewer than three meters is blocking. Results contain evidence and independent repetition.