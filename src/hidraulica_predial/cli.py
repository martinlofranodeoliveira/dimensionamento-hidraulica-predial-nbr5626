"""Interface de linha de comando (CLI) para dimensionamento hidráulico predial NBR 5626.

LOFRANO TECNOLOGIA.
"""

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from .calculator import dimensionar_rede_hidraulica
from .codecs import (
    carregar_projeto,
    resultado_para_dict,
    serializar_json_canonico,
)
from .domain import (
    formatar_milimetros_para_metros_br,
    formatar_mmca_para_mca_br,
    formatar_vazao_ls_br,
    formatar_velocidade_ms_br,
)
from .errors import ErroHidraulicaPredial
from .exports import (
    criar_pacote_zip_deterministico,
    gerar_pontos_consumo_csv_str,
    gerar_relatorio_memorial_markdown,
    gerar_trechos_csv_str,
)
from .svg_report import gerar_painel_svg
from .tabelas_nbr5626 import APARELHOS_SANITARIOS, DIAMETROS_PVC

VERSAO = "1.0.0"

EXEMPLO_CANONICO = {
    "nome_edificacao": "Residência Unifamiliar Padrão - Sobrado",
    "descricao": "Instalação predial de água fria atendendo banheiro social, cozinha e lavanderia.",
    "pressao_disponivel_inicial_mmca": 2000,
    "no_origem_principal": "RES",
    "criterio_velocidade_maxima_mms": 3000,
    "criterio_pressao_estatica_max_mmca": 40000,
    "criterio_pressao_dinamica_min_mmca": 1000,
    "trechos": [
        {
            "id_trecho": "T1",
            "no_origem": "RES",
            "no_destino": "BAR",
            "comprimento_real_mm": 2000,
            "desnivel_geometrico_mm": 1500,
            "dn_fixado": 32,
            "conexoes": [
                {"tipo": "SAIDA_CANALIZACAO", "quantidade": 1},
                {"tipo": "REGISTRO_GAVETA_ABERTO", "quantidade": 1}
            ],
            "aparelhos_diretos": []
        },
        {
            "id_trecho": "T2",
            "no_origem": "BAR",
            "no_destino": "COL1",
            "comprimento_real_mm": 4500,
            "desnivel_geometrico_mm": 1000,
            "dn_fixado": 25,
            "conexoes": [
                {"tipo": "TE_PASSAGEM_DIRETA", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 2}
            ],
            "aparelhos_diretos": []
        },
        {
            "id_trecho": "T3",
            "no_origem": "COL1",
            "no_destino": "BANH",
            "comprimento_real_mm": 2800,
            "desnivel_geometrico_mm": 2200,
            "conexoes": [
                {"tipo": "TE_SAIDA_LATERAL", "quantidade": 1},
                {"tipo": "REGISTRO_GAVETA_ABERTO", "quantidade": 1}
            ],
            "aparelhos_diretos": []
        },
        {
            "id_trecho": "T4",
            "no_origem": "BANH",
            "no_destino": "CHUV",
            "comprimento_real_mm": 1200,
            "desnivel_geometrico_mm": -600,
            "conexoes": [
                {"tipo": "TE_PASSAGEM_DIRETA", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 2},
                {"tipo": "REGISTRO_PRESSAO_ABERTO", "quantidade": 1}
            ],
            "aparelhos_diretos": [
                {"codigo_aparelho": "CHUVEIRO_ELETRICO", "descricao": "Chuveiro do banheiro social", "quantidade": 1}
            ]
        },
        {
            "id_trecho": "T5",
            "no_origem": "BANH",
            "no_destino": "LAV",
            "comprimento_real_mm": 1500,
            "desnivel_geometrico_mm": 1200,
            "conexoes": [
                {"tipo": "TE_PASSAGEM_DIRETA", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 2}
            ],
            "aparelhos_diretos": [
                {"codigo_aparelho": "LAVATORIO", "descricao": "Lavatório do banheiro", "quantidade": 1}
            ]
        },
        {
            "id_trecho": "T6",
            "no_origem": "BANH",
            "no_destino": "BACIA",
            "comprimento_real_mm": 2200,
            "desnivel_geometrico_mm": 1800,
            "conexoes": [
                {"tipo": "TE_SAIDA_LATERAL", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 2}
            ],
            "aparelhos_diretos": [
                {"codigo_aparelho": "BACIA_CAIXA_ACOPLADA", "descricao": "Bacia sanitária c/ caixa", "quantidade": 1}
            ]
        },
        {
            "id_trecho": "T7",
            "no_origem": "BAR",
            "no_destino": "COZ",
            "comprimento_real_mm": 6000,
            "desnivel_geometrico_mm": 4500,
            "dn_fixado": 25,
            "conexoes": [
                {"tipo": "TE_SAIDA_LATERAL", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 3},
                {"tipo": "REGISTRO_GAVETA_ABERTO", "quantidade": 1}
            ],
            "aparelhos_diretos": [
                {"codigo_aparelho": "PIA_COZINHA", "descricao": "Pia da cozinha", "quantidade": 1}
            ]
        },
        {
            "id_trecho": "T8",
            "no_origem": "COZ",
            "no_destino": "LAVAND",
            "comprimento_real_mm": 3500,
            "desnivel_geometrico_mm": 0,
            "conexoes": [
                {"tipo": "TE_PASSAGEM_DIRETA", "quantidade": 1},
                {"tipo": "JOELHO_90", "quantidade": 2}
            ],
            "aparelhos_diretos": [
                {"codigo_aparelho": "TANQUE_LAVAR_ROUPA", "descricao": "Tanque de lavar roupas", "quantidade": 1},
                {"codigo_aparelho": "MAQUINA_LAVAR_ROUPA", "descricao": "Máquina de lavar roupas", "quantidade": 1}
            ]
        }
    ]
}


