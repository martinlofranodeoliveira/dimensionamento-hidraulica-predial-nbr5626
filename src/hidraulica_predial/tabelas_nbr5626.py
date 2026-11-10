"""Tabelas normativas da ABNT NBR 5626:2020 e NBR 5648 para instalações prediais de água.

LOFRANO TECNOLOGIA.
Todos os valores são armazenados como inteiros (centímetros, milímetros, mililitros/s, mm.c.a.).
"""

from fractions import Fraction
from typing import Dict, List, NamedTuple


class AparelhoNormativo(NamedTuple):
    """Propriedades normativas de um aparelho sanitário (Tabela B.1 NBR 5626)."""
    codigo: str
    nome: str
    peso_relativo_decimos: int      # 1 unidade de peso = 10 décimos (ex: 0,3 = 3 décimos)
    vazao_minima_mls: int           # Vazão mínima de projeto em mL/s (ex: 0,15 L/s = 150 mL/s)
    pressao_minima_mmca: int        # Pressão dinâmica mínima exigida em mm.c.a. (10 kPa = 1000 mm.c.a.)


class DiametroComercialPVC(NamedTuple):
    """Dimensões nominais e reais de tubulações de PVC rígido soldável (NBR 5648)."""
    dn: int                         # Diâmetro nominal (mm)
    polegadas_ref: str              # Bitola comercial em polegadas
    diametro_externo_mm: int        # Diâmetro externo nominal em mm
    diametro_interno_decimos_mm: int  # Diâmetro interno real em décimos de mm (17,0 mm = 170 décimos)


# Aparelhos sanitários usuais e especificações da NBR 5626:2020 (Tabela B.1)
APARELHOS_SANITARIOS: Dict[str, AparelhoNormativo] = {
    "BACIA_CAIXA_ACOPLADA": AparelhoNormativo(
        codigo="BACIA_CAIXA_ACOPLADA",
        nome="Bacia sanitária com caixa acoplada",
        peso_relativo_decimos=3,
        vazao_minima_mls=150,
        pressao_minima_mmca=1000,
    ),
    "BACIA_VALVULA_DESCARGA": AparelhoNormativo(
        codigo="BACIA_VALVULA_DESCARGA",
        nome="Bacia sanitária com válvula de descarga",
        peso_relativo_decimos=320,
        vazao_minima_mls=1700,
        pressao_minima_mmca=1500,
    ),
    "BANHEIRA": AparelhoNormativo(
        codigo="BANHEIRA",
        nome="Banheira de hidromassagem / imersão",
        peso_relativo_decimos=10,
        vazao_minima_mls=300,
        pressao_minima_mmca=1000,
    ),
    "CHUVEIRO_ELETRICO": AparelhoNormativo(
        codigo="CHUVEIRO_ELETRICO",
        nome="Chuveiro ou ducha elétrica",
        peso_relativo_decimos=4,
        vazao_minima_mls=200,
        pressao_minima_mmca=1000,
    ),
    "CHUVEIRO_MISTURADOR": AparelhoNormativo(
        codigo="CHUVEIRO_MISTURADOR",
        nome="Ducha de alta vazão ou misturador",
        peso_relativo_decimos=5,
        vazao_minima_mls=250,
        pressao_minima_mmca=1000,
    ),
    "DUCHA_HIGIENICA": AparelhoNormativo(
        codigo="DUCHA_HIGIENICA",
        nome="Ducha higiênica com registro",
        peso_relativo_decimos=4,
        vazao_minima_mls=100,
        pressao_minima_mmca=1000,
    ),
    "LAVATORIO": AparelhoNormativo(
        codigo="LAVATORIO",
        nome="Lavatório residencial ou comercial",
        peso_relativo_decimos=3,
        vazao_minima_mls=150,
        pressao_minima_mmca=1000,
    ),
    "PIA_COZINHA": AparelhoNormativo(
        codigo="PIA_COZINHA",
        nome="Pia de cozinha ou copa",
        peso_relativo_decimos=7,
        vazao_minima_mls=250,
        pressao_minima_mmca=1000,
    ),
    "MAQUINA_LAVAR_LOUCA": AparelhoNormativo(
        codigo="MAQUINA_LAVAR_LOUCA",
        nome="Máquina de lavar louças",
        peso_relativo_decimos=10,
        vazao_minima_mls=300,
        pressao_minima_mmca=1000,
    ),
    "MAQUINA_LAVAR_ROUPA": AparelhoNormativo(
        codigo="MAQUINA_LAVAR_ROUPA",
        nome="Máquina de lavar roupas",
        peso_relativo_decimos=10,
        vazao_minima_mls=300,
        pressao_minima_mmca=1000,
    ),
    "TANQUE_LAVAR_ROUPA": AparelhoNormativo(
        codigo="TANQUE_LAVAR_ROUPA",
        nome="Tanque de lavar roupas",
        peso_relativo_decimos=7,
        vazao_minima_mls=250,
        pressao_minima_mmca=1000,
    ),
    "TORNEIRA_JARDIM": AparelhoNormativo(
        codigo="TORNEIRA_JARDIM",
        nome="Torneira de jardim / tanque externo",
        peso_relativo_decimos=4,
        vazao_minima_mls=200,
        pressao_minima_mmca=1000,
    ),
    "BIDE": AparelhoNormativo(
        codigo="BIDE",
        nome="Bidê com ducha",
        peso_relativo_decimos=1,
        vazao_minima_mls=100,
        pressao_minima_mmca=1000,
    ),
    "MICTORIO_VALVULA": AparelhoNormativo(
        codigo="MICTORIO_VALVULA",
        nome="Mictório com válvula de descarga",
        peso_relativo_decimos=28,
        vazao_minima_mls=500,
        pressao_minima_mmca=1500,
    ),
    "MICTORIO_CAIXA": AparelhoNormativo(
        codigo="MICTORIO_CAIXA",
        nome="Mictório com caixa de descarga / sensor",
        peso_relativo_decimos=3,
        vazao_minima_mls=150,
        pressao_minima_mmca=1000,
    ),
}

