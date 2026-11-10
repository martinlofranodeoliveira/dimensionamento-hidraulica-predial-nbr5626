"""Testes unitários dos codecs canônicos e serializadores JSON (NBR 5626).

LOFRANO TECNOLOGIA.
"""

from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from hidraulica_predial.calculator import dimensionar_rede_hidraulica
from hidraulica_predial.codecs import (
    carregar_projeto,
    decodificar_json_canonico,
    resultado_para_dict,
    serializar_json_canonico,
)
from hidraulica_predial.domain import (
    ConexaoTrecho,
    InstalacaoPredialInput,
    PontoConsumo,
    TrechoInput,
)
from hidraulica_predial.errors import ErroCodec


class TestCodecs(unittest.TestCase):
    """Testes dos requisitos estritos de segurança e determinismo de codecs."""

    def test_decodificar_valido(self):
        dados = decodificar_json_canonico('{"nome": "Casa", "pressao": 1500}')
        self.assertEqual(dados["nome"], "Casa")
        self.assertEqual(dados["pressao"], 1500)

    def test_rejeitar_bom_bytes(self):
        com_bom = b"\xef\xbb\xbf{\"nome\": \"Casa\"}"
        with self.assertRaises(ErroCodec) as ctx:
            decodificar_json_canonico(com_bom)
        self.assertIn("BOM", ctx.exception.mensagem)

    def test_rejeitar_bom_str(self):
        com_bom = "\ufeff{\"nome\": \"Casa\"}"
        with self.assertRaises(ErroCodec) as ctx:
            decodificar_json_canonico(com_bom)
        self.assertIn("BOM", ctx.exception.mensagem)

    def test_rejeitar_float_na_leitura(self):
        com_float = '{"nome": "Casa", "pressao": 15.5}'
        with self.assertRaises(ErroCodec) as ctx:
            decodificar_json_canonico(com_float)
        self.assertIn("float", ctx.exception.mensagem.lower())

    def test_rejeitar_chave_duplicada(self):
        duplicada = '{"campo": 1, "campo": 2}'
        with self.assertRaises(ErroCodec) as ctx:
            decodificar_json_canonico(duplicada)
        self.assertIn("duplicada", ctx.exception.mensagem)

    def test_rejeitar_profundidade_excessiva(self):
        aninhado: dict = {}
        curr = aninhado
        for _ in range(35):
            curr["filho"] = {}
            curr = curr["filho"]
        texto = json.dumps(aninhado)
        with self.assertRaises(ErroCodec) as ctx:
            decodificar_json_canonico(texto)
        self.assertIn("Profundidade", ctx.exception.mensagem)

    def test_serializacao_deterministica(self):
        d1 = {"z": 10, "a": 1, "m": 5}
        d2 = {"a": 1, "m": 5, "z": 10}
        s1 = serializar_json_canonico(d1)
        s2 = serializar_json_canonico(d2)
        self.assertEqual(s1, s2)

    def test_rejeitar_float_na_serializacao(self):
        invalido = {"valor": 3.14}
        with self.assertRaises(ErroCodec):
            serializar_json_canonico(invalido)

    def test_carregar_projeto_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            carregar_projeto("arquivo_fantasma.json")

    def test_carregar_projeto_campos_ausentes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write(json.dumps({"nome_edificacao": "Teste"}))
            caminho = f.name
        try:
            with self.assertRaises(ErroCodec) as ctx:
                carregar_projeto(caminho)
            self.assertIn("obrigatório ausente", ctx.exception.mensagem)
        finally:
            Path(caminho).unlink(missing_ok=True)

    def test_carregar_projeto_e_resultado_para_dict(self):
        t1 = TrechoInput(
            id_trecho="T1",
            no_origem="RES",
            no_destino="LAV",
            comprimento_real_mm=2000,
            desnivel_geometrico_mm=1000,
            conexoes=[ConexaoTrecho("JOELHO_90", 1)],
            aparelhos_diretos=[PontoConsumo("LAVATORIO", "Lavatorio", 1)],
        )
        projeto = InstalacaoPredialInput(
            nome_edificacao="Residencial Alpha",
            descricao="Projeto Teste",
            pressao_disponivel_inicial_mmca=1000,
            no_origem_principal="RES",
            trechos=[t1],
        )

        res = dimensionar_rede_hidraulica(projeto)
        dict_res = resultado_para_dict(res)

        self.assertEqual(dict_res["edificacao"]["nome"], "Residencial Alpha")
        self.assertEqual(dict_res["resumo_engenharia"]["total_trechos"], 1)
        self.assertEqual(len(dict_res["trechos"]), 1)
        self.assertEqual(len(dict_res["pontos_consumo"]), 1)
        self.assertIn("vazao_projeto_formatada", dict_res["trechos"][0])


if __name__ == "__main__":
    unittest.main()
