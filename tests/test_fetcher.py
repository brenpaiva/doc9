import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fetcher import fetch_records
from datetime import date
from unittest.mock import MagicMock, AsyncMock

class AsyncContextManager:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

@pytest.mark.asyncio
async def test_fetch_records_filters_only_due_invoices():
    """
    Garante que fetch_records retorna apenas faturas vencidas.
    """
    # Resposta simulada: dois itens, mas apenas o primeiro vencido antes de 13-05-2025
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()  # síncrono
    mock_response.json = AsyncMock(return_value={
        "data": [
            {"id": "1", "duedate": "10-05-2024", "invoice": "/inv1.pdf"},
            {"id": "2", "duedate": "14-05-2025", "invoice": "/inv2.pdf"},
        ]
    })

    session = MagicMock()
    session.post.return_value = AsyncContextManager(mock_response)

    result = await fetch_records(session, date(2025, 5, 13))

    assert len(result) == 1
    assert result[0][0] == "1"