# Diâmetros comerciais de tubos de PVC soldável (NBR 5648)
DIAMETROS_PVC: List[DiametroComercialPVC] = [
    DiametroComercialPVC(dn=20, polegadas_ref="1/2\"", diametro_externo_mm=20, diametro_interno_decimos_mm=170),
    DiametroComercialPVC(dn=25, polegadas_ref="3/4\"", diametro_externo_mm=25, diametro_interno_decimos_mm=216),
    DiametroComercialPVC(dn=32, polegadas_ref="1\"", diametro_externo_mm=32, diametro_interno_decimos_mm=278),
    DiametroComercialPVC(dn=40, polegadas_ref="1.1/4\"", diametro_externo_mm=40, diametro_interno_decimos_mm=352),
    DiametroComercialPVC(dn=50, polegadas_ref="1.1/2\"", diametro_externo_mm=50, diametro_interno_decimos_mm=440),
    DiametroComercialPVC(dn=60, polegadas_ref="2\"", diametro_externo_mm=60, diametro_interno_decimos_mm=534),
    DiametroComercialPVC(dn=75, polegadas_ref="2.1/2\"", diametro_externo_mm=75, diametro_interno_decimos_mm=666),
    DiametroComercialPVC(dn=85, polegadas_ref="3\"", diametro_externo_mm=85, diametro_interno_decimos_mm=756),
    DiametroComercialPVC(dn=110, polegadas_ref="4\"", diametro_externo_mm=110, diametro_interno_decimos_mm=978),
]

# Mapa por DN para busca direta O(1)
MAPA_DIAMETROS_PVC: Dict[int, DiametroComercialPVC] = {d.dn: d for d in DIAMETROS_PVC}

