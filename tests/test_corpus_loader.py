import unittest

from RAG_medils.ingest.corpus.loader import (
    document_metadata,
    is_single_unit,
    render,
    strip_redundant_preamble,
)

EMAIL = {
    "id": "email1327",
    "type": "email",
    "title": "AVISO: Su buzón ha superado el límite de almacenamiento",
    "language": "es",
    "tags": ["Email"],
    "related": [],
    "metadata": {
        "createdDateTime": "2024-02-16T09:00:00Z",
        "from": {"name": "Administrador del Webmail", "email": "admin@webmail-soporte-cuota.info"},
        "to": [{"name": "Elena Villegas Carmona", "email": "elena.villegas@urbeterra.es"}],
        "thread_id": "thread-email1327",
    },
    "content": {
        "body": "**Fecha:** 16/02/2024\n**Asunto:** AVISO: Su buzón ha superado el límite de almacenamiento"
        "\n\nEstimada usuaria:\n\nLe informamos."
    },
}

CHAT = {
    "id": "chat_conversation582",
    "type": "chat",
    "title": "Elena ↔ Gabriel — 15/02/2024",
    "language": "es",
    "tags": ["ChatConversation"],
    "related": [],
    "metadata": {
        "createdDateTime": "2024-02-15T16:31:00Z",
        "participants": ["Gabriel Ramos Soria", "Elena Villegas Carmona"],
    },
    "content": {"messages": [
        {"date": "2024-02-15T16:31:00Z", "author": "Gabriel Ramos Soria", "message": "buenas!"},
        {"date": "2024-02-15T16:34:00Z", "author": "Elena Villegas Carmona", "message": "genial, gracias!"},
    ]},
}


class CorpusLoaderTests(unittest.TestCase):
    def test_email_matches_spec_header(self):
        self.assertEqual(
            render(EMAIL),
            "ID: email1327\n"
            "Type: email\n"
            "Title: AVISO: Su buzón ha superado el límite de almacenamiento\n"
            "Language: es\n"
            "Tags: Email\n"
            "Created Date: 2024-02-16T09:00:00Z\n"
            "From: Administrador del Webmail (admin@webmail-soporte-cuota.info)\n"
            "To: Elena Villegas Carmona (elena.villegas@urbeterra.es)\n"
            "Thread ID: thread-email1327\n"
            "Body:\n"
            "Estimada usuaria:\n\nLe informamos.\n",
        )

    def test_chat_messages_are_merged_into_one_document(self):
        text = render(CHAT)
        self.assertIn("[16:31] Gabriel Ramos Soria: buenas!\n[16:34] Elena Villegas Carmona: genial, gracias!", text)
        self.assertFalse(is_single_unit(CHAT))

    def test_strategy_by_type(self):
        for doc_type in ("email", "event", "note", "task"):
            self.assertTrue(is_single_unit({"id": "x", "type": doc_type}))
        for doc_type in ("document", "chat"):
            self.assertFalse(is_single_unit({"id": "x", "type": doc_type}))
        with self.assertRaises(ValueError):
            is_single_unit({"id": "x", "type": "pdf"})

    def test_preamble_keeps_informative_lines(self):
        body = "**Evento:** Reunión\n**Fecha:** 19/02/2024\n**Lugar:** Sala A\n\nTexto."
        self.assertEqual(strip_redundant_preamble(body), "**Lugar:** Sala A\n\nTexto.")

    def test_document_metadata_keeps_created_date_top_level(self):
        metadata = document_metadata(EMAIL)
        self.assertEqual(metadata["createdDateTime"], "2024-02-16T09:00:00Z")
        self.assertEqual(metadata["dataset_id"], "email1327")
        self.assertEqual(metadata["metadata"]["thread_id"], "thread-email1327")


if __name__ == "__main__":
    unittest.main()
