"""Modelos de dados e validações de domínio para dimensionamento hidráulico NBR 5626.

LOFRANO TECNOLOGIA.
Todos os cálculos e representações utilizam grandezas inteiras ou frações racionais exatas.
"""

from dataclasses import dataclass, field
from fractions import Fraction
import re
from typing import Any, Dict, List, Optional

from .errors import ErroValidacaoEntrada, ERR_VALIDACAO_DOMINIO
from .tabelas_nbr5626 import (
    APARELHOS_SANITARIOS,
    COMPRIMENTOS_EQUIVALENTES_MM,
    MAPA_DIAMETROS_PVC,
)


@dataclass(frozen=True)
class ConexaoTrecho:
    """Representa conexões hidráulicas instaladas em um trecho de tubulação."""
    tipo: str
    quantidade: int

    def __post_init__(self):
        if not self.tipo or not isinstance(self.tipo, str):
            raise ErroValidacaoEntrada("O tipo de conexão deve ser uma string não vazia.", ERR_VALIDACAO_DOMINIO)
        if self.tipo not in COMPRIMENTOS_EQUIVALENTES_MM:
            raise ErroValidacaoEntrada(f"Tipo de conexão desconhecido na NBR 5626: '{self.tipo}'.", ERR_VALIDACAO_DOMINIO)
        if not isinstance(self.quantidade, int) or self.quantidade <= 0:
            raise ErroValidacaoEntrada("A quantidade de conexões deve ser um número inteiro positivo.", ERR_VALIDACAO_DOMINIO)


@dataclass(frozen=True)
class PontoConsumo:
    """Aparelho sanitário atendido pela rede hidráulica."""
    codigo_aparelho: str
    descricao: str
    quantidade: int = 1

    def __post_init__(self):
        if self.codigo_aparelho not in APARELHOS_SANITARIOS:
            raise ErroValidacaoEntrada(f"Aparelho sanitário desconhecido: '{self.codigo_aparelho}'.", ERR_VALIDACAO_DOMINIO)
        if not isinstance(self.quantidade, int) or self.quantidade <= 0:
            raise ErroValidacaoEntrada("A quantidade de aparelhos deve ser um inteiro positivo.", ERR_VALIDACAO_DOMINIO)


@dataclass(frozen=True)
class TrechoInput:
    """Especificação de engenharia de um trecho de tubulação."""
    id_trecho: str
    no_origem: str
    no_destino: str
    comprimento_real_mm: int
    desnivel_geometrico_mm: int
    conexoes: List[ConexaoTrecho] = field(default_factory=list)
    aparelhos_diretos: List[PontoConsumo] = field(default_factory=list)
    dn_fixado: Optional[int] = None

    def __post_init__(self):
        if not self.id_trecho or not isinstance(self.id_trecho, str):
            raise ErroValidacaoEntrada("O id_trecho deve ser fornecido e não vazio.", ERR_VALIDACAO_DOMINIO)
        if not self.no_origem or not self.no_destino:
            raise ErroValidacaoEntrada("Os nós de origem e destino devem ser informados.", ERR_VALIDACAO_DOMINIO)
        if self.no_origem == self.no_destino:
            raise ErroValidacaoEntrada(f"Trecho '{self.id_trecho}' não pode conectar um nó a si mesmo.", ERR_VALIDACAO_DOMINIO)
        if not isinstance(self.comprimento_real_mm, int) or self.comprimento_real_mm <= 0:
            raise ErroValidacaoEntrada(f"Comprimento do trecho '{self.id_trecho}' deve ser inteiro positivo em mm.", ERR_VALIDACAO_DOMINIO)
        if not isinstance(self.desnivel_geometrico_mm, int):
            raise ErroValidacaoEntrada(f"Desnível do trecho '{self.id_trecho}' deve ser um inteiro em mm.", ERR_VALIDACAO_DOMINIO)
        if self.dn_fixado is not None:
            if not isinstance(self.dn_fixado, int) or self.dn_fixado not in MAPA_DIAMETROS_PVC:
                raise ErroValidacaoEntrada(f"DN fixado inválido '{self.dn_fixado}' no trecho '{self.id_trecho}'.", ERR_VALIDACAO_DOMINIO)


