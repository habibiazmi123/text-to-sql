from unittest.mock import patch, MagicMock
from app.embeddings.model import embed_text, embed_texts


def test_embed_text_returns_list():
    with patch("app.embeddings.model._model", None):
        with patch("app.embeddings.model.SentenceTransformer") as MockModel:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2, 0.3])
            MockModel.return_value = mock_instance

            result = embed_text("test query")
            assert isinstance(result, list)


def test_embed_texts_returns_list():
    with patch("app.embeddings.model._model", None):
        with patch("app.embeddings.model.SentenceTransformer") as MockModel:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = MagicMock(tolist=lambda: [[0.1], [0.2]])
            MockModel.return_value = mock_instance

            result = embed_texts(["query 1", "query 2"])
            assert isinstance(result, list)
