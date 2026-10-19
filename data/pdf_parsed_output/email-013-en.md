Sender: Tomás Leal Guerra <tomas.leal@upsc.example>
Recipient: Andrés Beltrán Vega <andres.beltran@upsc.example>
Title: Urgent review of the ARIADNA baseline metrics

Hello Andrés,

The latest hybrid baseline run reaches recall@10 of 0.94, compared with 0.78 in the previous run. We have made no change to the index or model that would explain an improvement of this size.

While reviewing a sample, I found test questions that are nearly identical to questions used during tuning. It appears that the split was created by identifier rather than semantic intent, meaning ES/EN translations and minor paraphrases may have been placed in different partitions.

I have attached the results and an initial list of duplicate candidates. I recommend that these metrics not be circulated until the split has been checked.

Best regards,
Tomás