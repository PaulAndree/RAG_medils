"""
Level 0
original chunks

Level 1
semantic cluster summaries
{
    "text": "...",

    "representation": "summary",
    "scope": "document",

    "document_id": "paper_001",
    "catalog_id": "ai_safety",

    "level": 1,

    "summary_id": "summary_001",

    "source_chunk_ids": [
        "chunk_02",
        "chunk_03",
        "chunk_07"
    ]
}
Level 2
optional document-level summary

Level 3
optional cross-document/catalog summary
{
    "representation": "summary",
    "scope": "catalog",
    "catalog_id": "ai_safety",
    "level": 2,

    "source_document_ids": [
        "paper_001",
        "paper_004",
        "paper_012"
    ],

    "source_summary_ids": [
        "summary_001",
        "summary_018",
        "summary_041"
    ]
}

stop criteria:
MIN_NODES_FOR_NEXT_LEVEL = 10
if len(current_nodes) < MIN_NODES_FOR_NEXT_LEVEL:
    stop


Qdrant collection design after indexing:

COLLECTION: passages
─────────────────────────
original chunks
document_id
chunk_id
text
embedding


COLLECTION: summaries
─────────────────────────

LEVEL 1
document-cluster summaries
scope = "document"
document_id
catalog_id
source_chunk_ids

LEVEL 2
cross-document summaries
scope = "catalog"
catalog_id
source_document_ids
source_summary_ids
"""

"""
data/passages_chunk/**/*_chunks.json
      ↓
discover documents + embed chunks with the passage embedding model
      ↓
RAPTOR soft clustering
(global UMAP → GMM → local UMAP → GMM)
      ↓
cluster summaries
      ↓
embed summaries
      ↓
Are there >= 10 nodes?
      │
      ├── YES → RAPTOR soft cluster again
      │
      └── NO  → document summary
                     ↓
              final document node
                     ↓
       collect document summaries
                     ↓
              catalog summary
"""

Meaning of each field:

node_id: unique hierarchy-node identifier.
text: LLM-generated summary.
level: hierarchy depth.
scope:- document_cluster: intermediate cluster summary.
- document: final summary of one document.
- catalog: summary across document summaries.

document_id: owning document; null for catalog nodes.
catalog_id: logical document group.
source_node_ids: immediate parent nodes used to generate this summary.
source_chunk_ids: all original chunks represented below the node.
source_document_ids: all documents represented below the node.


-----------------------------------------------------------------------------------------------
DESCRIPTION 
The summary pipeline builds a RAPTOR-style hierarchy independently for each document, then creates one final summary per catalog.
Chunk files
    ↓
Level 0 passage nodes + embeddings
    ↓
If node count ≥ 10:
    RAPTOR clustering
    ↓
One summary per semantic cluster
    ↓
Repeat while node count ≥ 10
    ↓
One final document summary
    ↓
Document summaries grouped by catalog
    ↓
One catalog summary
Full flow
1. Load and validate chunks
The builder discovers every *_chunks.json under data_root/passages_chunk and requires a non-empty chunk_list. It generates deterministic document and chunk UUIDs and embeds all chunks through the external embedding API.
See [builder.py (line 171)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:171).
One detail: chunk_title is included in the embedding input, but the summary node’s text contains only the chunk content.
2. Create level-0 nodes
Every chunk becomes an internal passage node containing:
- Its content and embedding
- level = 0
- scope = "passage"
- Its document and catalog IDs
- Provenance pointing to itself through source_chunk_ids
These level-0 nodes are used internally and are not written to the summary JSON files.
See [builder.py (line 262)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:262).
3. Build the document hierarchy
As long as the current level has at least 10 nodes, the builder clusters them.
Clustering performs:
Global UMAP reduction
    ↓
Global soft GMM clustering
    ↓
For each global cluster:
    fewer than 5 members → keep it directly
    5+ members           → local UMAP + local GMM
“Soft” means one node can belong to multiple clusters when several GMM probabilities exceed the threshold of 0.2.
See [raptor_clustering.py (line 77)](/home/peyzaguirre/learning_1/representations/summaries/raptor_clustering.py:77) and [builder.py (line 435)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:435).
Each resulting cluster is sent to the LLM to produce a document_cluster node. That summary is embedded and becomes an input node for the next hierarchy level.
If clustering fails to reduce the number of nodes, the loop stops to prevent an infinite hierarchy.
4. Create the final document summary
When fewer than 10 nodes remain, they are combined into one node with:
scope = "document"
summary_type = "document-level"
Its provenance contains:
- Immediate inputs in source_node_ids
- All underlying original chunks in source_chunk_ids
- The owning document in source_document_ids
See [builder.py (line 467)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:467).
5. Create catalog summaries
After every document is finished, document summaries are grouped by catalog_id. One catalog summary is created for every catalog, even if that catalog contains only one document.
Catalog summaries are placed one level above the deepest document hierarchy found anywhere in the run.
See [builder.py (line 657)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:657).
6. Save results
Nodes are saved as:
summaries/level_1.json
summaries/level_2.json
...
Embeddings are deliberately removed from these JSON files. Each summary retains its provenance metadata.
See [builder.py (line 539)](/home/peyzaguirre/learning_1/representations/summaries/builder.py:539).
What happens with exactly one chunk?
For a document containing one chunk:
One chunk (level 0)
    ↓
No clustering
    ↓
Document summary (level 1)
    ↓
Catalog summary
The clustering loop is skipped because 1 < MIN_NODES_FOR_NEXT_LEVEL, whose actual value is 10.
The builder directly asks the LLM to produce a document-level summary from the single chunk. Consequently:
- No UMAP is executed.
- No GMM is fitted.
- No document_cluster node is created.
- One document node is created at level 1.
- The document summary’s source_node_ids contains the chunk ID.
- Its source_chunk_ids also contains that same chunk ID.
If this is also the only document in the entire corpus/catalog, a second LLM operation creates a catalog summary from the document summary. The output will therefore normally contain:
level_1.json → one document summary
level_2.json → one catalog summary
So a one-chunk, one-document corpus produces two persisted summary nodes—not one.
The standalone clustering function is also protected against a one-item input: it immediately returns [[0]], assigning the item to cluster 0 without invoking UMAP or GMM. However, this path is not reached through normal build_document() execution because clustering starts only at 10 nodes. See [raptor_clustering.py (line 97)](/home/peyzaguirre/learning_1/representations/summaries/raptor_clustering.py:97).
There is one exceptional case: if that single chunk makes the prompt exceed SUMMARY_INPUT_TOKEN_LIMIT—currently approximately 13,500 estimated tokens—the builder raises an error asking for a smaller upstream chunk. It cannot split an individual chunk itself.