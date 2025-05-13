"""
Módulo responsável por buscar e filtrar registros de faturas vencidas.
"""

from datetime import date, datetime
from typing import List, Tuple
from aiohttp import ClientSession
from urllib.parse import urljoin

import config

async def fetch_records(
    session: ClientSession,
    today: date
) -> List[Tuple[str, str, str]]:
    """
    Busca registros via POST na API de seed e retorna
    lista de tuplas (invoice_id, due_date_str, invoice_url)
    somente para faturas com due_date <= today.
    """
    async with session.post(config.API_SEED_ENDPOINT, json={}) as resp:
        resp.raise_for_status()
        payload = await resp.json()

    filtered: List[Tuple[str, str, str]] = []
    for item in payload.get("data", []):
        due_date = datetime.strptime(item["duedate"], config.DATE_FORMAT).date()
        if due_date <= today:
            invoice_url = urljoin(config.BASE_URL, item["invoice"])
            filtered.append((item["id"], item["duedate"], invoice_url))
    return filtered