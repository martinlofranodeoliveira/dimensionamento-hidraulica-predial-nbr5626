"""Módulo de tratamento de exceções e erros do dimensionamento hidráulico predial (NBR 5626).

LOFRANO TECNOLOGIA.
"""


class ErroHidraulicaPredial(Exception):
    """Exceção base para todas as falhas de dimensionamento hidráulico."""

    def __init__(self, mensagem: str, codigo: str = "ERR_GENERICO"):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensagem}"


class ErroValidacaoEntrada(ErroHidraulicaPredial):
    """Lançada quando a especificação da rede ou dos aparelhos possui inconsistências."""

    def __init__(self, mensagem: str, codigo: str = "ERR_VALIDACAO"):
        super().__init__(mensagem, codigo)


class ErroNormaNBR5626(ErroHidraulicaPredial):
    """Lançada quando critérios compulsórios da ABNT NBR 5626 são violados."""

    def __init__(self, mensagem: str, codigo: str = "ERR_NORMA_NBR5626"):
        super().__init__(mensagem, codigo)


class ErroVelocidadeExcessiva(ErroNormaNBR5626):
    """Lançada quando a velocidade do escoamento ultrapassa 3,0 m/s."""

    def __init__(self, mensagem: str, codigo: str = "ERR_VELOCIDADE_EXCESSIVA"):
        super().__init__(mensagem, codigo)


class ErroPressaoInsuficiente(ErroNormaNBR5626):
    """Lançada quando a pressão residual dinâmica é inferior ao mínimo normativo."""

    def __init__(self, mensagem: str, codigo: str = "ERR_PRESSAO_INSUFICIENTE"):
        super().__init__(mensagem, codigo)


class ErroPressaoExcessiva(ErroNormaNBR5626):
    """Lançada quando a pressão estática ultrapassa 400 kPa (40 m.c.a.)."""

    def __init__(self, mensagem: str, codigo: str = "ERR_PRESSAO_EXCESSIVA"):
        super().__init__(mensagem, codigo)


class ErroTopologiaRede(ErroHidraulicaPredial):
    """Lançada quando a rede contém ciclos, nós desconexos ou referências órfãs."""

    def __init__(self, mensagem: str, codigo: str = "ERR_TOPOLOGIA"):
        super().__init__(mensagem, codigo)


class ErroCodec(ErroHidraulicaPredial):
    """Lançada quando a decodificação ou codificação canônica JSON falha."""

    def __init__(self, mensagem: str, codigo: str = "ERR_CODEC"):
        super().__init__(mensagem, codigo)


class ErroExportacao(ErroHidraulicaPredial):
    """Lançada quando a geração de relatórios, SVG, CSV ou ZIP falha."""

    def __init__(self, mensagem: str, codigo: str = "ERR_EXPORTACAO"):
        super().__init__(mensagem, codigo)


# Constantes de códigos de erro
ERR_VALIDACAO_DOMINIO = "ERR_VALIDACAO_DOMINIO"
ERR_FLOAT_PROIBIDO = "ERR_FLOAT_PROIBIDO"
ERR_BOM_DETECTADO = "ERR_BOM_DETECTADO"
ERR_CHAVE_DUPLICADA = "ERR_CHAVE_DUPLICADA"
ERR_PROFUNDIDADE_EXCEDIDA = "ERR_PROFUNDIDADE_EXCEDIDA"
ERR_APARELHO_DESCONHECIDO = "ERR_APARELHO_DESCONHECIDO"
ERR_NO_NAO_ENCONTRADO = "ERR_NO_NAO_ENCONTRADO"
ERR_CICLO_DETECTADO = "ERR_CICLO_DETECTADO"
ERR_TOPOLOGIA = "ERR_TOPOLOGIA"
ERR_DIAMETRO_NAO_ENCONTRADO = "ERR_DIAMETRO_NAO_ENCONTRADO"
