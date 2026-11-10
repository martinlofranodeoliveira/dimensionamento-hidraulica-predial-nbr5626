"""Motor de cálculo e dimensionamento determinístico de rede hidráulica predial (NBR 5626).

LOFRANO TECNOLOGIA.
Todos os cálculos operam exclusivamente em aritmética inteira e frações racionais (Zero Float).
"""

from collections import defaultdict
from fractions import Fraction
import math
from typing import Dict, List, Set, Tuple

from .domain import (
    InstalacaoPredialInput,
    PontoConsumoVerificado,
    ResultadoDimensionamento,
    TrechoDimensionado,
    TrechoInput,
)
from .errors import (
    ErroTopologiaRede,
    ErroValidacaoEntrada,
    ERR_CICLO_DETECTADO,
    ERR_NO_NAO_ENCONTRADO,
    ERR_TOPOLOGIA,
)
from .tabelas_nbr5626 import (
    APARELHOS_SANITARIOS,
    DIAMETROS_PVC,
    MAPA_DIAMETROS_PVC,
    calcular_perda_carga_unitaria_racional,
    obter_comprimento_equivalente_conexao,
)

# Aproximação racional de Pi: 355 / 113 (erro < 2.7e-7)
PI_NUMERADOR = 355
PI_DENOMINADOR = 113


def calcular_vazao_provavel_mls(soma_pesos_decimos: int) -> int:
    """Calcula a vazão provável Q = 0,30 * sqrt(soma_pesos) em mL/s por raiz inteira exata."""
    if soma_pesos_decimos <= 0:
        return 0

    # soma_pesos_decimos = 10 * soma_pesos
    # Q (L/s) = 0,30 * sqrt(soma_pesos_decimos / 10)
    # Q (mL/s) = 300 * sqrt(soma_pesos_decimos * 10) / 10 = 30 * sqrt(soma_pesos_decimos * 10)
    # Para precisão inteira com 3 casas antes da divisão:
    # raiz = isqrt(soma_pesos_decimos * 10 * 1_000_000)
    # Q_mls = (30 * raiz + 500) // 1000
    raiz = math.isqrt(soma_pesos_decimos * 10 * 1_000_000)
    q_mls = (30 * raiz + 500) // 1000
    return max(q_mls, 1)


