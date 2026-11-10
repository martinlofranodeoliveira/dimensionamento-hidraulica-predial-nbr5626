"""Testes unitários dos modelos e validações de domínio (NBR 5626).

LOFRANO TECNOLOGIA.
"""

import unittest

from hidraulica_predial.domain import (
    ConexaoTrecho,
    InstalacaoPredialInput,
    PontoConsumo,
    TrechoInput,
    formatar_milimetros_para_metros_br,
    formatar_mmca_para_mca_br,
    formatar_vazao_ls_br,
    formatar_velocidade_ms_br,
)
from hidraulica_predial.errors import ErroValidacaoEntrada


class TestDomain(unittest.TestCase):
    """Testes unitários de regras e formatações de domínio."""

    def test_conexao_valida(self):
        c = ConexaoTrecho(tipo="JOELHO_90", quantidade=3)
        self.assertEqual(c.tipo, "JOELHO_90")
        self.assertEqual(c.quantidade, 3)

    def test_conexao_tipo_desconhecido(self):
        with self.assertRaises(ErroValidacaoEntrada):
            ConexaoTrecho(tipo="CONEXAO_FANTASMA", quantidade=1)

    def test_conexao_quantidade_invalida(self):
        with self.assertRaises(ErroValidacaoEntrada):
            ConexaoTrecho(tipo="JOELHO_90", quantidade=0)
        with self.assertRaises(ErroValidacaoEntrada):
            ConexaoTrecho(tipo="JOELHO_90", quantidade=-2)

    def test_ponto_consumo_valido(self):
        pc = PontoConsumo(codigo_aparelho="CHUVEIRO_ELETRICO", descricao="Chuveiro Suite", quantidade=2)
        self.assertEqual(pc.codigo_aparelho, "CHUVEIRO_ELETRICO")
        self.assertEqual(pc.quantidade, 2)

    def test_ponto_consumo_aparelho_invalido(self):
        with self.assertRaises(ErroValidacaoEntrada):
            PontoConsumo(codigo_aparelho="TURBINA_A_VAPOR", descricao="Inexistente", quantidade=1)

    def test_trecho_valido(self):
        t = TrechoInput(
            id_trecho="T1",
            no_origem="A",
            no_destino="B",
            comprimento_real_mm=3500,
            desnivel_geometrico_mm=1000,
        )
        self.assertEqual(t.id_trecho, "T1")
        self.assertEqual(t.comprimento_real_mm, 3500)

    def test_trecho_mesmo_no_origem_destino(self):
        with self.assertRaises(ErroValidacaoEntrada):
            TrechoInput(
                id_trecho="T1",
                no_origem="A",
                no_destino="A",
                comprimento_real_mm=1000,
                desnivel_geometrico_mm=0,
            )

    def test_trecho_comprimento_zero_ou_negativo(self):
        with self.assertRaises(ErroValidacaoEntrada):
            TrechoInput(id_trecho="T1", no_origem="A", no_destino="B", comprimento_real_mm=0, desnivel_geometrico_mm=0)
        with self.assertRaises(ErroValidacaoEntrada):
            TrechoInput(id_trecho="T1", no_origem="A", no_destino="B", comprimento_real_mm=-500, desnivel_geometrico_mm=0)

    def test_trecho_dn_fixado_invalido(self):
        with self.assertRaises(ErroValidacaoEntrada):
            TrechoInput(
                id_trecho="T1",
                no_origem="A",
                no_destino="B",
                comprimento_real_mm=1000,
                desnivel_geometrico_mm=0,
                dn_fixado=999,
            )

    def test_instalacao_predial_sem_trechos(self):
        with self.assertRaises(ErroValidacaoEntrada):
            InstalacaoPredialInput(
                nome_edificacao="Casa",
                descricao="Teste",
                pressao_disponivel_inicial_mmca=1000,
                no_origem_principal="RES",
                trechos=[],
            )

    def test_instalacao_pressao_negativa(self):
        t = TrechoInput("T1", "RES", "B", 1000, 0)
        with self.assertRaises(ErroValidacaoEntrada):
            InstalacaoPredialInput(
                nome_edificacao="Casa",
                descricao="Teste",
                pressao_disponivel_inicial_mmca=-100,
                no_origem_principal="RES",
                trechos=[t],
            )

    def test_formatadores_pt_br(self):
        self.assertEqual(formatar_milimetros_para_metros_br(3500), "3,50 m")
        self.assertEqual(formatar_milimetros_para_metros_br(-1200), "-1,20 m")
        self.assertEqual(formatar_milimetros_para_metros_br(50), "0,05 m")

        self.assertEqual(formatar_mmca_para_mca_br(1500), "1,50 m.c.a.")
        self.assertEqual(formatar_mmca_para_mca_br(12345), "12,34 m.c.a.")

        self.assertEqual(formatar_vazao_ls_br(150), "0,15 L/s")
        self.assertEqual(formatar_vazao_ls_br(1700), "1,70 L/s")

        self.assertEqual(formatar_velocidade_ms_br(1420), "1,42 m/s")
        self.assertEqual(formatar_velocidade_ms_br(2850), "2,85 m/s")


if __name__ == "__main__":
    unittest.main()
