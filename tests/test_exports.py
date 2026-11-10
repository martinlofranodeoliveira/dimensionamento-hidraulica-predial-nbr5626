"""Testes unitários dos exportadores CSV, Markdown, SVG e ZIP (NBR 5626).

LOFRANO TECNOLOGIA.
"""

from pathlib import Path
import tempfile
import unittest
import zipfile

from hidraulica_predial.calculator import dimensionar_rede_hidraulica
from hidraulica_predial.domain import (
    ConexaoTrecho,
    InstalacaoPredialInput,
    PontoConsumo,
    TrechoInput,
)
from hidraulica_predial.errors import ErroExportacao
from hidraulica_predial.exports import (
    criar_pacote_zip_deterministico,
    gerar_pontos_consumo_csv_str,
    gerar_relatorio_memorial_markdown,
    gerar_trechos_csv_str,
    sanitizar_campo_csv,
)
from hidraulica_predial.svg_report import gerar_painel_svg


class TestExports(unittest.TestCase):
    """Testes de exportações, relatórios e proteções de formato."""

    def setUp(self):
        self.t1 = TrechoInput(
            id_trecho="T1",
            no_origem="RES",
            no_destino="CHUV",
            comprimento_real_mm=2500,
            desnivel_geometrico_mm=2000,
            conexoes=[ConexaoTrecho("JOELHO_90", 2)],
            aparelhos_diretos=[PontoConsumo("CHUVEIRO_ELETRICO", "Ducha", 1)],
        )
        self.projeto = InstalacaoPredialInput(
            nome_edificacao="Sobrado Teste",
            descricao="Memorial e Exportações",
            pressao_disponivel_inicial_mmca=1500,
            no_origem_principal="RES",
            trechos=[self.t1],
        )
        self.resultado = dimensionar_rede_hidraulica(self.projeto)

    def test_sanitizar_campo_csv_formula_injection(self):
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+SOMAR()"), "'+SOMAR()")
        self.assertEqual(sanitizar_campo_csv("-100"), "'-100")
        self.assertEqual(sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(sanitizar_campo_csv("TextoNormal"), "TextoNormal")
        self.assertEqual(sanitizar_campo_csv(""), "")

    def test_gerar_trechos_csv_str(self):
        csv_str = gerar_trechos_csv_str(self.resultado)
        self.assertIn("ID_Trecho;No_Origem;No_Destino", csv_str)
        self.assertIn("T1;RES;CHUV", csv_str)
        self.assertIn("CONFORME", csv_str)

    def test_gerar_pontos_consumo_csv_str(self):
        csv_str = gerar_pontos_consumo_csv_str(self.resultado)
        self.assertIn("No_Terminal;Codigo_Aparelho;Nome_Aparelho", csv_str)
        self.assertIn("CHUV;CHUVEIRO_ELETRICO", csv_str)
        self.assertIn("APROVADO", csv_str)

    def test_gerar_relatorio_memorial_markdown(self):
        md = gerar_relatorio_memorial_markdown(self.resultado)
        self.assertIn("# Memorial Descritivo e de Cálculo Hidráulico Predial — NBR 5626", md)
        self.assertIn("Sobrado Teste", md)
        self.assertIn("Ponto Hidraulicamente Mais Desfavorável", md)
        self.assertIn("LOFRANO TECNOLOGIA", md)

    def test_gerar_painel_svg(self):
        svg = gerar_painel_svg(self.resultado)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("DIMENSIONAMENTO HIDRÁULICO PREDIAL", svg)
        self.assertIn("CONFORME NBR 5626", svg)
        self.assertTrue(svg.endswith("</svg>\n"))

    def test_criar_pacote_zip_deterministico(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "teste.zip"
            arquivos = [
                ("dados.txt", b"conteudo de teste"),
                ("outro.csv", b"a;b;c\n1;2;3"),
            ]
            criar_pacote_zip_deterministico(zip_path, arquivos)
            self.assertTrue(zip_path.exists())

            with zipfile.ZipFile(zip_path, "r") as zf:
                nomes = zf.namelist()
                self.assertEqual(nomes, ["dados.txt", "outro.csv"])
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))

            # Testar que não sobrescreve
            with self.assertRaises(ErroExportacao):
                criar_pacote_zip_deterministico(zip_path, arquivos)


if __name__ == "__main__":
    unittest.main()
