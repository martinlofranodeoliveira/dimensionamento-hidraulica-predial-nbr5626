"""dimensionamento-hidraulica-predial-nbr5626

Dimensionamento determinístico de instalações prediais de água fria e quente (ABNT NBR 5626).
LOFRANO TECNOLOGIA.
"""

from .calculator import dimensionar_rede_hidraulica
from .codecs import carregar_projeto, resultado_para_dict
from .domain import InstalacaoPredialInput, ResultadoDimensionamento

__version__ = "1.0.0"
__all__ = [
    "dimensionar_rede_hidraulica",
    "carregar_projeto",
    "resultado_para_dict",
    "InstalacaoPredialInput",
    "ResultadoDimensionamento",
    "__version__",
]
