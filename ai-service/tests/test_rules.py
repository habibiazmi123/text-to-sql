from unittest.mock import patch, MagicMock


def test_retrieve_relevant_rules_returns_string():
    with patch("app.rag.rules_retriever.psycopg2") as mock_psycopg2:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_cur.fetchall.return_value = [
            (1, "Revenue", "Total amount of paid orders", 0.95),
        ]

        from app.rag.rules_retriever import retrieve_relevant_rules
        result = retrieve_relevant_rules("berapa revenue")

        assert "BUSINESS RULES:" in result
        assert "Revenue" in result


def test_retrieve_relevant_rules_empty():
    with patch("app.rag.rules_retriever.psycopg2") as mock_psycopg2:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_cur.fetchall.return_value = []

        from app.rag.rules_retriever import retrieve_relevant_rules
        result = retrieve_relevant_rules("random question")

        assert result == ""


def test_index_business_rules():
    with patch("app.rag.rules_indexer.psycopg2") as mock_psycopg2, \
         patch("app.rag.rules_indexer.embed_texts") as mock_embed:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        mock_cur.fetchall.return_value = [
            (1, "Revenue", "Total amount"),
            (2, "Active User", "Placed order in 30 days"),
        ]
        mock_embed.return_value = [[0.1] * 384, [0.2] * 384]

        from app.rag.rules_indexer import index_business_rules
        result = index_business_rules()

        assert result["rules_indexed"] == 2
        # 1 SELECT + 2 UPDATEs = 3 calls
        assert mock_cur.execute.call_count == 3
