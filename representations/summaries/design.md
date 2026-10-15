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
MIN_NODES_FOR_NEXT_LEVEL = 5
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
Are there >= 5 nodes?
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
