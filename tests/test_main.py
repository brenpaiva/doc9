import subprocess
import time
from pathlib import Path
import pytest



def test_main_script_execution(tmp_path):
    """
    Executa o script principal e valida que ele roda com sucesso e gera o CSV.
    Também informa o tempo de execução, mas sem impor limite.
    Para ativar basta executar o comando "pytest"
    """
    csv_path = tmp_path / "test_output.csv"
    download_dir = tmp_path / "invoices"

    start = time.perf_counter()

    result = subprocess.run(
        [
            "python", "main.py",
            "--csv-path", str(csv_path),
            "--download-dir", str(download_dir),
            "--max-connections", "20",
            "--timeout", "10"
        ],
        capture_output=True,
        text=True
    )

    elapsed = time.perf_counter() - start

    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)
    print(f"\nTempo de execução: {elapsed:.2f} segundos")

    assert result.returncode == 0, "Script falhou na execução"
    assert csv_path.exists(), "CSV de saída não foi criado"
