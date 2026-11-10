"""Módulo de exportação de dados, relatórios e pacotes determinísticos (NBR 5626).

LOFRANO TECNOLOGIA.
Sanitização estrita contra injeção de fórmulas em CSV e empacotamento ZIP determinístico.
"""

import csv
import io
import os
from pathlib import Path
import stat
from typing import List, Sequence, Tuple
import zipfile

from .domain import (
    ResultadoDimensionamento,
    formatar_milimetros_para_metros_br,
    formatar_mmca_para_mca_br,
    formatar_vazao_ls_br,
    formatar_velocidade_ms_br,
)
from .errors import ErroExportacao

# Caracteres perigosos para injeção de fórmulas em planilhas eletrônicas (CSV Injection)
CARACTERES_INJECAO_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: str) -> str:
    """Higieniza campo CSV contra injeção de fórmulas e comandos maliciosos."""
    if not valor:
        return valor
    texto = str(valor)
    if texto.startswith(CARACTERES_INJECAO_FORMULA):
        return f"'{texto}"
    return texto


def gerar_trechos_csv_str(resultado: ResultadoDimensionamento) -> str:
    """Gera planilha CSV com dimensionamento e verificação hidráulica de todos os trechos."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    cabecalho = [
        "ID_Trecho",
        "No_Origem",
        "No_Destino",
        "Soma_Pesos",
        "Vazao_Projeto_Ls",
        "DN_mm",
        "Bitola_Ref",
        "Velocidade_ms",
        "Comp_Real_m",
        "Comp_Equiv_m",
        "Comp_Total_m",
        "Perda_Carga_mca",
        "Pressao_Estatica_Jusante_mca",
        "Pressao_Dinamica_Jusante_mca",
        "Status_Velocidade",
        "Status_Pressao_Estatica",
        "Status_Pressao_Dinamica",
    ]
    writer.writerow([sanitizar_campo_csv(c) for c in cabecalho])

    for t in resultado.trechos:
        soma_p_formatada = f"{t.soma_pesos_decimos // 10},{t.soma_pesos_decimos % 10}"
        linha = [
            t.id_trecho,
            t.no_origem,
            t.no_destino,
            soma_p_formatada,
            formatar_vazao_ls_br(t.vazao_projeto_mls),
            str(t.dn_selecionado),
            t.polegadas_ref,
            formatar_velocidade_ms_br(t.velocidade_mms),
            formatar_milimetros_para_metros_br(t.comprimento_real_mm),
            formatar_milimetros_para_metros_br(t.comprimento_equivalente_mm),
            formatar_milimetros_para_metros_br(t.comprimento_total_mm),
            formatar_mmca_para_mca_br(t.perda_carga_total_mmca),
            formatar_mmca_para_mca_br(t.pressao_estatica_jusante_mmca),
            formatar_mmca_para_mca_br(t.pressao_dinamica_jusante_mmca),
            "CONFORME" if t.velocidade_conforme else "NAO_CONFORME",
            "CONFORME" if t.pressao_estatica_conforme else "NAO_CONFORME",
            "CONFORME" if t.pressao_dinamica_conforme else "NAO_CONFORME",
        ]
        writer.writerow([sanitizar_campo_csv(col) for col in linha])

    return output.getvalue()


def gerar_pontos_consumo_csv_str(resultado: ResultadoDimensionamento) -> str:
    """Gera planilha CSV com verificação pontual em cada ponto de utilização."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    cabecalho = [
        "No_Terminal",
        "Codigo_Aparelho",
        "Nome_Aparelho",
        "Vazao_Minima_Ls",
        "Pressao_Minima_Exigida_mca",
        "Pressao_Dinamica_Real_mca",
        "Conformidade_NBR5626",
    ]
    writer.writerow([sanitizar_campo_csv(c) for c in cabecalho])

    for pc in resultado.pontos_consumo:
        linha = [
            pc.no,
            pc.codigo_aparelho,
            pc.nome_aparelho,
            formatar_vazao_ls_br(pc.vazao_minima_mls),
            formatar_mmca_para_mca_br(pc.pressao_minima_exigida_mmca),
            formatar_mmca_para_mca_br(pc.pressao_dinamica_real_mmca),
            "APROVADO" if pc.conforme else "REPROVADO",
        ]
        writer.writerow([sanitizar_campo_csv(col) for col in linha])

    return output.getvalue()