def calcular_velocidade_mms(vazao_mls: int, diametro_interno_decimos_mm: int) -> int:
    """Calcula a velocidade média v = 4*Q / (pi*D^2) em mm/s usando aritmética inteira exata."""
    if vazao_mls <= 0 or diametro_interno_decimos_mm <= 0:
        return 0

    # Q (mm^3/s) = vazao_mls * 1000
    # D (mm) = diametro_interno_decimos_mm / 10 => D^2 = diametro_interno_decimos_mm^2 / 100
    # Area (mm^2) = (PI_NUMERADOR / PI_DENOMINADOR) * (D_dec^2 / 400)
    #             = (PI_NUMERADOR * D_dec^2) / (400 * PI_DENOMINADOR)
    # v (mm/s) = Q / Area = (vazao_mls * 1000 * 400 * PI_DENOMINADOR) / (PI_NUMERADOR * D_dec^2)
    #          = (vazao_mls * 400_000 * 113) / (355 * D_dec^2)
    #          = (vazao_mls * 45_200_000) / (355 * D_dec^2)
    numerador = vazao_mls * 45_200_000
    denominador = 355 * (diametro_interno_decimos_mm ** 2)
    velocidade = (numerador + denominador // 2) // denominador
    return velocidade


def selecionar_menor_dn_admissivel(
    vazao_mls: int,
    velocidade_maxima_mms: int,
    dn_fixado: int | None = None,
    possui_valvula_descarga: bool = False,
) -> Tuple[int, int, int]:
    """Seleciona o menor DN comercial de PVC que atende a velocidade máxima admissível.

    Retorna: (dn, diametro_interno_decimos_mm, velocidade_mms).
    """
    if dn_fixado is not None:
        pvc = MAPA_DIAMETROS_PVC[dn_fixado]
        vel = calcular_velocidade_mms(vazao_mls, pvc.diametro_interno_decimos_mm)
        return (pvc.dn, pvc.diametro_interno_decimos_mm, vel)

    for pvc in DIAMETROS_PVC:
        # Se for sub-ramal de válvula de descarga, DN mínimo normativo é 40 mm (1.1/4" ou 1.1/2")
        if possui_valvula_descarga and pvc.dn < 40:
            continue

        vel = calcular_velocidade_mms(vazao_mls, pvc.diametro_interno_decimos_mm)
        if vel <= velocidade_maxima_mms:
            return (pvc.dn, pvc.diametro_interno_decimos_mm, vel)

    # Caso a vazão seja muito alta para a linha padrão, retorna o maior diâmetro disponível
    pvc_max = DIAMETROS_PVC[-1]
    vel_max = calcular_velocidade_mms(vazao_mls, pvc_max.diametro_interno_decimos_mm)
    return (pvc_max.dn, pvc_max.diametro_interno_decimos_mm, vel_max)


def ordenar_topologicamente(
    trechos: List[TrechoInput],
    no_raiz: str,
) -> List[TrechoInput]:
    """Ordena os trechos da rede da montante para a jusante, detectando ciclos e desconexões."""
    adjacencias: Dict[str, List[TrechoInput]] = defaultdict(list)
    grau_entrada: Dict[str, int] = defaultdict(int)
    todos_nos: Set[str] = set()

    for t in trechos:
        adjacencias[t.no_origem].append(t)
        grau_entrada[t.no_destino] += 1
        todos_nos.add(t.no_origem)
        todos_nos.add(t.no_destino)

    if no_raiz not in todos_nos:
        raise ErroTopologiaRede(f"Nó raiz '{no_raiz}' não existe na rede.", ERR_NO_NAO_ENCONTRADO)

    # 1. Detecção rigorosa de ciclos direcionados via DFS com 3 estados
    estado_dfs: Dict[str, int] = defaultdict(int)

    def detectar_ciclo_dfs(u: str) -> bool:
        estado_dfs[u] = 1
        for t in adjacencias.get(u, []):
            v = t.no_destino
            if estado_dfs[v] == 1:
                return True
            if estado_dfs[v] == 0:
                if detectar_ciclo_dfs(v):
                    return True
        estado_dfs[u] = 2
        return False

    for n in sorted(todos_nos):
        if estado_dfs[n] == 0:
            if detectar_ciclo_dfs(n):
                raise ErroTopologiaRede("Ciclo direcionado detectado na rede hidráulica.", ERR_CICLO_DETECTADO)

    # 2. Ordenação topológica por BFS a partir do nó raiz
    fila: List[str] = [no_raiz]
    visitados_nos: Set[str] = {no_raiz}
    trechos_ordenados: List[TrechoInput] = []
    visitados_trechos: Set[str] = set()

    while fila:
        atual = fila.pop(0)
        for t in adjacencias[atual]:
            if t.id_trecho in visitados_trechos:
                continue
            visitados_trechos.add(t.id_trecho)
            trechos_ordenados.append(t)
            dest = t.no_destino
            if dest not in visitados_nos:
                visitados_nos.add(dest)
                fila.append(dest)

    if len(trechos_ordenados) != len(trechos):
        # Houve ciclo ou trechos isolados desconexos do reservatório
        nao_visitados = [t.id_trecho for t in trechos if t.id_trecho not in visitados_trechos]
        raise ErroTopologiaRede(
            f"Rede hidráulica contém ciclos ou trechos desconexos da raiz: {nao_visitados}",
            ERR_CICLO_DETECTADO,
        )

    return trechos_ordenados


def mapear_aparelhos_jusante(
    trechos_ordenados: List[TrechoInput],
) -> Dict[str, List[Tuple[str, int, int, int]]]:
    """Mapeia os aparelhos sanitários alimentados a jusante de cada trecho.

    Retorna: {id_trecho: [(codigo_aparelho, peso_decimos, vazao_min_mls, pressao_min_mmca)]}
    """
    # Construir grafo reverso de dependências (jusante para montante)
    # Para cada trecho, os aparelhos a jusante são os seus próprios diretos + os dos trechos filhos
    adj_filhos: Dict[str, List[TrechoInput]] = defaultdict(list)
    for t in trechos_ordenados:
        adj_filhos[t.no_origem].append(t)

    # Processar na ordem reversa da ordenação topológica (folhas para raiz)
    aparelhos_jusante: Dict[str, List[Tuple[str, int, int, int]]] = {}

    for t in reversed(trechos_ordenados):
        lista: List[Tuple[str, int, int, int]] = []
        # Aparelhos diretos instalados no próprio trecho/destino
        for pc in t.aparelhos_diretos:
            ap_norm = APARELHOS_SANITARIOS[pc.codigo_aparelho]
            for _ in range(pc.quantidade):
                lista.append((
                    ap_norm.codigo,
                    ap_norm.peso_relativo_decimos,
                    ap_norm.vazao_minima_mls,
                    ap_norm.pressao_minima_mmca,
                ))

        # Adicionar aparelhos de trechos filhos alimentados a partir do nó destino
        for filho in adj_filhos.get(t.no_destino, []):
            lista.extend(aparelhos_jusante.get(filho.id_trecho, []))

        aparelhos_jusante[t.id_trecho] = lista

    return aparelhos_jusante


def dimensionar_rede_hidraulica(projeto: InstalacaoPredialInput) -> ResultadoDimensionamento:
    """Executa o dimensionamento completo determinístico da instalação predial de água."""
    trechos_ord = ordenar_topologicamente(projeto.trechos, projeto.no_origem_principal)
    aparelhos_por_trecho = mapear_aparelhos_jusante(trechos_ord)

    # Dicionário de pressões nos nós
    # {id_no: (pressao_estatica_mmca, pressao_dinamica_mmca)}
    pressoes_nos: Dict[str, Tuple[int, int]] = {
        projeto.no_origem_principal: (
            projeto.pressao_disponivel_inicial_mmca,
            projeto.pressao_disponivel_inicial_mmca,
        )
    }

    trechos_calculados: List[TrechoDimensionado] = []
    pontos_consumo_verificados: List[PontoConsumoVerificado] = []

    soma_pesos_global = 0
    vazao_total_instalada = 0

    ponto_mais_desfavoravel = projeto.no_origem_principal
    pressao_minima_observada = 999_999_999
    ponto_maior_estatica = projeto.no_origem_principal
    pressao_maxima_estatica = -999_999_999

    for t in trechos_ord:
        aparelhos = aparelhos_por_trecho[t.id_trecho]
        soma_pesos_trecho = sum(a[1] for a in aparelhos)
        soma_vazao_minima_instalada = sum(a[2] for a in aparelhos)
        possui_valvula = any(a[0] == "BACIA_VALVULA_DESCARGA" for a in aparelhos)

        if len(aparelhos) == 1:
            # Sub-ramal exclusivo para um único aparelho
            vazao_projeto = aparelhos[0][2]
        elif len(aparelhos) > 1:
            # Ramal ou coluna atendendo múltiplos aparelhos (método probabilístico NBR 5626)
            vazao_calc = calcular_vazao_provavel_mls(soma_pesos_trecho)
            # Garantir que a vazão de projeto não seja menor que a maior vazão de aparelho atendido
            maior_individual = max(a[2] for a in aparelhos)
            vazao_projeto = max(vazao_calc, maior_individual)
        else:
            # Trecho sem aparelhos (ex: reservatório até barrilete intermediário)
            vazao_projeto = 150  # Valor base mínimo de verificação

        # Seleção de diâmetro comercial
        dn, d_int, vel = selecionar_menor_dn_admissivel(
            vazao_mls=vazao_projeto,
            velocidade_maxima_mms=projeto.criterio_velocidade_maxima_mms,
            dn_fixado=t.dn_fixado,
            possui_valvula_descarga=possui_valvula,
        )
        pvc_info = MAPA_DIAMETROS_PVC[dn]

        # Comprimento equivalente das conexões no diâmetro selecionado
        leq_total_mm = 0
        for c in t.conexoes:
            leq_unitaria = obter_comprimento_equivalente_conexao(c.tipo, dn)
            leq_total_mm += leq_unitaria * c.quantidade

        comp_total_mm = t.comprimento_real_mm + leq_total_mm

        # Perda de carga unitária J e perda total do trecho
        j_frac = calcular_perda_carga_unitaria_racional(dn, vazao_projeto)
        # delta_h = J (mmca/m) * comp_total (mm) / 1000 mm/m
        # Divisão inteira com teto (arredondamento seguro em favor da segurança)
        num_perda = j_frac.numerator * comp_total_mm
        den_perda = j_frac.denominator * 1000
        perda_carga_total_mmca = (num_perda + den_perda - 1) // den_perda

        # Pressões de montante e jusante
        p_est_mont, p_din_mont = pressoes_nos[t.no_origem]
        p_est_jus = p_est_mont + t.desnivel_geometrico_mm
        p_din_jus = p_din_mont + t.desnivel_geometrico_mm - perda_carga_total_mmca
        pressoes_nos[t.no_destino] = (p_est_jus, p_din_jus)

        # Atualizar extremos observados
        if p_din_jus < pressao_minima_observada:
            pressao_minima_observada = p_din_jus
            ponto_mais_desfavoravel = t.no_destino

        if p_est_jus > pressao_maxima_estatica:
            pressao_maxima_estatica = p_est_jus
            ponto_maior_estatica = t.no_destino

        vel_ok = vel <= projeto.criterio_velocidade_maxima_mms
        est_ok = p_est_jus <= projeto.criterio_pressao_estatica_max_mmca
        din_ok = p_din_jus >= projeto.criterio_pressao_dinamica_min_mmca

        trecho_dim = TrechoDimensionado(
            id_trecho=t.id_trecho,
            no_origem=t.no_origem,
            no_destino=t.no_destino,
            soma_pesos_decimos=soma_pesos_trecho,
            vazao_projeto_mls=vazao_projeto,
            dn_selecionado=dn,
            polegadas_ref=pvc_info.polegadas_ref,
            diametro_interno_decimos_mm=d_int,
            velocidade_mms=vel,
            comprimento_real_mm=t.comprimento_real_mm,
            comprimento_equivalente_mm=leq_total_mm,
            comprimento_total_mm=comp_total_mm,
            perda_carga_unitaria_mmca_m=j_frac,
            perda_carga_total_mmca=perda_carga_total_mmca,
            desnivel_geometrico_mm=t.desnivel_geometrico_mm,
            pressao_estatica_montante_mmca=p_est_mont,
            pressao_estatica_jusante_mmca=p_est_jus,
            pressao_dinamica_montante_mmca=p_din_mont,
            pressao_dinamica_jusante_mmca=p_din_jus,
            velocidade_conforme=vel_ok,
            pressao_estatica_conforme=est_ok,
            pressao_dinamica_conforme=din_ok,
        )
        trechos_calculados.append(trecho_dim)

        # Verificação de pontos de consumo diretos neste nó de destino
        for pc in t.aparelhos_diretos:
            ap_norm = APARELHOS_SANITARIOS[pc.codigo_aparelho]
            p_din_local = p_din_jus
            conforme = p_din_local >= ap_norm.pressao_minima_mmca
            for _ in range(pc.quantidade):
                pontos_consumo_verificados.append(PontoConsumoVerificado(
                    no=t.no_destino,
                    codigo_aparelho=ap_norm.codigo,
                    nome_aparelho=ap_norm.nome,
                    vazao_minima_mls=ap_norm.vazao_minima_mls,
                    pressao_minima_exigida_mmca=ap_norm.pressao_minima_mmca,
                    pressao_dinamica_real_mmca=p_din_local,
                    conforme=conforme,
                ))

    # Consolidações globais
    aparelhos_raiz = aparelhos_por_trecho.get(trechos_ord[0].id_trecho, [])
    soma_pesos_global = sum(a[1] for a in aparelhos_raiz)
    vazao_total_instalada = sum(a[2] for a in aparelhos_raiz)
    vazao_provavel_global = calcular_vazao_provavel_mls(soma_pesos_global)

    todos_atendidos = (
        all(t.velocidade_conforme for t in trechos_calculados) and
        all(t.pressao_estatica_conforme for t in trechos_calculados) and
        all(pc.conforme for pc in pontos_consumo_verificados)
    )

    return ResultadoDimensionamento(
        nome_edificacao=projeto.nome_edificacao,
        descricao=projeto.descricao,
        total_trechos=len(trechos_calculados),
        total_aparelhos=len(pontos_consumo_verificados),
        soma_pesos_global_decimos=soma_pesos_global,
        vazao_total_instalada_mls=vazao_total_instalada,
        vazao_provavel_global_mls=vazao_provavel_global,
        ponto_mais_desfavoravel_no=ponto_mais_desfavoravel,
        pressao_ponto_mais_desfavoravel_mmca=pressao_minima_observada,
        ponto_maior_pressao_estatica_no=ponto_maior_estatica,
        pressao_estatica_maxima_mmca=pressao_maxima_estatica,
        trechos=trechos_calculados,
        pontos_consumo=pontos_consumo_verificados,
        todos_criterios_atendidos=todos_atendidos,
    )
