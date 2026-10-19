VERDANT DATA QUALITY REPORT V1.0

1. Summary

This report evaluates energy readings and derived products received during the VERDANT pilot. Evaluation covers temporal continuity, units, identifiers, quality codes, meter replacements, aggregation, coverage, and provenance.

The main dataset contains sixty-two installations, sixty-four devices, and eighty-nine observation days. The difference between installations and devices results from two physical replacements. The system expected ninety-six fifteen-minute intervals per complete day and device, with documented adjustments for clock changes.

2. Overall results

Measured readings cover 97.8% of expected intervals. Estimated readings account for 1.4%, corrected readings 0.3%, and records marked missing 0.5%. There are no null values without a quality code.

The review identified thirty-one gap sequences, fourteen negative readings, nine unit changes, seven reused device identifiers, and four hourly products calculated with incomplete coverage. Every case was reviewed before final delivery.

3. Principles

Quality is not summarized by one percentage. Every dimension has a rule, severity, exception, and evidence. An estimated value may be valid where declared. A measured reading may be incorrect where its unit or interval is inconsistent.

4. Method

The pipeline compared manifests, profiled fields, validated schemas, checked continuity, calculated aggregates, and reviewed a sample. Corrections ran through versioned rules and retained the original value.

Quality analysis 1

Dimension 1, completeness, covers expected, present, and missing intervals. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 2

Dimension 2, continuity, covers temporal sequence and clock changes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 3

Dimension 3, identity, covers installations, devices, and replacements. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 4

Dimension 4, units, covers kWh, kW, and conversions. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 5

Dimension 5, ranges, covers negative values, outliers, and contracted power. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 6

Dimension 6, quality, covers measured, estimated, corrected, and missing. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 7

Dimension 7, aggregation, covers contributions, coverage, and rule. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 8

Dimension 8, provenance, covers source, batch, rule, and version. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 9

Dimension 9, bilingualism, covers labels, descriptions, and codes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 10

Dimension 10, manifest, covers counts, checksums, and exclusions. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 11

Quality case 1 is a sequence missing because of communication failure. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 12

Quality case 2 is a negative reading caused by reversed direction. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 13

Quality case 3 is a change from kWh to Wh. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 14

Quality case 4 is an identifier reused after replacement. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 15

Quality case 5 is a daylight-saving transition hour. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 16

Quality case 6 is an hourly product with three of four intervals. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 17

Quality case 7 is an estimated value later replaced by corrected. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 18

Quality case 8 is average power above contracted power. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 19

The four incomplete hourly products were recalculated after intervals were confirmed. The original version remains archived and is not distributed. The final manifest states zero products below the coverage threshold.

Quality analysis 20

Comparison between SolCentro and NEXUS verified counts, daily totals, event counts, and quality codes. Rounding differences were resolved by aggregating before rounding.

Quality analysis 21

The recommendation is to retain alerts for unit changes, prevent deviceId reuse, and publish coverage with the value. The next load will reuse this batch as regression data.

Quality analysis 22

Dimension 1, completeness, covers expected, present, and missing intervals. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 23

Dimension 2, continuity, covers temporal sequence and clock changes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 24

Dimension 3, identity, covers installations, devices, and replacements. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 25

Dimension 4, units, covers kWh, kW, and conversions. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 26

Dimension 5, ranges, covers negative values, outliers, and contracted power. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 27

Dimension 6, quality, covers measured, estimated, corrected, and missing. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 28

Dimension 7, aggregation, covers contributions, coverage, and rule. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 29

Dimension 8, provenance, covers source, batch, rule, and version. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 30

Dimension 9, bilingualism, covers labels, descriptions, and codes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 31

Dimension 10, manifest, covers counts, checksums, and exclusions. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 32

Quality case 1 is a sequence missing because of communication failure. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 33

Quality case 2 is a negative reading caused by reversed direction. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 34

Quality case 3 is a change from kWh to Wh. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 35

Quality case 4 is an identifier reused after replacement. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 36

Quality case 5 is a daylight-saving transition hour. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 37

Quality case 6 is an hourly product with three of four intervals. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 38

Quality case 7 is an estimated value later replaced by corrected. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 39

Quality case 8 is average power above contracted power. Review compares the source, event, rule, and context. A value is not automatically corrected merely because it appears unusual. The decision may accept, correct, mark missing, exclude from aggregation, or request confirmation. The result retains its owner, date, and explanation. Where other records may be affected, a scope review is performed.

Quality analysis 40

The four incomplete hourly products were recalculated after intervals were confirmed. The original version remains archived and is not distributed. The final manifest states zero products below the coverage threshold.

Quality analysis 41

Comparison between SolCentro and NEXUS verified counts, daily totals, event counts, and quality codes. Rounding differences were resolved by aggregating before rounding.

Quality analysis 42

The recommendation is to retain alerts for unit changes, prevent deviceId reuse, and publish coverage with the value. The next load will reuse this batch as regression data.

Quality analysis 43

Dimension 1, completeness, covers expected, present, and missing intervals. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 44

Dimension 2, continuity, covers temporal sequence and clock changes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 45

Dimension 3, identity, covers installations, devices, and replacements. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 46

Dimension 4, units, covers kWh, kW, and conversions. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 47

Dimension 5, ranges, covers negative values, outliers, and contracted power. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 48

Dimension 6, quality, covers measured, estimated, corrected, and missing. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 49

Dimension 7, aggregation, covers contributions, coverage, and rule. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 50

Dimension 8, provenance, covers source, batch, rule, and version. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.

Quality analysis 51

Dimension 9, bilingualism, covers labels, descriptions, and codes. The test records the field, rule, result, severity, and exception. Critical errors block derived products. Warnings are accepted with an identified justification. The manual sample contains installations with high and low use, export, meter replacement, and gaps. A correction is evaluated against a regression set and retains the earlier result.