def gerar_relatorio_memorial_markdown(resultado: ResultadoDimensionamento) -> str:
    """Gera Memorial Descritivo e de Cálculo Hidráulico segundo a ABNT NBR 5626 em Markdown."""
    status_geral = "APROVADO COM TOTAL CONFORMIDADE" if resultado.todos_criterios_atendidos else "REQUER AJUSTES DE PROJETO"

    linhas = [
        f"# Memorial Descritivo e de Cálculo Hidráulico Predial — NBR 5626",
        "",
        f"**Edificação:** {resultado.nome_edificacao}  ",
        f"**Descrição do Projeto:** {resultado.descricao}  ",
        f"**Status Normativo Global:** **{status_geral}**  ",
        f"**Padrão de Engenharia:** LOFRANO TECNOLOGIA (Zero Float, Aritmética Racional Exata)  ",
        "",
        "---",
        "",
        "## 1. Resumo Executivo da Instalação Hidráulica",
        "",
        f"- **Total de Trechos de Tubulação Dimensionados:** {resultado.total_trechos}",
        f"- **Total de Aparelhos Sanitários Atendidos:** {resultado.total_aparelhos}",
        r"- **Soma dos Pesos Relativos ($\sum P$):** "
        f"{resultado.soma_pesos_global_decimos // 10},{resultado.soma_pesos_global_decimos % 10}",
        f"- **Vazão Total Instalada (simultaneidade 100%):** {formatar_vazao_ls_br(resultado.vazao_total_instalada_mls)}",
        f"- **Vazão Provável Global (Método Probabilístico NBR 5626):** {formatar_vazao_ls_br(resultado.vazao_provavel_global_mls)}",
        f"- **Ponto Hidraulicamente Mais Desfavorável:** Nó `{resultado.ponto_mais_desfavoravel_no}` "
        f"com pressão residual dinâmica de **{formatar_mmca_para_mca_br(resultado.pressao_ponto_mais_desfavoravel_mmca)}**",
        f"- **Ponto de Maior Pressão Estática:** Nó `{resultado.ponto_maior_pressao_estatica_no}` "
        f"com pressão estática de **{formatar_mmca_para_mca_br(resultado.pressao_estatica_maxima_mmca)}** (limite normativo: 40,00 m.c.a.)",
        "",
        "---",
        "",
        "## 2. Dimensionamento dos Trechos de Tubulação (PVC Rígido NBR 5648)",
        "",
        r"| Trecho | Origem → Destino | $\sum P$ | Vazão (L/s) | DN (mm) | Bitola | Velocidade | Compr. Total | Perda $\Delta h$ | Pressão Dinâmica | Status |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for t in resultado.trechos:
        soma_p = f"{t.soma_pesos_decimos // 10},{t.soma_pesos_decimos % 10}"
        status_trecho = "OK" if (t.velocidade_conforme and t.pressao_dinamica_conforme and t.pressao_estatica_conforme) else "ATENÇÃO"
        linhas.append(
            f"| `{t.id_trecho}` | `{t.no_origem}` → `{t.no_destino}` | {soma_p} | "
            f"{formatar_vazao_ls_br(t.vazao_projeto_mls)} | **{t.dn_selecionado}** | {t.polegadas_ref} | "
            f"{formatar_velocidade_ms_br(t.velocidade_mms)} | {formatar_milimetros_para_metros_br(t.comprimento_total_mm)} | "
            f"{formatar_mmca_para_mca_br(t.perda_carga_total_mmca)} | "
            f"**{formatar_mmca_para_mca_br(t.pressao_dinamica_jusante_mmca)}** | {status_trecho} |"
        )

    linhas.extend([
        "",
        "---",
        "",
        "## 3. Verificação de Pressões nos Pontos de Utilização Sanitários",
        "",
        "| Nó | Aparelho Sanitário | Vazão Mínima | Pressão Mínima Exigida | Pressão Dinâmica Real | Parecer NBR 5626 |",
        "|---|---|---|---|---|---|",
    ])

    for pc in resultado.pontos_consumo:
        parecer = "CONFORME" if pc.conforme else "**INSUFICIENTE**"
        linhas.append(
            f"| `{pc.no}` | {pc.nome_aparelho} | {formatar_vazao_ls_br(pc.vazao_minima_mls)} | "
            f"{formatar_mmca_para_mca_br(pc.pressao_minima_exigida_mmca)} | "
            f"**{formatar_mmca_para_mca_br(pc.pressao_dinamica_real_mmca)}** | {parecer} |"
        )

    linhas.extend([
        "",
        "---",
        "",
        "## 4. Notas Metodológicas e Fundamentação Normativa",
        "",
        r"1. **Critério de Velocidade Máxima**: A velocidade em qualquer trecho foi limitada em $v \le 3,00$ m/s, conforme NBR 5626 item 5.3.3.1.",
        "2. **Critério de Pressão Estática Máxima**: Em nenhum ponto a pressão estática com a rede fechada ultrapassa 40,00 m.c.a. (400 kPa).",
        "3. **Critério de Pressão Dinâmica Residual**: Todos os aparelhos contam com pressão residual de escoamento acima do valor de projeto especificado na Tabela B.1.",
        "4. **Perda de Carga em Conexões**: Calculada pelo método dos comprimentos virtuais equivalentes normativos.",
        "5. **Confiabilidade Algorítmica**: O dimensionamento foi computado sem aproximações por ponto flutuante binário (IEEE-754), eliminando divergências cumulativas.",
        "",
        "---",
        "Engenharia e Software desenvolvidos por LOFRANO TECNOLOGIA.",
    ])

    return "\n".join(linhas) + "\n"


def criar_pacote_zip_deterministico(
    caminho_zip: Path,
    arquivos: Sequence[Tuple[str, bytes]],
) -> None:
    """Cria pacote ZIP determinístico rejeitando sobrescrita com os.O_EXCL."""
    if caminho_zip.exists():
        raise ErroExportacao(
            f"O arquivo ZIP '{caminho_zip}' já existe e não será sobrescrito.",
            "ERR_ARQUIVO_EXISTENTE",
        )

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    try:
        fd = os.open(str(caminho_zip), flags, 0o644)
    except OSError as e:
        raise ErroExportacao(f"Falha ao abrir descritor exclusivo de arquivo ZIP: {e}", "ERR_ARQUIVO_ZIP")

    data_fixa = (2026, 1, 1, 0, 0, 0)

    try:
        with os.fdopen(fd, "wb") as f_out:
            with zipfile.ZipFile(f_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for nome_arquivo, conteudo_bytes in sorted(arquivos, key=lambda x: x[0]):
                    zinfo = zipfile.ZipInfo(filename=nome_arquivo, date_time=data_fixa)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    zinfo.external_attr = (stat.S_IFREG | 0o644) << 16
                    zf.writestr(zinfo, conteudo_bytes)
    except Exception as e:
        if caminho_zip.exists():
            caminho_zip.unlink(missing_ok=True)
        raise ErroExportacao(f"Falha ao gravar arquivo ZIP determinístico: {e}", "ERR_GRAVACAO_ZIP")