def criar_parser() -> argparse.ArgumentParser:
    """Cria analisador de linha de comando."""
    parser = argparse.ArgumentParser(
        prog="hidraulica-nbr5626",
        description="Dimensionamento determinístico de rede predial de água fria/quente (ABNT NBR 5626) — LOFRANO TECNOLOGIA",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"dimensionamento-hidraulica-predial-nbr5626 {VERSAO}",
    )

    subparsers = parser.add_subparsers(dest="subcomando", help="Subcomandos disponíveis")

    # Subcomando 'dimensionar'
    p_dim = subparsers.add_parser("dimensionar", help="Calcula e dimensiona a rede hidráulica predial a partir de arquivo JSON")
    p_dim.add_argument("arquivo", help="Caminho do arquivo JSON de especificação da rede")
    p_dim.add_argument("--saida", "-s", help="Diretório para salvar relatórios (JSON, CSVs, Memorial MD, SVG)")
    p_dim.add_argument("--zip", "-z", help="Caminho para gerar pacote ZIP determinístico consolidado")

    # Subcomando 'exemplo'
    p_exemplo = subparsers.add_parser("exemplo", help="Emite modelo JSON canônico de projeto hidráulico predial")
    p_exemplo.add_argument("--saida", "-o", help="Caminho do arquivo de saída (padrão: stdout)")

    # Subcomando 'tabelas'
    subparsers.add_parser("tabelas", help="Exibe aparelhos e tubulações normativas da NBR 5626")

    # Subcomando 'versao'
    subparsers.add_parser("versao", help="Exibe a versão do sistema")

    return parser


