import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from downloader import download_invoice
from unittest.mock import MagicMock, AsyncMock

class AsyncContextManager:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

@pytest.mark.asyncio
async def test_download_invoice_success(tmp_path):
    """
    Testa se download_invoice salva o arquivo corretamente.
    """
    content = b"PDF DATA"

    # Resposta simulada: conteúdo e status
    mock_response = MagicMock()
    mock_response.read = AsyncMock(return_value=content)
    mock_response.raise_for_status = MagicMock()

    session = MagicMock()
    session.get.return_value = AsyncContextManager(mock_response)

    invoice_id = "123"
    url = "http://site.com/invoice.pdf"
    result = await download_invoice(session, invoice_id, url, tmp_path)

    file = tmp_path / f"{invoice_id}.pdf"
    assert file.exists()
    assert file.read_bytes() == content
    assert result == invoice_id