# Comprimentos equivalentes de conexões (NBR 5626) em milímetros inteiros
# Estrutura: {tipo_conexao: {dn: comprimento_equivalente_mm}}
COMPRIMENTOS_EQUIVALENTES_MM: Dict[str, Dict[int, int]] = {
    "JOELHO_90": {
        20: 1100, 25: 1200, 32: 1500, 40: 2000, 50: 3200, 60: 3400, 75: 3700, 85: 3900, 110: 4300
    },
    "JOELHO_45": {
        20: 400, 25: 500, 32: 700, 40: 1000, 50: 1300, 60: 1500, 75: 1700, 85: 1800, 110: 2100
    },
    "CURVA_90_LONGA": {
        20: 400, 25: 500, 32: 600, 40: 700, 50: 1000, 60: 1300, 75: 1400, 85: 1500, 110: 1900
    },
    "CURVA_45": {
        20: 200, 25: 300, 32: 400, 40: 500, 50: 600, 60: 700, 75: 800, 85: 900, 110: 1100
    },
    "TE_PASSAGEM_DIRETA": {
        20: 700, 25: 800, 32: 900, 40: 1500, 50: 2200, 60: 2300, 75: 2500, 85: 2600, 110: 3100
    },
    "TE_SAIDA_LATERAL": {
        20: 2300, 25: 2400, 32: 3100, 40: 4600, 50: 7300, 60: 7600, 75: 7800, 85: 8400, 110: 10000
    },
    "TE_SAIDA_BILATERAL": {
        20: 2300, 25: 2400, 32: 3100, 40: 4600, 50: 7300, 60: 7600, 75: 7800, 85: 8400, 110: 10000
    },
    "REGISTRO_GAVETA_ABERTO": {
        20: 100, 25: 200, 32: 300, 40: 400, 50: 700, 60: 800, 75: 900, 85: 900, 110: 1100
    },
    "REGISTRO_PRESSAO_ABERTO": {
        20: 5600, 25: 6800, 32: 8500, 40: 11400, 50: 16000, 60: 18000, 75: 22000, 85: 25000, 110: 32000
    },
    "VALVULA_RETENCAO": {
        20: 2400, 25: 2700, 32: 3800, 40: 4900, 50: 6800, 60: 8200, 75: 9300, 85: 10400, 110: 14000
    },
    "ENTRADA_NORMAL": {
        20: 400, 25: 500, 32: 600, 40: 800, 50: 1200, 60: 1400, 75: 1500, 85: 1600, 110: 2000
    },
    "SAIDA_CANALIZACAO": {
        20: 800, 25: 900, 32: 1300, 40: 1600, 50: 2400, 60: 2700, 75: 3200, 85: 3500, 110: 4500
    },
}

# Tabela canônica de Perda de Carga Unitária J (em mm.c.a. por metro de tubulação de PVC)
# Calculada para pontos discretos de vazão Q (mL/s) e interpolada racionalmente.
# Garante 100% de estabilidade determinística e ausência de divergências flutuantes.
GRADE_VAZAO_MLS: List[int] = [
    0, 50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 1000,
    1200, 1500, 1700, 2000, 2500, 3000, 4000, 5000, 7000, 10000
]

