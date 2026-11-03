"""Host-side ingestion service for the adjacent RAG project."""

import sys
from pathlib import Path

# The RAG project also runs standalone and uses top-level stores/representations
# imports. Make those same modules available when launching `ingest.api`.
RAG_ROOT = Path(__file__).resolve().parent.parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))
