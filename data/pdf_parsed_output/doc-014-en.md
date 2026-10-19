VERDANT CONNECTOR PRIVACY AND SECURITY ASSESSMENT V1.0

1. Summary

The assessment analyzes energy-data exchange through the VERDANT connector. Fifteen-minute frequency may allow inferences about presence, activity, and habits even without names or addresses. Original readings therefore remain inside SolCentro and aggregated products are provided.

The proposal is conditionally approved. Hourly products require at least three meters, and fifteen-minute data does not leave SolCentro. Non-operational external uses receive daily products. Every exception requires a purpose, duration, owner, environment, and deletion evidence.

2. Scope

Data, identifiers, connector, authentication, authorization, logs, certificates, administration, temporary storage, aggregation, and tests are assessed. Billing and decisions about customers are outside scope. Synthetic data may be used before controls close.

3. Risk

Absence of names does not remove risk. A granular series may be linked to an installation or reveal patterns. Risk depends on frequency, duration, group size, access, purpose, and ability to combine information.

Assessment section 1

Control 1: Minimization. The design establishes that only necessary fields are exchanged. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 2

Control 2: Aggregation. The design establishes that products require three installations and coverage. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 3

Control 3: Identifiers. The design establishes that product rather than contract identifiers are used. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 4

Control 4: Authentication. The design establishes that certificates can be revoked. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 5

Control 5: Authorization. The design establishes that policy considers identity, product, operation, purpose, and validity. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 6

Control 6: Network. The design establishes that administration is limited to authorized networks. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 7

Control 7: Logging. The design establishes that tokens, headers, and bodies are removed. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 8

Control 8: Secrets. The design establishes that they are stored outside code and rotated. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 9

Control 9: Retention. The design establishes that temporary copies have a deletion date. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 10

Control 10: Audit. The design establishes that every request retains policy, result, and version. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 11

Control 11: Exceptions. The design establishes that temporary permissions expire automatically. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 12

Control 12: Incidents. The design establishes that the product can be disabled and evidence preserved. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 13

Threat 1 is reidentification of an installation. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 14

Threat 2 is inference of habits. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 15

Threat 3 is enumeration through errors. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 16

Threat 4 is expired policy remaining active. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 17

Threat 5 is secret in logs. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 18

Threat 6 is external administration access. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 19

Threat 7 is reuse of a temporary copy. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 20

Threat 8 is revoked certificate accepted. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 21

Threat 9 is aggregation with too few participants. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 22

Threat 10 is reconstruction of granularity. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 23

Exception 1 covers synthetic diagnostic series. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 24

Exception 2 covers four-hour real sample. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 25

Exception 3 covers support access during an incident. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 26

Exception 4 covers temporary retention of records. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 27

Control 1: Minimization. The design establishes that only necessary fields are exchanged. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 28

Control 2: Aggregation. The design establishes that products require three installations and coverage. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 29

Control 3: Identifiers. The design establishes that product rather than contract identifiers are used. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 30

Control 4: Authentication. The design establishes that certificates can be revoked. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 31

Control 5: Authorization. The design establishes that policy considers identity, product, operation, purpose, and validity. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 32

Control 6: Network. The design establishes that administration is limited to authorized networks. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 33

Control 7: Logging. The design establishes that tokens, headers, and bodies are removed. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 34

Control 8: Secrets. The design establishes that they are stored outside code and rotated. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 35

Control 9: Retention. The design establishes that temporary copies have a deletion date. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 36

Control 10: Audit. The design establishes that every request retains policy, result, and version. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 37

Control 11: Exceptions. The design establishes that temporary permissions expire automatically. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 38

Control 12: Incidents. The design establishes that the product can be disabled and evidence preserved. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 39

Threat 1 is reidentification of an installation. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 40

Threat 2 is inference of habits. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 41

Threat 3 is enumeration through errors. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 42

Threat 4 is expired policy remaining active. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 43

Threat 5 is secret in logs. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 44

Threat 6 is external administration access. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 45

Threat 7 is reuse of a temporary copy. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 46

Threat 8 is revoked certificate accepted. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 47

Threat 9 is aggregation with too few participants. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 48

Threat 10 is reconstruction of granularity. The asset, actor, precondition, impact, likelihood, and detection are analyzed. Mitigation combines preventive controls and a negative test. Residual risk is low, medium, or high. High risk blocks external testing; medium risk needs conditional approval; low risk is monitored. The decision retains date and owner.

Assessment section 49

Exception 1 covers synthetic diagnostic series. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 50

Exception 2 covers four-hour real sample. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 51

Exception 3 covers support access during an incident. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 52

Exception 4 covers temporary retention of records. It must show that a lower-risk alternative does not resolve the issue. It defines data, operations, environment, people, start, and end. It allows no download where diagnosis can occur in a secure space. At the end, access is revoked, the sample deleted, and deletion verified by another person.

Assessment section 53

Control 1: Minimization. The design establishes that only necessary fields are exchanged. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 54

Control 2: Aggregation. The design establishes that products require three installations and coverage. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.

Assessment section 55

Control 3: Identifiers. The design establishes that product rather than contract identifiers are used. It has an owner, configuration, test, and evidence. Review checks allowed and denied behavior. A document is insufficient where deployed configuration does not match. Changes are versioned and tests repeated before real data. If it fails, the product remains disabled.