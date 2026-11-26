# SPECS FOR RAG WITH HERIARCHICAL SUMMARIES, ADOPTED FROM RAPTOR

The goal is to adpot the current work developed and reuse the components, as well as the frontend UI.&#32;

Our first goal is to evaluate the system, for this I have already built a dataset with 6 types of files : chats, documents, emails, events, notes, tasks which represents a real-like corpus of a company, this is located in the folder data/ path>. /home/peyzaguirre/learning/RAG\_medils/data.

&#32;On top of this dataset we have a dataset with questions and GT answers, doc\_ids, etc. this is located in the folder evaluation/ path> /home/peyzaguirre/learning/RAG\_medils/evaluation

So, we need to ingest, evaluate the system over this dataset and calculate these metrics over all the corpus.:&#32;

Document Hit@10

Document Recall@10

Document nDCG@10

Document MRR@10

Document MAP@10

Text Evidence Recall@10

Text Evidence Hit@10

our second objective is to ingest the data and allow a client to interact with a chatbot through the UI over the ingested data.&#32;

Important things to consider:

0\) We start from the json files from the dataset with the parsed text and metadata, no need of ocr for this controlled experiment.

1\) METADATA: keep it for each chunk in qdrant as the payload. Summaries within one document could still keep the doc metadata however summaries cross documents and at corpus level will obviously not have a payload with metadata. Also keep the current hierarchical structure and rules that was implemented.

2\) ingest according the fyle type :

2.1 for documents use hierarchical summaries

2.2 for chats use hierarchical summaries. For chats merge all the messages and treat it as one document. For example the follfowing section should be treated as one document:  "content": {

&#32;&#32;&#32;"messages": \[

&#32;&#32;&#32;&#32;{

"date": "2024-02-15T16:31:00Z",

"author": "Gabriel Ramos Soria",

"message": "buenas! primer día ya, eh. wifi: UrbeTerra\_2024 y la clave te la paso ahora por aquí. Soy Gabriel, de UrbeTerra Estudios e Inversiones Territoriales S.L., por si acaso jaja"

&#32;&#32;&#32;&#32;},

&#32;&#32;&#32;&#32;{

"date": "2024-02-15T16:31:00Z",

"author": "Gabriel Ramos Soria",

"message": "la segunda llave del portal está en el cajón de la entrada"

&#32;&#32;&#32;&#32;},

&#32;&#32;&#32;&#32;{

"date": "2024-02-15T16:34:00Z",

"author": "Elena Villegas Carmona",

"message": "genial, gracias! y la cafetera, cómo va?"

&#32;&#32;&#32;&#32;},

&#32;&#32;&#32;&#32;{

"date": "2024-02-15T16:35:00Z",

"author": "Gabriel Ramos Soria",

"message": "hay que darle un golpecito para que suelte la cápsula"

&#32;&#32;&#32;&#32;}

&#32;&#32;&#32;\]

&#32;&#32;}

2.3 for emails, events, notes and tasks do not use hierarchical summaries, instead they are considered one independent unit and just check they are below the allowed token treshold for embedding and save it to the vector db. Also and very importantly, you would need to include the metadata as a header in plain text in each unit. For example consider the following section you would see in the email.json dataset:

{

&#32;&#32;"id": "email1327",

"type": "email",

"title": "AVISO: Su buzón ha superado el límite de almacenamiento",

"language": "es",

"tags": \[

"Email"

&#32;&#32;\],

"related": \[\],

"metadata": {

"createdDateTime": "2024-02-16T09:00:00Z",

"from": {

"name": "Administrador del Webmail",

"email": "admin@webmail-soporte-cuota.info"

&#32;&#32;&#32;},

"to": \[

&#32;&#32;&#32;&#32;{

"name": "Elena Villegas Carmona",

"email": "elena.villegas@urbeterra.es"

&#32;&#32;&#32;&#32;}

&#32;&#32;&#32;\],

"thread\_id": "thread-email1327"

&#32;&#32;},

"content": {

"body": "\*\*Fecha:\*\* 16/02/2024\\n\*\*Asunto:\*\* AVISO: Su buzón ha superado el límite de almacenamiento\\n\\nEstimada usuaria:\\n\\nLe informamos de que su buzón de correo elena.villegas@urbeterra.es ha alcanzado el límite de almacenamiento permitido. Según nuestros registros, actualmente está ocupando 2,1 GB de un límite de 2 GB.\\n\\nComo consecuencia, su cuenta dejará de recibir correo nuevo en un plazo de 24 horas. Los mensajes que lleguen a partir de ese momento serán rechazados y devueltos a sus remitentes, por lo que podría perder comunicaciones importantes.\\n\\nPara evitar la suspensión y mantener su servicio activo, es necesario que valide su cuenta cuanto antes. Para ello, acceda al siguiente enlace e introduzca su usuario y su contraseña actuales en el formulario de verificación:\\n\\nhttp://webmail-soporte-cuota.info/validar-cuenta\\n\\nUna vez completada la validación, se restablecerá automáticamente la capacidad de su buzón y no tendrá que realizar ninguna otra gestión. El proceso lleva menos de un minuto.\\n\\nSi no realiza la validación dentro del plazo indicado, su cuenta quedará desactivada y se eliminarán los datos asociados a la misma. Lamentamos las molestias que esto pueda ocasionarle y le agradecemos su colaboración.\\n\\nEste mensaje se ha generado de forma automática. Por favor, no responda directamente a este correo, ya que el buzón no está supervisado.\\n\\nAtentamente,\\n\\nAdministrador del Webmail\\nSoporte Webmail Administración\\nSoporte Técnico Correo"

&#32;&#32;}

The ideal transform for embbeding would be:&#32;

ID: email1327

Type: email

Title: AVISO: Su buzón ha superado el límite de almacenamiento

Language: es

Tags: Email

Created Date: 2024-02-16T09:00:00Z

From: Administrador del Webmail (admin@webmail-soporte-cuota.info)

To: Elena Villegas Carmona (elena.villegas@urbeterra.es)

Thread ID: thread-email1327

Body:

Estimada usuaria:

Le informamos de que su buzón de correo elena.villegas@urbeterra.es ha alcanzado el límite de almacenamiento permitido. Según nuestros registros, actualmente está ocupando 2,1 GB de un límite de 2 GB.

Como consecuencia, su cuenta dejará de recibir correo nuevo en un plazo de 24 horas. Los mensajes que lleguen a partir de ese momento serán rechazados y devueltos a sus remitentes, por lo que podría perder comunicaciones importantes.

Para evitar la suspensión y mantener su servicio activo, es necesario que valide su cuenta cuanto antes. Para ello, acceda al siguiente enlace e introduzca su usuario y su contraseña actuales en el formulario de verificación:

<http://webmail-soporte-cuota.info/validar-cuenta>

Una vez completada la validación, se restablecerá automáticamente la capacidad de su buzón y no tendrá que realizar ninguna otra gestión. El proceso lleva menos de un minuto.

Si no realiza la validación dentro del plazo indicado, su cuenta quedará desactivada y se eliminarán los datos asociados a la misma. Lamentamos las molestias que esto pueda ocasionarle y le agradecemos su colaboración.

Este mensaje se ha generado de forma automática. Por favor, no responda directamente a este correo, ya que el buzón no está supervisado.

Atentamente,

Administrador del Webmail

Soporte Webmail Administración

Soporte Técnico Correo

3. Deactivate the query rewrite step before the retrieval.
4. Implement a CLI for running the experiment on bash, because I imagine it would take time for the whole corpus.&#32;
