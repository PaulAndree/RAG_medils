SOLCENTRO DATA DICTIONARY FOR VERDANT V1.1

Purpose

This dictionary describes fields in the revised SolCentro export. Version 1.1 adds the stable installation identifier, time zone, quality code, contracted power, and distinction between reset and replacement. It supports ingestion but does not define authorized products.

General rules

Every field has a name, type, cardinality, unit, description, example, provenance, requirement status, and null handling. The original value is retained where a transformation changes format. Personal and contractual fields are not part of the export.

Identifiers and time

`installationId` is the historical key; `deviceId` identifies the meter and may change; `sourceRecordId` locates the source record. `intervalStart` and `intervalEnd` use ISO 8601 with a UTC offset. `durationMinutes` must equal fifteen.

Measures

`importedEnergyKWh`, `exportedEnergyKWh`, and `averagePowerKW` are decimals. `contractedPowerKW` belongs to the installation. Values are not rounded before aggregation.

Field definition 1

Field 1: `installationId`. Type: string. Cardinality: 1. Description: stable installation identifier. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 2

Field 2: `deviceId`. Type: string. Cardinality: 1. Description: physical meter identifier. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 3

Field 3: `sourceRecordId`. Type: string. Cardinality: 1. Description: source record key. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 4

Field 4: `intervalStart`. Type: datetime. Cardinality: 1. Description: interval start. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 5

Field 5: `intervalEnd`. Type: datetime. Cardinality: 1. Description: interval end. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 6

Field 6: `timeZone`. Type: string. Cardinality: 1. Description: IANA time zone. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 7

Field 7: `durationMinutes`. Type: integer. Cardinality: 1. Description: expected duration. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 8

Field 8: `importedEnergyKWh`. Type: decimal. Cardinality: 0..1. Description: imported energy. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 9

Field 9: `exportedEnergyKWh`. Type: decimal. Cardinality: 0..1. Description: exported energy. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 10

Field 10: `averagePowerKW`. Type: decimal. Cardinality: 0..1. Description: average power. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 11

Field 11: `contractedPowerKW`. Type: decimal. Cardinality: 0..1. Description: contracted power. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 12

Field 12: `qualityCode`. Type: code. Cardinality: 1. Description: quality status. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 13

Field 13: `eventType`. Type: code. Cardinality: 0..1. Description: reset or replacement. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 14

Field 14: `eventTimestamp`. Type: datetime. Cardinality: 0..1. Description: event date. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 15

Field 15: `ingestionBatch`. Type: string. Cardinality: 1. Description: batch identifier. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 16

Field 16: `extractionDate`. Type: datetime. Cardinality: 1. Description: extraction date. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 17

Quality codes form a closed vocabulary. Measured requires a measurement; missing requires absence; estimated and corrected retain method or review information. An inconsistent combination blocks the record.

Field definition 18

Reset and replacement are not equivalent. Reset retains deviceId; replacement closes one period and opens another. The installation does not change. Readings retain the event.

Field definition 19

The delivery profile records counts of installations, devices, intervals, nulls, codes, and events. Differences from the earlier batch must be explained.

Field definition 20

Field 1: `installationId`. Type: string. Cardinality: 1. Description: stable installation identifier. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 21

Field 2: `deviceId`. Type: string. Cardinality: 1. Description: physical meter identifier. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 22

Field 3: `sourceRecordId`. Type: string. Cardinality: 1. Description: source record key. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.

Field definition 23

Field 4: `intervalStart`. Type: datetime. Cardinality: 1. Description: interval start. It includes a validation rule, example, and provenance. Where optional, absence must be compatible with the quality code or record type. An empty string does not replace a documented null. Transformations retain the source value and record the applied rule.