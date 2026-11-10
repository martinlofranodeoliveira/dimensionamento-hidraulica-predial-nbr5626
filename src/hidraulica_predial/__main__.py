"""Ponto de entrada quando executado como módulo: python -m hidraulica_predial."""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
