Date: 2026-06-28T09:15:00Z
Author: Alba Prieto Mora
Message: Global validation now covers all 62 procedures, but five warnings remain for mandatory fields without direct mappings.

Date: 2026-06-28T09:17:00Z
Author: Javier Ortega Campos
Message: We need to decide whether these are missing values, justified exceptions or model problems.

Date: 2026-06-28T09:19:00Z
Author: Mireia Soler Pons
Message: Three warnings concern the appeal authority; the source only states that an appeal exists, not the specific authority.

Date: 2026-06-28T09:21:00Z
Author: Luis Noguera Sáez
Message: Municipal units confirm that the authority depends on the case and is determined when the decision is issued.

Date: 2026-06-28T09:24:00Z
Author: Clara Ibáñez Soto
Message: Then we should not invent a value or use a generic authority.

Date: 2026-06-28T09:27:00Z
Author: Mireia Soler Pons
Message: We can use conditional-at-resolution with a provenance note and display rule.

Date: 2026-06-28T09:30:00Z
Author: Sergio Vidal Cruz
Message: Validation should accept that code only when the corresponding municipal evidence exists.

Date: 2026-06-28T09:33:00Z
Author: Alba Prieto Mora
Message: The fourth warning is notification channel. The procedure allows electronic or postal notification depending on citizen choice.

Date: 2026-06-28T09:36:00Z
Author: Javier Ortega Campos
Message: That requires a list of options rather than one mandatory single value.

Date: 2026-06-28T09:39:00Z
Author: Mireia Soler Pons
Message: I will modify the cardinality and add selection-dependent.

Date: 2026-06-28T09:42:00Z
Author: Luis Noguera Sáez
Message: The fifth warning concerns a fee. The ordinance says a fee may apply, but the amount changes annually.

Date: 2026-06-28T09:45:00Z
Author: Clara Ibáñez Soto
Message: We must separate fee applicability, amount and effective date.

Date: 2026-06-28T09:48:00Z
Author: Alba Prieto Mora
Message: We can map feeApplicable=true and link the amount to the annual table.

Date: 2026-06-28T09:51:00Z
Author: Sergio Vidal Cruz
Message: The API should return the amount valid for queryDate and data-not-available if the annual table is missing.

Date: 2026-06-28T09:54:00Z
Author: Javier Ortega Campos
Message: Do these decisions maintain 98.4 percent coverage without hiding uncertainty?

Date: 2026-06-28T09:57:00Z
Author: Mireia Soler Pons
Message: Yes. The fields are considered covered through explicit rules rather than invented values.

Date: 2026-06-28T10:00:00Z
Author: Luis Noguera Sáez
Message: I will request written confirmation for appeal authority and notification channel.

Date: 2026-06-28T10:03:00Z
Author: Clara Ibáñez Soto
Message: The fee table must have an owner responsible for annual updates.

Date: 2026-06-28T10:06:00Z
Author: Alba Prieto Mora
Message: We will assign that responsibility to the municipal finance unit and record the next review.

Date: 2026-06-28T10:10:00Z
Author: Javier Ortega Campos
Message: Agreed: three conditional codes with evidence, multiple cardinality for notification and a date-versioned fee; no critical errors remain.