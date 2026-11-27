# Informe de evaluación de recuperación: rag/v2

**Fecha:** 27 de noviembre de 2026
**Rama:** `rag/v2` (último commit en GitHub: `fe2b0b7`; hay cambios locales pendientes de subir, ver §6)
**Tenant:** `company_benchmark`
**Benchmark:** `evaluation/questions_easy.json`, versión del 27/11/2026: 578 preguntas, 962 hechos

## 1. Objetivo

Medir la calidad de recuperación del sistema RAG con resúmenes jerárquicos (estilo RAPTOR) sobre el corpus empresarial `company_benchmark`. Los resultados de esta variante (rag/v2) sirven de referencia para compararla con la variante con clustering entre documentos (rag/v3-cross-doc). En esta fase solo se evalúa la recuperación; la generación de respuestas y su evaluación con un modelo juez quedan para una fase posterior.

## 2. Sistema evaluado

### 2.1 Corpus e ingesta

Se ingestaron los 6.142 registros del corpus. Ninguno falló.

| Tipo de registro | Registros | Representación |
| --- | --- | --- |
| `document` | 1.925 | Jerarquía RAPTOR: chunks semánticos (200–500 tokens), clusters UMAP + GMM y resumen del documento |
| `chat` | 846 | Mensajes concatenados (`[HH:MM] Autor: mensaje`) y la misma jerarquía RAPTOR |
| `email`, `event`, `note`, `task` | 3.371 | Unidad independiente con cabecera de metadatos en texto plano, sin resúmenes |

Por encima de los documentos hay un único resumen de todo el corpus (nodo *catalog*). Se construye resumiendo por lotes los 2.771 resúmenes de documento; no se forman clusters entre documentos.

### 2.2 Índice

En total hay 16.172 nodos indexados en Qdrant (vectores densos `bge-m3` y dispersos `milco-650m`, fusionados con RRF):

| Ámbito | Nodos | | Nivel | Nodos |
| --- | --- | --- | --- | --- |
| `passage` (chunks y unidades) | 12.316 | | 0 | 12.316 |
| `document_cluster` | 959 | | 1 | 3.524 |
| `document` | 2.771 | | 2 | 196 |
| `catalog` | 1 | | 3 | 10 |
| | | | 4 | 1 |

La consulta se envía literalmente: la reescritura de consultas está desactivada y no hay filtros de fecha.

## 3. Incidencias y correcciones

| Incidencia | Causa | Corrección |
| --- | --- | --- |
| La ingesta se detuvo al guardar en PostgreSQL | `qwen3:14b` devolvió un texto vacío en 2 de los 16.046 resúmenes | Reintento automático ante respuestas vacías (3 intentos, `SUMMARY_EMPTY_RETRIES`), y al reanudar se regeneran los checkpoints con nodos vacíos |
| La evaluación falló al final de `run` | `metrics.py` se importaba con dos nombres distintos en el mismo proceso y su métrica de Prometheus se registraba dos veces | Import unificado a `RAG_medils.metrics` en `semantic_search.py` |
| Servicio de embeddings no disponible (27/11, 13:21) | Se detuvieron de forma controlada los contenedores `vectorizer` (8089) y `chunker` (8085) | Se volvió a arrancar `vectorizer` (`docker compose start`). `chunker` sigue parado; solo hace falta para ingestar |

## 4. Protocolo de evaluación

El benchmark cambió de formato el 27/11. En lugar de `relevant_doc_ids`, cada pregunta trae una lista de **hechos**, y cada hecho tiene **alternativas** equivalentes y sin orden: todos los sitios donde aparece (`doc_id` y, en las alternativas de texto, el fragmento exacto `text`). Un hecho aparece de media en 2 documentos distintos (mediana) y como máximo en 859. Solo 224 preguntas tienen un único documento válido.

Reglas acordadas, con *k* = 10 nodos recuperados (de media equivalen a 7,9 documentos distintos):

- **Documento relevante:** cualquier `doc_id` de cualquier alternativa. Basta con recuperar uno.
- **Document Hit@10:** 1 si al menos un documento recuperado es relevante.
- **Document MRR@10:** 1 ÷ la posición del primer documento relevante.
- **Document nDCG@10:** el ideal es un documento relevante en la posición 1, es decir, 1 / log₂(posición + 1) del primer acierto.
- **Text Evidence Recall@10:** hechos encontrados ÷ hechos de la pregunta. Un hecho se encuentra si el `text` de cualquiera de sus alternativas aparece en el texto de cualquier nodo recuperado, o en los chunks de origen de un resumen recuperado. La comparación ignora mayúsculas, espacios repetidos y `**`.
- **Text Evidence Hit@10:** 1 si se encuentra al menos un hecho.
- **Strict:** la misma métrica de evidencia sin contar los chunks de origen de los resúmenes.

Recall y MAP de documento no se calculan: dividen por el número de documentos relevantes y castigarían la redundancia (con 859 alternativas, el máximo posible sería 0,01).

## 5. Resultados

### 5.1 Resultados globales (578 preguntas)

| Métrica | rag/v2 |
| --- | --- |
| Document Hit@10 | **0,891** |
| Document MRR@10 | **0,698** |
| Document nDCG@10 | **0,745** |
| Text Evidence Recall@10 | **0,781** |
| Text Evidence Hit@10 | **0,830** |
| Text Evidence Recall@10 (strict) | 0,714 |
| Text Evidence Hit@10 (strict) | 0,791 |