# Tabela de Perda de Carga J tabelada (em mm.c.a./m) para cada (DN, Vazão)
# Valores normativos consagrados (Fórmula de Fair-Whipple-Hsiao arredondados para inteiros de mm.c.a./m)
TABELA_J_MMCA_POR_M: Dict[int, Dict[int, int]] = {
    20: {
        0: 0, 50: 8, 100: 27, 150: 55, 200: 92, 250: 137, 300: 190, 400: 318, 500: 474,
        600: 657, 700: 865, 800: 1098, 1000: 1634, 1200: 2269, 1500: 3376, 1700: 4220,
        2000: 5630, 2500: 8320, 3000: 11450, 4000: 18900, 5000: 27800, 7000: 49500, 10000: 91000
    },
    25: {
        0: 0, 50: 3, 100: 9, 150: 18, 200: 30, 250: 45, 300: 62, 400: 104, 500: 155,
        600: 215, 700: 283, 800: 359, 1000: 535, 1200: 742, 1500: 1104, 1700: 1381,
        2000: 1842, 2500: 2722, 3000: 3746, 4000: 6184, 5000: 9095, 7000: 16196, 10000: 29774
    },
    32: {
        0: 0, 50: 1, 100: 3, 150: 5, 200: 9, 250: 13, 300: 18, 400: 30, 500: 44,
        600: 61, 700: 81, 800: 102, 1000: 153, 1200: 211, 1500: 315, 1700: 394,
        2000: 525, 2500: 776, 3000: 1068, 4000: 1763, 5000: 2593, 7000: 4618, 10000: 8489
    },
    40: {
        0: 0, 50: 0, 100: 1, 150: 2, 200: 3, 250: 4, 300: 6, 400: 10, 500: 15,
        600: 21, 700: 27, 800: 35, 1000: 52, 1200: 72, 1500: 107, 1700: 134,
        2000: 178, 2500: 263, 3000: 363, 4000: 599, 5000: 881, 7000: 1569, 10000: 2884
    },
    50: {
        0: 0, 50: 0, 100: 0, 150: 1, 200: 1, 250: 1, 300: 2, 400: 3, 500: 5,
        600: 7, 700: 9, 800: 11, 1000: 17, 1200: 23, 1500: 35, 1700: 44,
        2000: 58, 2500: 86, 3000: 119, 4000: 196, 5000: 288, 7000: 513, 10000: 943
    },
    60: {
        0: 0, 50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 1, 400: 1, 500: 2,
        600: 3, 700: 3, 800: 4, 1000: 7, 1200: 9, 1500: 14, 1700: 17,
        2000: 23, 2500: 34, 3000: 47, 4000: 77, 5000: 114, 7000: 202, 10000: 372
    },
    75: {
        0: 0, 50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0, 400: 0, 500: 1,
        600: 1, 700: 1, 800: 2, 1000: 2, 1200: 3, 1500: 5, 1700: 6,
        2000: 8, 2500: 12, 3000: 17, 4000: 28, 5000: 41, 7000: 73, 10000: 134
    },
    85: {
        0: 0, 50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0, 400: 0, 500: 0,
        600: 1, 700: 1, 800: 1, 1000: 1, 1200: 2, 1500: 3, 1700: 3,
        2000: 4, 2500: 6, 3000: 9, 4000: 14, 5000: 21, 7000: 37, 10000: 69
    },
    110: {
        0: 0, 50: 0, 100: 0, 150: 0, 200: 0, 250: 0, 300: 0, 400: 0, 500: 0,
        600: 0, 700: 0, 800: 0, 1000: 0, 1200: 1, 1500: 1, 1700: 1,
        2000: 1, 2500: 2, 3000: 3, 4000: 4, 5000: 6, 7000: 11, 10000: 21
    },
}


def obter_comprimento_equivalente_conexao(tipo_conexao: str, dn: int) -> int:
    """Retorna o comprimento equivalente normativo da conexão em milímetros."""
    tabela = COMPRIMENTOS_EQUIVALENTES_MM.get(tipo_conexao)
    if not tabela:
        return 0
    return tabela.get(dn, 0)


def calcular_perda_carga_unitaria_racional(dn: int, vazao_mls: int) -> Fraction:
    """Calcula a perda de carga unitária J (mm.c.a. / m) com interpolação linear racional exata."""
    if vazao_mls <= 0:
        return Fraction(0, 1)

    tabela_dn = TABELA_J_MMCA_POR_M.get(dn)
    if not tabela_dn:
        # Padrão seguro para DN desconhecido
        return Fraction(0, 1)

    if vazao_mls in tabela_dn:
        return Fraction(tabela_dn[vazao_mls], 1)

    # Encontrar intervalo de interpolação
    q_ant = GRADE_VAZAO_MLS[0]
    for q_post in GRADE_VAZAO_MLS[1:]:
        if q_ant <= vazao_mls <= q_post:
            j_ant = tabela_dn[q_ant]
            j_post = tabela_dn[q_post]
            delta_q = q_post - q_ant
            delta_j = j_post - j_ant
            # Interpolação racional: j = j_ant + delta_j * (vazao - q_ant) / delta_q
            frac_j = Fraction(j_ant, 1) + Fraction(delta_j * (vazao_mls - q_ant), delta_q)
            return frac_j
        q_ant = q_post

    # Se exceder o máximo da grade, extrapolação linear simples com base no último intervalo
    q_penult = GRADE_VAZAO_MLS[-2]
    q_ult = GRADE_VAZAO_MLS[-1]
    j_penult = tabela_dn[q_penult]
    j_ult = tabela_dn[q_ult]
    delta_q = q_ult - q_penult
    delta_j = j_ult - j_penult
    return Fraction(j_ult, 1) + Fraction(delta_j * (vazao_mls - q_ult), delta_q)
