from __future__ import annotations

import sys
from pathlib import Path


def configure_imports() -> None:
    """
    Garante que o diretório raiz do projeto esteja no sys.path.

    Isso permite que imports absolutos como `from src.api.routes import ...`
    funcionem mesmo quando o entrypoint é executado como script,
    por exemplo: `python src/main.py` ou `uv run src/main.py`.
    """
    root_dir = Path(__file__).resolve().parents[1]  # .../teste tecnico
    root_str = str(root_dir)

    if root_str not in sys.path:
        sys.path.insert(0, root_str)


