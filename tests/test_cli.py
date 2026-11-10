"""Testes unitários da interface de linha de comando (CLI) NBR 5626.

LOFRANO TECNOLOGIA.
"""

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from hidraulica_predial.cli import EXEMPLO_CANONICO, VERSAO, main


class TestCLI(unittest.TestCase):
    """Testes unitários de todos os comandos e opções da CLI."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.caminho_temp = Path(self.temp_dir.name)
        self.arquivo_json = self.caminho_temp / "projeto_teste.json"
        self.arquivo_json.write_text(json.dumps(EXEMPLO_CANONICO), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_sem_argumentos(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            codigo = main([])
            self.assertEqual(codigo, 0)
            self.assertIn("hidraulica-nbr5626", mock_stdout.getvalue())

    def test_cli_versao_subcomando(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            codigo = main(["versao"])
            self.assertEqual(codigo, 0)
            self.assertIn(f"dimensionamento-hidraulica-predial-nbr5626 {VERSAO}", mock_stdout.getvalue())

    def test_cli_versao_flag(self):
        with patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as ctx:
                main(["--version"])
            self.assertEqual(ctx.exception.code, 0)

    def test_cli_tabelas(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            codigo = main(["tabelas"])
            self.assertEqual(codigo, 0)
            saida = mock_stdout.getvalue()
            self.assertIn("APARELHOS SANITÁRIOS NORMATIVOS", saida)
            self.assertIn("CHUVEIRO_ELETRICO", saida)
            self.assertIn("TUBULAÇÕES COMERCIAIS DE PVC", saida)

    def test_cli_exemplo_stdout(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            codigo = main(["exemplo"])
            self.assertEqual(codigo, 0)
            dados = json.loads(mock_stdout.getvalue())
            self.assertEqual(dados["nome_edificacao"], "Residência Unifamiliar Padrão - Sobrado")

    def test_cli_exemplo_arquivo(self):
        saida = self.caminho_temp / "modelo.json"
        with patch("sys.stdout", new_callable=io.StringIO):
            codigo = main(["exemplo", "--saida", str(saida)])
            self.assertEqual(codigo, 0)
            self.assertTrue(saida.exists())
            dados = json.loads(saida.read_text(encoding="utf-8"))
            self.assertIn("trechos", dados)

    def test_cli_dimensionar_arquivo_inexistente(self):
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            codigo = main(["dimensionar", str(self.caminho_temp / "nao_existe.json")])
            self.assertEqual(codigo, 1)
            self.assertIn("Arquivo não encontrado", mock_stderr.getvalue())

    def test_cli_dimensionar_sucesso(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            codigo = main(["dimensionar", str(self.arquivo_json)])
            self.assertEqual(codigo, 0)
            saida = mock_stdout.getvalue()
            self.assertIn("TRECHOS DIMENSIONADOS", saida)
            self.assertIn("VERIFICAÇÃO NOS PONTOS DE CONSUMO", saida)
            self.assertIn("Status NBR 5626: [APROVADO]", saida)

    def test_cli_dimensionar_com_saida(self):
        dir_saida = self.caminho_temp / "relatorios"
        with patch("sys.stdout", new_callable=io.StringIO):
            codigo = main(["dimensionar", str(self.arquivo_json), "--saida", str(dir_saida)])
        self.assertEqual(codigo, 0)

        self.assertTrue((dir_saida / "resultado_hidraulico.json").exists())
        self.assertTrue((dir_saida / "trechos_dimensionados.csv").exists())
        self.assertTrue((dir_saida / "pontos_consumo.csv").exists())
        self.assertTrue((dir_saida / "memorial_calculo.md").exists())
        self.assertTrue((dir_saida / "painel_hidraulico.svg").exists())

    def test_cli_dimensionar_com_zip(self):
        zip_saida = self.caminho_temp / "dossie.zip"
        with patch("sys.stdout", new_callable=io.StringIO):
            codigo = main(["dimensionar", str(self.arquivo_json), "--zip", str(zip_saida)])
        self.assertEqual(codigo, 0)
        self.assertTrue(zip_saida.exists())
        self.assertGreater(zip_saida.stat().st_size, 100)

    def test_cli_dimensionar_zip_existente_falha(self):
        zip_saida = self.caminho_temp / "bloqueado.zip"
        zip_saida.write_bytes(b"dados")
        with patch("sys.stdout", new_callable=io.StringIO):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                codigo = main(["dimensionar", str(self.arquivo_json), "--zip", str(zip_saida)])
                self.assertEqual(codigo, 1)
                self.assertIn("Erro ao gerar ZIP", mock_stderr.getvalue())

    def test_cli_dimensionar_arquivo_invalido(self):
        invalido = dict(EXEMPLO_CANONICO)
        invalido["trechos"] = []
        arquivo_bad = self.caminho_temp / "invalido.json"
        arquivo_bad.write_text(json.dumps(invalido), encoding="utf-8")

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            codigo = main(["dimensionar", str(arquivo_bad)])
            self.assertEqual(codigo, 1)
            self.assertIn("Erro no dimensionamento hidráulico", mock_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
