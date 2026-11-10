"""Codecs e serializadores canônicos determinísticos para dimensionamento hidráulico NBR 5626.

LOFRANO TECNOLOGIA.
Rejeita estritamente BOM, floats, chaves duplicadas e profundidade excessiva.
"""

from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from .domain import (
    ConexaoTrecho,
    InstalacaoPredialInput,
    PontoConsumo,
    ResultadoDimensionamento,
    TrechoInput,
    formatar_milimetros_para_metros_br,
    formatar_mmca_para_mca_br,
    formatar_vazao_ls_br,
    formatar_velocidade_ms_br,
)
from .errors import (
    ErroCodec,
    ERR_BOM_DETECTADO,
    ERR_CHAVE_DUPLICADA,
    ERR_FLOAT_PROIBIDO,
    ERR_PROFUNDIDADE_EXCEDIDA,
    ERR_VALIDACAO_DOMINIO,
)

LIMITE_PROFUNDIDADE_MAXIMA = 32


def _verificar_profundidade(obj: Any, nivel: int = 0) -> None:
    if nivel > LIMITE_PROFUNDIDADE_MAXIMA:
        raise ErroCodec(
            f"Profundidade de aninhamento excedeu o limite máximo de {LIMITE_PROFUNDIDADE_MAXIMA}.",
            ERR_PROFUNDIDADE_EXCEDIDA,
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, nivel + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel + 1)


def _verificar_sem_float(obj: Any) -> None:
    if isinstance(obj, float):
        raise ErroCodec("Números em ponto flutuante (float) são terminantemente proibidos.", ERR_FLOAT_PROIBIDO)
    if isinstance(obj, dict):
        for k, v in obj.items():
            _verificar_sem_float(k)
            _verificar_sem_float(v)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_sem_float(item)


def decodificar_json_canonico(conteudo: Union[str, bytes]) -> Any:
    """Decodifica JSON rejeitando BOM, floats, chaves duplicadas e profundidade excessiva."""
    if isinstance(conteudo, bytes):
        if conteudo.startswith(b"\xef\xbb\xbf"):
            raise ErroCodec("Byte Order Mark (BOM) UTF-8 detectado e proibido.", ERR_BOM_DETECTADO)
        texto = conteudo.decode("utf-8")
    else:
        if conteudo.startswith("\ufeff"):
            raise ErroCodec("Byte Order Mark (BOM) UTF-8 detectado e proibido.", ERR_BOM_DETECTADO)
        texto = conteudo

    def pares_sem_duplicatas(pares: List[Tuple[str, Any]]) -> Dict[str, Any]:
        dicionario: Dict[str, Any] = {}
        for chave, valor in pares:
            if chave in dicionario:
                raise ErroCodec(f"Chave duplicada detectada no JSON: '{chave}'.", ERR_CHAVE_DUPLICADA)
            dicionario[chave] = valor
        return dicionario

    def rejeitar_float(token: str) -> None:
        raise ErroCodec(
            f"Número em ponto flutuante (float) detectado no JSON: '{token}'. "
            "Use apenas inteiros (milímetros, décimos de peso, mL/s, mm.c.a.).",
            ERR_FLOAT_PROIBIDO,
        )

    try:
        obj = json.loads(
            texto,
            object_pairs_hook=pares_sem_duplicatas,
            parse_float=rejeitar_float,
        )
    except json.JSONDecodeError as e:
        raise ErroCodec(f"Falha de sintaxe no JSON: {e}", "ERR_JSON_SINTAXE")

    _verificar_profundidade(obj)
    _verificar_sem_float(obj)
    return obj


