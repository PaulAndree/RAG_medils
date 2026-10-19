Sender: Sergio Vidal Cruz <sergio.vidal@upsc.example>
Recipient: Lucía Navarro Gil <lucia.navarro@upsc.example>, Eva Calderón Gil <eva.calderon@archivoregional.example>
Title: Issues in the second LUMEN ingestion

Hello,

The second ingestion processed 2,080 records and successfully loaded 1,962. The 118 failed records include forty-six encoding errors, thirty-one uninterpretable dates, twenty-two references to people without an entity, twelve duplicate identifiers, and seven missing digital files.

Most encoding errors come from a Windows-1252 export declared as UTF-8. I will not automatically convert expressions such as “spring 1947” into exact dates. Person mentions without sufficient evidence will remain unlinked.

I have attached the incident report. I propose correcting the automatic cases and performing a limited reingestion of failed records after the Regional Archive reviews dates, duplicates, and missing files.

Best regards,
Sergio