@dataclass(frozen=True)
class InstalacaoPredialInput:
    """Projeto completo de instalação hidráulica predial."""
    nome_edificacao: str
    descricao: str
    pressao_disponivel_inicial_mmca: int
    no_origem_principal: str
    trechos: List[TrechoInput]
    criterio_velocidade_maxima_mms: int = 3000       # 3,0 m/s = 3000 mm/s (NBR 5626)
    criterio_pressao_estatica_max_mmca: int = 40000  # 40 m.c.a. (400 kPa)
    criterio_pressao_dinamica_min_mmca: int = 1000   # 1,0 m.c.a. (10 kPa)

    def __post_init__(self):
        if not self.nome_edificacao or not isinstance(self.nome_edificacao, str):
            raise ErroValidacaoEntrada("Nome da edificação deve ser informado.", ERR_VALIDACAO_DOMINIO)
        if not isinstance(self.pressao_disponivel_inicial_mmca, int) or self.pressao_disponivel_inicial_mmca < 0:
            raise ErroValidacaoEntrada("Pressão inicial deve ser um inteiro não-negativo em mm.c.a.", ERR_VALIDACAO_DOMINIO)
        if not self.no_origem_principal:
            raise ErroValidacaoEntrada("Nó de origem principal da rede deve ser informado.", ERR_VALIDACAO_DOMINIO)
        if not self.trechos:
            raise ErroValidacaoEntrada("A instalação deve conter pelo menos um trecho de tubulação.", ERR_VALIDACAO_DOMINIO)


@dataclass(frozen=True)
class TrechoDimensionado:
    """Resultado detalhado de cálculo e dimensionamento de um trecho da rede."""
    id_trecho: str
    no_origem: str
    no_destino: str
    soma_pesos_decimos: int
    vazao_projeto_mls: int
    dn_selecionado: int
    polegadas_ref: str
    diametro_interno_decimos_mm: int
    velocidade_mms: int
    comprimento_real_mm: int
    comprimento_equivalente_mm: int
    comprimento_total_mm: int
    perda_carga_unitaria_mmca_m: Fraction
    perda_carga_total_mmca: int
    desnivel_geometrico_mm: int
    pressao_estatica_montante_mmca: int
    pressao_estatica_jusante_mmca: int
    pressao_dinamica_montante_mmca: int
    pressao_dinamica_jusante_mmca: int
    velocidade_conforme: bool
    pressao_estatica_conforme: bool
    pressao_dinamica_conforme: bool


@dataclass(frozen=True)
class PontoConsumoVerificado:
    """Verificação individual de pressão e vazão em um ponto de utilização sanitário."""
    no: str
    codigo_aparelho: str
    nome_aparelho: str
    vazao_minima_mls: int
    pressao_minima_exigida_mmca: int
    pressao_dinamica_real_mmca: int
    conforme: bool


@dataclass(frozen=True)
class ResultadoDimensionamento:
    """Dossiê consolidado de dimensionamento da instalação hidráulica predial."""
    nome_edificacao: str
    descricao: str
    total_trechos: int
    total_aparelhos: int
    soma_pesos_global_decimos: int
    vazao_total_instalada_mls: int
    vazao_provavel_global_mls: int
    ponto_mais_desfavoravel_no: str
    pressao_ponto_mais_desfavoravel_mmca: int
    ponto_maior_pressao_estatica_no: str
    pressao_estatica_maxima_mmca: int
    trechos: List[TrechoDimensionado]
    pontos_consumo: List[PontoConsumoVerificado]
    todos_criterios_atendidos: bool


def formatar_milimetros_para_metros_br(milimetros: int) -> str:
    """Converte milímetros inteiros para metros formatados em pt-BR (ex: 3500 -> 3,50 m)."""
    sinal = "-" if milimetros < 0 else ""
    val_abs = abs(milimetros)
    m = val_abs // 1000
    resto = val_abs % 1000
    cm = resto // 10
    return f"{sinal}{m},{cm:02d} m"


def formatar_mmca_para_mca_br(mmca: int) -> str:
    """Converte mm.c.a. para m.c.a. formatado em pt-BR (ex: 1250 -> 1,25 m.c.a.)."""
    sinal = "-" if mmca < 0 else ""
    val_abs = abs(mmca)
    m = val_abs // 1000
    resto = val_abs % 1000
    cm = resto // 10
    return f"{sinal}{m},{cm:02d} m.c.a."


def formatar_vazao_ls_br(vazao_mls: int) -> str:
    """Converte vazão em mL/s para L/s formatado em pt-BR (ex: 150 -> 0,15 L/s)."""
    l = vazao_mls // 1000
    resto = abs(vazao_mls % 1000)
    ml = resto // 10
    return f"{l},{ml:02d} L/s"


def formatar_velocidade_ms_br(velocidade_mms: int) -> str:
    """Converte velocidade em mm/s para m/s formatado em pt-BR (ex: 1420 -> 1,42 m/s)."""
    m = velocidade_mms // 1000
    resto = abs(velocidade_mms % 1000)
    cm = resto // 10
    return f"{m},{cm:02d} m/s"
