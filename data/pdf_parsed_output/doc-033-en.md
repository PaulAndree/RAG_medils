LUMEN DEMONSTRATOR FUNCTIONAL SPECIFICATION V1.0

Purpose

The LUMEN demonstrator supports search and exploration of Regional Archive objects through people, places, dates, document types, collections, and relations. The interface is available in Spanish and English and preserves the query and context when language changes.

Scope

Version 1.0 includes a home page, search, filters, result list, object page, person page, place page, relation navigation, rights presentation, help, and error handling. It does not include data editing or bulk download.

Principles

The interface must display provenance and uncertainty. An approximate date is not displayed as exact. An unlinked mention is not presented as a verified identity. An object without an authorized image uses a metadata record. Conditions of use remain visible.

Languages

Identifiers are shared. Labels and text change with language. An access translation of a title is distinguished from the source title. Language switching preserves filters, page, entity, and position where possible.

Functional requirement 1

Feature 1, basic search, accepts text and returns relevant objects, people, and places. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 2

Feature 2, filters, limits by collection, type, person, place, period, image, and rights. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 3

Feature 3, results, shows title, date, type, collection, authorized image, and snippet. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 4

Feature 4, object page, presents source, description, date, agents, places, relations, and rights. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 5

Feature 5, person page, distinguishes explicit facts, variants, activity, and relations. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 6

Feature 6, place page, shows historical variants, jurisdiction, period, and related objects. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 7

Feature 7, navigation, supports following relations and returning without losing context. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 8

Feature 8, rights, explains whether a file, thumbnail, download, or metadata only is available. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 9

Feature 9, help, defines terms, approximate dates, roles, and limitations. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 10

Feature 10, errors, uses stable codes and messages that reveal no internal details. The specification defines its input, initial state, interaction, output, empty states, errors, accessibility, and tests. Presented data must match the graph and rights policy. An abbreviated label retains access to the full definition. Journeys are tested in Spanish and English using objects from different collection types.

Functional requirement 11

Interface state 1 is no results. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 12

Interface state 2 is result without an image. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 13

Interface state 3 is approximate date. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 14

Interface state 4 is unlinked person. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 15

Interface state 5 is ambiguous place. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 16

Interface state 6 is pending rights. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 17

Interface state 7 is withdrawn object. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 18

Interface state 8 is service temporarily unavailable. The page explains its meaning, available actions, and information that cannot be asserted. Substitutes are not invented to fill gaps. A pending state is distinguished from restricted. Messages are consistent across languages and verified with users. Telemetry records the error type rather than the content of personal searches.

Functional requirement 19

Accessibility requirements include keyboard navigation, visible focus, form labels, alternative text, logical order, contrast, and field-associated messages. Technical evaluation does not replace testing with people.