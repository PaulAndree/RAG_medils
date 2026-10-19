ARIADNA FAITHFULNESS AND CITATION ERROR ANALYSIS REPORT V1.0

1. Summary

This report analyzes 120 answers with citation and faithfulness problems. The sample contains direct, temporal, multi-hop, version-comparison, and unanswerable questions. The objective is to identify failure patterns and define post-generation controls.

In forty-six answers, the citation supports part of the content but not an exception or condition. Thirty-one cite an earlier document version. In twenty-four, the correct evidence appears in a neighboring chunk that is not included. Nineteen answers combine two facts while providing one citation.

2. Method

Every answer was decomposed into atomic claims. Reviewers checked the complete source, cited chunk, neighboring chunks, date, and version relations. Error type, severity, probable cause, and correction were recorded.

An answer with correct content and incomplete evidence is not fully faithful. A citation pointing to the correct document but not allowing the relevant passage to be located receives partial credit for location rather than coverage.

3. Failure categories

Failures are grouped as partial coverage, incorrect version, chunking, one citation for several hops, thematic but non-probative source, missing citation, and poorly justified abstention. Categories may coexist.

Error analysis 1

Error category 1, partial coverage, occurs where evidence supports the rule but not a condition or exception. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 2

Error category 2, incorrect version, occurs where the citation points to a superseded source for the requested date. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 3

Error category 3, chunking, occurs where the complete claim depends on a neighboring chunk. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 4

Error category 4, single multi-hop citation, occurs where two necessary facts come from different sources or passages. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 5

Error category 5, thematic source, occurs where the document concerns the topic but does not prove the claim. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 6

Error category 6, missing citation, occurs where a factual claim has no locatable reference. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 7

Error category 7, unjustified abstention, occurs where the system claims absence without checking related sources. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 8

Proposed control 1 is claim decomposition. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 9

Proposed control 2 is coverage verification. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 10

Proposed control 3 is validity filtering. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 11

Proposed control 4 is neighboring-chunk expansion. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 12

Proposed control 5 is second-source retrieval. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 13

Proposed control 6 is relation checking. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 14

Proposed control 7 is abstention validation. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 15

Proposed control 8 is multiple-citation presentation. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 16

Analyzed example 1 concerns travel deadline and documents. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 17

Analyzed example 2 concerns current policy version. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 18

Analyzed example 3 concerns task owner and date. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 19

Analyzed example 4 concerns approval of an extension. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 20

Analyzed example 5 concerns provisional pilot date. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 21

Analyzed example 6 concerns question without a final date. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 22

The proposed check reduced insufficient single-citation cases in a controlled test but increased mean answer length. Sources should be displayed compactly with an option to expand details.

Error analysis 23

Links should open the exact passage and provide access to the complete document. A citation to an identifier without a passage forces the user to repeat the search and is considered less useful.

Error analysis 24

The next version will evaluate citation precision, claim coverage, and correction rate after the control. Results will not be mixed with the earlier baseline without a new version.

Error analysis 25

Error category 1, partial coverage, occurs where evidence supports the rule but not a condition or exception. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 26

Error category 2, incorrect version, occurs where the citation points to a superseded source for the requested date. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 27

Error category 3, chunking, occurs where the complete claim depends on a neighboring chunk. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 28

Error category 4, single multi-hop citation, occurs where two necessary facts come from different sources or passages. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 29

Error category 5, thematic source, occurs where the document concerns the topic but does not prove the claim. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 30

Error category 6, missing citation, occurs where a factual claim has no locatable reference. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 31

Error category 7, unjustified abstention, occurs where the system claims absence without checking related sources. Review records the affected claims, expected source, used citation, and action. Severity increases where the error changes a decision, date, or legal condition. A correction must improve the case and pass a regression set. A local rule is not applied where it harms questions in another category.

Error analysis 32

Proposed control 1 is claim decomposition. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 33

Proposed control 2 is coverage verification. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 34

Proposed control 3 is validity filtering. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 35

Proposed control 4 is neighboring-chunk expansion. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 36

Proposed control 5 is second-source retrieval. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 37

Proposed control 6 is relation checking. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 38

Proposed control 7 is abstention validation. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 39

Proposed control 8 is multiple-citation presentation. The component receives the answer, citations, question, and metadata. It produces a list of claims with supported, partial, unsupported, or non-factual status. Temporal controls use the reference date. Multi-hop controls require evidence for every hop. Where coverage is insufficient, the system may retrieve additional evidence, shorten the answer, or abstain.

Error analysis 40

Analyzed example 1 concerns travel deadline and documents. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 41

Analyzed example 2 concerns current policy version. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.

Error analysis 42

Analyzed example 3 concerns task owner and date. Review separates the rule, exception, date, entity, and status. One citation may cover several elements only where the passage explicitly contains them. Where two documents are required, both are presented. The error explanation avoids attributing to generation a defect originating in retrieval or chunking.