def serializar_json_canonico(dados: Any) -> str:
    """Serializa estruturas de dados em JSON canônico estrito e determinístico."""
    _verificar_profundidade(dados)
    _verificar_sem_float(dados)

    return json.dumps(
        dados,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def carregar_projeto(caminho: Union[str, Path]) -> InstalacaoPredialInput:
    """Lê arquivo JSON e instancia o projeto de instalação hidráulica predial."""
    p = Path(caminho)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo de projeto não encontrado: '{p}'")

    dados = decodificar_json_canonico(p.read_bytes())
    if not isinstance(dados, dict):
        raise ErroCodec("O arquivo de projeto deve conter um objeto JSON na raiz.", ERR_VALIDACAO_DOMINIO)

    campos_obrigatorios = [
        "nome_edificacao",
        "descricao",
        "pressao_disponivel_inicial_mmca",
        "no_origem_principal",
        "trechos",
    ]
    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ErroCodec(f"Campo obrigatório ausente no JSON: '{campo}'.", ERR_VALIDACAO_DOMINIO)

    lista_trechos: List[TrechoInput] = []
    for idx, t_raw in enumerate(dados["trechos"]):
        if not isinstance(t_raw, dict):
            raise ErroCodec(f"Trecho #{idx} deve ser um objeto JSON.", ERR_VALIDACAO_DOMINIO)

        conexoes: List[ConexaoTrecho] = []
        for c_raw in t_raw.get("conexoes", []):
            conexoes.append(ConexaoTrecho(
                tipo=c_raw["tipo"],
                quantidade=c_raw["quantidade"],
            ))

        aparelhos: List[PontoConsumo] = []
        for a_raw in t_raw.get("aparelhos_diretos", []):
            aparelhos.append(PontoConsumo(
                codigo_aparelho=a_raw["codigo_aparelho"],
                descricao=a_raw.get("descricao", ""),
                quantidade=a_raw.get("quantidade", 1),
            ))

        lista_trechos.append(TrechoInput(
            id_trecho=t_raw["id_trecho"],
            no_origem=t_raw["no_origem"],
            no_destino=t_raw["no_destino"],
            comprimento_real_mm=t_raw["comprimento_real_mm"],
            desnivel_geometrico_mm=t_raw["desnivel_geometrico_mm"],
            conexoes=conexoes,
            aparelhos_diretos=aparelhos,
            dn_fixado=t_raw.get("dn_fixado"),
        ))

    return InstalacaoPredialInput(
        nome_edificacao=dados["nome_edificacao"],
        descricao=dados["descricao"],
        pressao_disponivel_inicial_mmca=dados["pressao_disponivel_inicial_mmca"],
        no_origem_principal=dados["no_origem_principal"],
        trechos=lista_trechos,
        criterio_velocidade_maxima_mms=dados.get("criterio_velocidade_maxima_mms", 3000),
        criterio_pressao_estatica_max_mmca=dados.get("criterio_pressao_estatica_max_mmca", 40000),
        criterio_pressao_dinamica_min_mmca=dados.get("criterio_pressao_dinamica_min_mmca", 1000),
    )


def resultado_para_dict(resultado: ResultadoDimensionamento) -> Dict[str, Any]:
    """Converte o resultado do dimensionamento para dicionário canônico determinístico."""
    trechos_json = []
    for t in resultado.trechos:
        j_num = t.perda_carga_unitaria_mmca_m.numerator
        j_den = t.perda_carga_unitaria_mmca_m.denominator
        trechos_json.append({
            "id_trecho": t.id_trecho,
            "no_origem": t.no_origem,
            "no_destino": t.no_destino,
            "soma_pesos_decimos": t.soma_pesos_decimos,
            "vazao_projeto_mls": t.vazao_projeto_mls,
            "vazao_projeto_formatada": formatar_vazao_ls_br(t.vazao_projeto_mls),
            "dn_selecionado": t.dn_selecionado,
            "polegadas_ref": t.polegadas_ref,
            "diametro_interno_decimos_mm": t.diametro_interno_decimos_mm,
            "velocidade_mms": t.velocidade_mms,
            "velocidade_formatada": formatar_velocidade_ms_br(t.velocidade_mms),
            "comprimento_real_mm": t.comprimento_real_mm,
            "comprimento_real_formatado": formatar_milimetros_para_metros_br(t.comprimento_real_mm),
            "comprimento_equivalente_mm": t.comprimento_equivalente_mm,
            "comprimento_equivalente_formatado": formatar_milimetros_para_metros_br(t.comprimento_equivalente_mm),
            "comprimento_total_mm": t.comprimento_total_mm,
            "comprimento_total_formatado": formatar_milimetros_para_metros_br(t.comprimento_total_mm),
            "perda_carga_unitaria_numerador": j_num,
            "perda_carga_unitaria_denominador": j_den,
            "perda_carga_total_mmca": t.perda_carga_total_mmca,
            "perda_carga_total_formatada": formatar_mmca_para_mca_br(t.perda_carga_total_mmca),
            "desnivel_geometrico_mm": t.desnivel_geometrico_mm,
            "desnivel_geometrico_formatado": formatar_milimetros_para_metros_br(t.desnivel_geometrico_mm),
            "pressao_estatica_jusante_mmca": t.pressao_estatica_jusante_mmca,
            "pressao_estatica_jusante_formatada": formatar_mmca_para_mca_br(t.pressao_estatica_jusante_mmca),
            "pressao_dinamica_jusante_mmca": t.pressao_dinamica_jusante_mmca,
            "pressao_dinamica_jusante_formatada": formatar_mmca_para_mca_br(t.pressao_dinamica_jusante_mmca),
            "velocidade_conforme": t.velocidade_conforme,
            "pressao_estatica_conforme": t.pressao_estatica_conforme,
            "pressao_dinamica_conforme": t.pressao_dinamica_conforme,
        })

    pontos_json = []
    for pc in resultado.pontos_consumo:
        pontos_json.append({
            "no": pc.no,
            "codigo_aparelho": pc.codigo_aparelho,
            "nome_aparelho": pc.nome_aparelho,
            "vazao_minima_mls": pc.vazao_minima_mls,
            "vazao_minima_formatada": formatar_vazao_ls_br(pc.vazao_minima_mls),
            "pressao_minima_exigida_mmca": pc.pressao_minima_exigida_mmca,
            "pressao_minima_exigida_formatada": formatar_mmca_para_mca_br(pc.pressao_minima_exigida_mmca),
            "pressao_dinamica_real_mmca": pc.pressao_dinamica_real_mmca,
            "pressao_dinamica_real_formatada": formatar_mmca_para_mca_br(pc.pressao_dinamica_real_mmca),
            "conforme": pc.conforme,
        })

    return {
        "edificacao": {
            "nome": resultado.nome_edificacao,
            "descricao": resultado.descricao,
        },
        "resumo_engenharia": {
            "total_trechos": resultado.total_trechos,
            "total_aparelhos": resultado.total_aparelhos,
            "soma_pesos_global_decimos": resultado.soma_pesos_global_decimos,
            "vazao_total_instalada_mls": resultado.vazao_total_instalada_mls,
            "vazao_total_instalada_formatada": formatar_vazao_ls_br(resultado.vazao_total_instalada_mls),
            "vazao_provavel_global_mls": resultado.vazao_provavel_global_mls,
            "vazao_provavel_global_formatada": formatar_vazao_ls_br(resultado.vazao_provavel_global_mls),
            "ponto_mais_desfavoravel_no": resultado.ponto_mais_desfavoravel_no,
            "pressao_ponto_mais_desfavoravel_mmca": resultado.pressao_ponto_mais_desfavoravel_mmca,
            "pressao_ponto_mais_desfavoravel_formatada": formatar_mmca_para_mca_br(resultado.pressao_ponto_mais_desfavoravel_mmca),
            "ponto_maior_pressao_estatica_no": resultado.ponto_maior_pressao_estatica_no,
            "pressao_estatica_maxima_mmca": resultado.pressao_estatica_maxima_mmca,
            "pressao_estatica_maxima_formatada": formatar_mmca_para_mca_br(resultado.pressao_estatica_maxima_mmca),
            "todos_criterios_atendidos": resultado.todos_criterios_atendidos,
        },
        "trechos": trechos_json,
        "pontos_consumo": pontos_json,
    }