**Posición del primer documento relevante:** está en la posición 1 en 341 preguntas (59%), en la 2 en 81 y en las posiciones 3–5 en 66. En **63 preguntas (10,9%) no se recupera ningún documento relevante**.

**Composición del top 10:** el 66% de los nodos son chunks, el 29% resúmenes de documento y el 6% resúmenes de cluster. El nodo *catalog* no se recuperó en ninguna pregunta.

### 5.2 Por tipo de recuperación y de razonamiento

| Segmento | n | Hit | MRR | nDCG | Evid. Recall | Evid. Hit |
| --- | --- | --- | --- | --- | --- | --- |
| `retrieval_type = single` | 448 | 0,893 | 0,736 | 0,775 | 0,893 | 0,900 |
| `retrieval_type = multiple` | 130 | 0,885 | 0,567 | 0,644 | **0,394** | 0,592 |
| `reasoning_type = explicit` | 472 | 0,873 | 0,703 | 0,745 | 0,889 | 0,898 |
| `reasoning_type = implicit` | 106 | 0,972 | 0,677 | 0,750 | **0,297** | 0,528 |

### 5.3 Por tipo de respuesta

| `answer_type` | n | Hit | MRR | nDCG | Evid. Recall | Evid. Hit |
| --- | --- | --- | --- | --- | --- | --- |
| text | 223 | 0,874 | 0,717 | 0,756 | 0,830 | 0,830 |
| list | 176 | 0,835 | 0,673 | 0,712 | 0,925 | 0,949 |
| number | 107 | 0,972 | 0,742 | 0,799 | **0,528** | 0,551 |
| summary | 47 | 0,979 | 0,562 | 0,663 | 0,543 | 1,000 |
| date | 17 | 1,000 | 0,897 | 0,923 | 1,000 | 1,000 |
| composite | 5 | 1,000 | 0,800 | 0,852 | 0,300 | 0,400 |
| name | 3 | 0,333 | 0,056 | 0,119 | 1,000 | 1,000 |

Las 63 preguntas sin ningún documento relevante son sobre todo de tipo `list` (29) y `text` (28).

### 5.4 Por tipo del primer documento relevante recuperado

| Tipo | n | MRR | nDCG | Evid. Recall | Evid. Hit |
| --- | --- | --- | --- | --- | --- |
| document | 308 | 0,841 | 0,880 | 0,957 | 0,958 |
| email | 158 | 0,668 | 0,749 | **0,544** | 0,696 |
| chat | 33 | 0,828 | 0,871 | 1,000 | 1,000 |
| note | 14 | 0,751 | 0,810 | 1,000 | 1,000 |
| event / task | 2 | — | — | — | — |
| ninguno | 63 | 0 | 0 | 0,343 | 0,413 |

## 6. Análisis

1. **Encontrar un documento válido no es el problema.** Hit@10 = 0,89 y el primer acierto suele estar en la posición 1–2. Lo que falla es recuperar **todos los hechos** de las preguntas que necesitan varios: en las preguntas `multiple` (130) el recall de evidencia baja a 0,39, y en las `implicit` (106) a 0,30.
2. **Respuestas numéricas:** se encuentra el documento correcto (Hit 0,97), pero el fragmento solo en la mitad de los casos (Recall 0,53). Hay que revisar si la causa es la coincidencia exacta del formato del número (por ejemplo `38.600,00 €` frente a `38.600 €`) o que la cifra quede en un chunk que no se recupera.
3. **Emails:** cuando el primer documento válido es un email, la evidencia baja a 0,54, frente a 0,96 en los documentos. Una posible causa es que la cabecera de metadatos ocupe buena parte del texto embebido en emails cortos.
4. **Resúmenes:** contar sus chunks de origen añade unos 7 puntos de recall de evidencia. Los resúmenes sí recuperan el documento correcto, pero no reproducen el texto literal.
5. **Nodo catalog:** nunca se recupera. Con el diseño actual, el nivel de corpus no aporta nada a la recuperación. Es una de las motivaciones de rag/v3-cross-doc.

## 7. Limitaciones

- Text Evidence acepta un fragmento en cualquier nodo recuperado, aunque sea de otro documento. Los fragmentos muy cortos (cifras) podrían coincidir por casualidad.
- La coincidencia es por texto normalizado, no por las posiciones `start`/`end`: los chunks no conservan los offsets del texto original.
- Las alternativas de tipo `metadata` solo cuentan a nivel de documento.
- Las unidades de más de 500 palabras (alrededor del 2%) se guardan como resumen. Su evidencia se busca en el registro original.
- Los resultados sobre el benchmark anterior (558 preguntas, formato `relevant_doc_ids`) no son comparables con estos.

## 8. Estado y siguientes pasos

**Pendiente de subir a `rag/v2`:** la corrección de resúmenes vacíos, la corrección del import de métricas, el evaluador adaptado al formato de hechos (con sus tests) y la actualización del README con estos resultados.

**Siguientes pasos:**
1. Opcional: añadir Recall@10 y All-found@10 de hechos a nivel de documento, como define el README del benchmark.
2. Crear la rama `rag/v3-cross-doc` con clustering UMAP + GMM sobre los resúmenes de documento, e indexar los niveles entre documentos (solo con procedencia, sin metadatos).
3. Evaluar v3 con este mismo protocolo y comparar segmento a segmento con esta referencia, incluyendo la proporción del top 10 que ocupan los nodos entre documentos.

**Archivos de resultados:** `evaluation/results/20261127T124651Z/summary.json` y `per_question.jsonl`.
