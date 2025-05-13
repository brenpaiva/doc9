"""
Entry-point do script: CLI, orquestração e relatório.
"""
import argparse
import asyncio
import csv
import logging
import time
from datetime import date
from pathlib import Path


import aiohttp
from aiohttp import ClientTimeout, TCPConnector


from fetcher import fetch_records
from downloader import download_invoice


def main():
    parser = argparse.ArgumentParser(
        description="Download overdue invoices and generate CSV report"
    )
    parser.add_argument(
        "--download-dir", default="invoices",
        help="Diretório para salvar faturas"
    )
    parser.add_argument(
        "--csv-path", default="invoices_data.csv",
        help="Caminho do relatório CSV"
    )
    parser.add_argument(
        "--max-connections", type=int, default=100,
        help="Máximo de conexões HTTP simultâneas"
    )
    parser.add_argument(
        "--timeout", type=int, default=15,
        help="Timeout total por requisição (s)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    start = time.perf_counter()
    today = date.today()
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    async def run():
        # connector e timeout dentro do loop
        connector = TCPConnector(limit=args.max_connections)
        timeout = ClientTimeout(total=args.timeout)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            records = await fetch_records(session, today)
            if not records:
                logging.info("Nenhuma fatura vencida para baixar.")
                return

            tasks = [
                download_invoice(session, inv_id, url, download_dir)
                for inv_id, _, url in records
            ]
            results = await asyncio.gather(*tasks)
            succeeded = {inv for inv in results if inv}

        # escrever CSV
        with Path(args.csv_path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Invoice ID", "Due Date", "Invoice URL"])
            for inv_id, due, url in records:
                if inv_id in succeeded:
                    writer.writerow([inv_id, due, url])

        elapsed = time.perf_counter() - start
        logging.info(
            "Finished: %d of %d invoices downloaded in %.2fs. Report at %s",
            len(succeeded), len(records), elapsed, args.csv_path
        )

    asyncio.run(run())


if __name__ == "__main__":
    main()