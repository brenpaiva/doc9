"""
Módulo responsável por baixar uma fatura e salvar no disco.
"""
import logging
from pathlib import Path
from typing import Optional
from aiohttp import ClientSession
from urllib.parse import urlparse



logger = logging.getLogger(__name__)

async def download_invoice(
    session: ClientSession,
    invoice_id: str,
    url: str,
    download_dir: Path
) -> Optional[str]:
    """
    Baixa a fatura e salva em download_dir.
    Retorna invoice_id em caso de sucesso, None caso contrário.
    """
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()

        ext = Path(urlparse(url).path).suffix or ".bin"
        dest = download_dir / f"{invoice_id}{ext}"
        dest.write_bytes(content)

        logger.info("Downloaded %s to %s", invoice_id, dest)
        return invoice_id
    except Exception as e:
        logger.error("Error downloading %s: %s", invoice_id, e)
        return None