def comando_dimensionar(args: argparse.Namespace) -> int:
    """Executa o comando de dimensionamento da rede hidráulica."""
    caminho = Path(args.arquivo)
    if not caminho.exists():
        print(f"Erro: Arquivo não encontrado: '{caminho}'", file=sys.stderr)
        return 1

    try:
        projeto = carregar_projeto(caminho)
        resultado = dimensionar_rede_hidraulica(projeto)
    except ErroHidraulicaPredial as e:
        print(f"Erro no dimensionamento hidráulico: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        return 1

    status_geral = "APROVADO" if resultado.todos_criterios_atendidos else "REQUER AJUSTES"
    print(f"Edificação: '{resultado.nome_edificacao}' · Status NBR 5626: [{status_geral}]")
    print(f"Total de Trechos: {resultado.total_trechos} · Total de Aparelhos: {resultado.total_aparelhos}")
    print(f"Vazão Provável Global: {formatar_vazao_ls_br(resultado.vazao_provavel_global_mls)} "
          f"(Instalada: {formatar_vazao_ls_br(resultado.vazao_total_instalada_mls)} · ΣP: {resultado.soma_pesos_global_decimos // 10},{resultado.soma_pesos_global_decimos % 10})")
    print(f"Ponto Crítico Mais Desfavorável: Nó '{resultado.ponto_mais_desfavoravel_no}' com {formatar_mmca_para_mca_br(resultado.pressao_ponto_mais_desfavoravel_mmca)}")
    print(f"Pressão Estática Máxima: Nó '{resultado.ponto_maior_pressao_estatica_no}' com {formatar_mmca_para_mca_br(resultado.pressao_estatica_maxima_mmca)} (Limite: ≤ 40,00 m.c.a.)")
    print()
    print("--- TRECHOS DIMENSIONADOS ---")
    for t in resultado.trechos:
        soma_p = f"{t.soma_pesos_decimos // 10},{t.soma_pesos_decimos % 10}"
        vel_status = "OK" if t.velocidade_conforme else "ALTA!"
        print(f"  [{t.id_trecho:<5}] {t.no_origem} → {t.no_destino:<6} | ΣP: {soma_p:>4} | Q: {formatar_vazao_ls_br(t.vazao_projeto_mls):>8} | "
              f"DN {t.dn_selecionado:>3} ({t.polegadas_ref:<5}) | v: {formatar_velocidade_ms_br(t.velocidade_mms):>8} [{vel_status}] | "
              f"P.Dinâmica: {formatar_mmca_para_mca_br(t.pressao_dinamica_jusante_mmca):>10}")

    print()
    print("--- VERIFICAÇÃO NOS PONTOS DE CONSUMO ---")
    for pc in resultado.pontos_consumo:
        status_pc = "CONFORME" if pc.conforme else "INSUFICIENTE!"
        print(f"  [Nó {pc.no:<6}] {pc.nome_aparelho:<35} | Exigido: {formatar_mmca_para_mca_br(pc.pressao_minima_exigida_mmca):>10} | "
              f"Real: {formatar_mmca_para_mca_br(pc.pressao_dinamica_real_mmca):>10} | {status_pc}")

    if args.saida:
        dir_saida = Path(args.saida)
        dir_saida.mkdir(parents=True, exist_ok=True)

        res_dict = resultado_para_dict(resultado)
        (dir_saida / "resultado_hidraulico.json").write_text(serializar_json_canonico(res_dict), encoding="utf-8")
        (dir_saida / "trechos_dimensionados.csv").write_text(gerar_trechos_csv_str(resultado), encoding="utf-8")
        (dir_saida / "pontos_consumo.csv").write_text(gerar_pontos_consumo_csv_str(resultado), encoding="utf-8")
        (dir_saida / "memorial_calculo.md").write_text(gerar_relatorio_memorial_markdown(resultado), encoding="utf-8")
        (dir_saida / "painel_hidraulico.svg").write_text(gerar_painel_svg(resultado), encoding="utf-8")
        print(f"\nArtefatos técnicos gerados na pasta: {dir_saida.resolve()}")

    if args.zip:
        zip_caminho = Path(args.zip)
        res_dict = resultado_para_dict(resultado)
        json_bytes = serializar_json_canonico(res_dict).encode("utf-8")
        csv_trechos_bytes = gerar_trechos_csv_str(resultado).encode("utf-8")
        csv_pc_bytes = gerar_pontos_consumo_csv_str(resultado).encode("utf-8")
        md_bytes = gerar_relatorio_memorial_markdown(resultado).encode("utf-8")
        svg_bytes = gerar_painel_svg(resultado).encode("utf-8")

        arquivos_zip = [
            ("entrada_projeto.json", caminho.read_bytes()),
            ("resultado_hidraulico.json", json_bytes),
            ("trechos_dimensionados.csv", csv_trechos_bytes),
            ("pontos_consumo.csv", csv_pc_bytes),
            ("memorial_calculo.md", md_bytes),
            ("painel_hidraulico.svg", svg_bytes),
        ]
        try:
            criar_pacote_zip_deterministico(zip_caminho, arquivos_zip)
            print(f"Pacote ZIP determinístico gerado: {zip_caminho.resolve()}")
        except ErroHidraulicaPredial as e:
            print(f"Erro ao gerar ZIP: {e}", file=sys.stderr)
            return 1

    return 0


def comando_exemplo(args: argparse.Namespace) -> int:
    """Emite modelo JSON canônico."""
    json_str = serializar_json_canonico(EXEMPLO_CANONICO)
    if args.saida:
        p = Path(args.saida)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json_str, encoding="utf-8")
        print(f"Exemplo canônico gravado em: {p.resolve()}")
    else:
        sys.stdout.write(json_str)
    return 0


def comando_tabelas(args: argparse.Namespace) -> int:
    """Exibe catálogo normativo de aparelhos sanitários e tubulações PVC."""
    print("=== APARELHOS SANITÁRIOS NORMATIVOS (NBR 5626:2020 - TABELA B.1) ===")
    for codigo, ap in sorted(APARELHOS_SANITARIOS.items()):
        p_str = f"{ap.peso_relativo_decimos // 10},{ap.peso_relativo_decimos % 10}"
        print(f"  [{codigo:<24}] {ap.nome:<38} | Peso: {p_str:>4} | Q_mín: {formatar_vazao_ls_br(ap.vazao_minima_mls):>8} | "
              f"P_mín: {formatar_mmca_para_mca_br(ap.pressao_minima_mmca):>10}")

    print("\n=== TUBULAÇÕES COMERCIAIS DE PVC SOLDÁVEL (NBR 5648) ===")
    for d in DIAMETROS_PVC:
        print(f"  DN {d.dn:<3} ({d.polegadas_ref:<6}) | D_externo: {d.diametro_externo_mm:>3} mm | "
              f"D_interno: {d.diametro_interno_decimos_mm // 10},{d.diametro_interno_decimos_mm % 10} mm")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Ponto de entrada da CLI."""
    parser = criar_parser()
    args = parser.parse_args(argv)

    if args.subcomando == "dimensionar":
        return comando_dimensionar(args)
    elif args.subcomando == "exemplo":
        return comando_exemplo(args)
    elif args.subcomando == "tabelas":
        return comando_tabelas(args)
    elif args.subcomando == "versao":
        print(f"dimensionamento-hidraulica-predial-nbr5626 {VERSAO}")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
