"""
Общие настройки тестов: корректные пути импорта для проекта.
"""
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

for path in (str(ROOT_DIR), str(SRC_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)
