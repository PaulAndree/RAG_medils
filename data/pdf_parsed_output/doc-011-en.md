VERDANT ENERGY READING SPECIFICATION V1.0

Purpose

This specification defines the minimum profile for representing energy readings in the VERDANT pilot. It covers installations, meters, intervals, imported and exported energy, power, quality, time zone, and provenance. It does not itself authorize exchange: exportable products are determined by the privacy assessment.

Identity

The installation uses a stable identifier. The device identifier is retained for traceability but may change after replacement and must not function as the historical key. A meter replacement creates a new device entity linked to the same installation and its period of use.

Time

Every reading contains a start, end, duration, and time zone. The export uses local time with a UTC offset. Seasonal time changes must not produce unexplained duplicate or missing intervals. The operational interval is fifteen minutes, equivalent to ninety-six readings per complete day and meter.

Measures and quality

`importedEnergy` and `exportedEnergy` use kWh; `averagePower` uses kW. Contracted power provides context for outliers. Quality codes are measured, estimated, corrected, and missing. A null value without a code is an error.

Provenance

Every batch retains its source, version, extraction date, owner, and checksum. Transformations record the original field, rule, and version. ES and EN versions share identifiers and structure.

Additional rule 1

Validation checks temporal continuity, constant duration, recognized unit, installation identifier, and quality code. A gap is allowed only where represented as missing and its reason is retained. A daily total does not fill intervals without a documented rule.

Additional rule 2

A reset and physical replacement are different events. A reset retains the device and records values before and after it. A replacement closes the old period and opens the new one. Neither event must be interpreted as negative consumption.

Additional rule 3

Hourly products aggregate four consecutive intervals and declare coverage, contributions, and rule. An incomplete product is not labeled as a complete hour. Corrections retain the source value and review decision.

Additional rule 4

Validation checks temporal continuity, constant duration, recognized unit, installation identifier, and quality code. A gap is allowed only where represented as missing and its reason is retained. A daily total does not fill intervals without a documented rule.

Additional rule 5

A reset and physical replacement are different events. A reset retains the device and records values before and after it. A replacement closes the old period and opens the new one. Neither event must be interpreted as negative consumption.

Additional rule 6

Hourly products aggregate four consecutive intervals and declare coverage, contributions, and rule. An incomplete product is not labeled as a complete hour. Corrections retain the source value and review decision.

Additional rule 7

Validation checks temporal continuity, constant duration, recognized unit, installation identifier, and quality code. A gap is allowed only where represented as missing and its reason is retained. A daily total does not fill intervals without a documented rule.

Additional rule 8

A reset and physical replacement are different events. A reset retains the device and records values before and after it. A replacement closes the old period and opens the new one. Neither event must be interpreted as negative consumption.

Additional rule 9

Hourly products aggregate four consecutive intervals and declare coverage, contributions, and rule. An incomplete product is not labeled as a complete hour. Corrections retain the source value and review decision.