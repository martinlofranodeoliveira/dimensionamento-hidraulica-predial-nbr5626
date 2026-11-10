"""Testes unitários do motor de cálculo hidráulico predial NBR 5626.

LOFRANO TECNOLOGIA.
"""

import unittest

from hidraulica_predial.calculator import (
    calcular_vazao_provavel_mls,
    calcular_velocidade_mms,
    dimensionar_rede_hidraulica,
    mapear_aparelhos_jusante,
    ordenar_topologicamente,
    selecionar_menor_dn_admissivel,
)
from hidraulica_predial.domain import (
    ConexaoTrecho,
    InstalacaoPredialInput,
    PontoConsumo,
    TrechoInput,
)
from hidraulica_predial.errors import ErroTopologiaRede


class TestCalculator(unittest.TestCase):
    """Testes unitários do dimensionamento, topologia e equações hidráulicas."""

    def test_vazao_provavel_pesos_conhecidos(self):
        # 0 pesos -> 0
        self.assertEqual(calcular_vazao_provavel_mls(0), 0)
        self.assertEqual(calcular_vazao_provavel_mls(-10), 0)

        # 10 décimos = 1.0 unidade de peso: Q = 0,30 * sqrt(1) = 0,30 L/s = 300 mL/s
        self.assertEqual(calcular_vazao_provavel_mls(10), 300)

        # 40 décimos = 4.0 unidades de peso: Q = 0,30 * sqrt(4) = 0,60 L/s = 600 mL/s
        self.assertEqual(calcular_vazao_provavel_mls(40), 600)

        # 90 décimos = 9.0 unidades de peso: Q = 0,30 * sqrt(9) = 0,90 L/s = 900 mL/s
        self.assertEqual(calcular_vazao_provavel_mls(90), 900)

    def test_velocidade_escoamento(self):
        self.assertEqual(calcular_velocidade_mms(0, 170), 0)
        self.assertEqual(calcular_velocidade_mms(150, 0), 0)

        # Vazão 150 mL/s em DN 20 (d_int = 17,0 mm = 170 décimos):
        # v = (150 * 45_200_000) / (355 * 170^2) = 6_780_000_000 / (355 * 28900)
        # = 6_780_000_000 / 10_259_500 = 660 mm/s (0,66 m/s)
        vel = calcular_velocidade_mms(150, 170)
        self.assertEqual(vel, 661)  # com arredondamento no meio

    def test_selecao_menor_dn_admissivel(self):
        # Vazão moderada (200 mL/s) pode usar DN 20 com vel ~ 0.88 m/s
        dn, d_int, vel = selecionar_menor_dn_admissivel(200, 3000)
        self.assertEqual(dn, 20)
        self.assertLessEqual(vel, 3000)

        # Com válvula de descarga, mínimo DN 40
        dn_v, _, _ = selecionar_menor_dn_admissivel(1700, 3000, possui_valvula_descarga=True)
        self.assertGreaterEqual(dn_v, 40)

        # DN fixado pelo usuário
        dn_f, d_int_f, _ = selecionar_menor_dn_admissivel(150, 3000, dn_fixado=32)
        self.assertEqual(dn_f, 32)
        self.assertEqual(d_int_f, 278)

    def test_topologia_ordenacao_sucesso(self):
        t1 = TrechoInput("T1", "RES", "BAR", 1000, 500)
        t2 = TrechoInput("T2", "BAR", "P1", 2000, 1000)
        t3 = TrechoInput("T3", "BAR", "P2", 2000, 1000)

        ordenados = ordenar_topologicamente([t3, t1, t2], "RES")
        ids = [t.id_trecho for t in ordenados]
        self.assertEqual(ids[0], "T1")
        self.assertIn("T2", ids[1:])
        self.assertIn("T3", ids[1:])

    def test_topologia_raiz_inexistente(self):
        t1 = TrechoInput("T1", "A", "B", 1000, 0)
        with self.assertRaises(ErroTopologiaRede):
            ordenar_topologicamente([t1], "RAIZ_INEXISTENTE")

    def test_topologia_ciclo_detectado(self):
        # Ciclo A -> B -> C -> A
        t1 = TrechoInput("T1", "A", "B", 1000, 0)
        t2 = TrechoInput("T2", "B", "C", 1000, 0)
        t3 = TrechoInput("T3", "C", "A", 1000, 0)
        with self.assertRaises(ErroTopologiaRede):
            ordenar_topologicamente([t1, t2, t3], "A")

    def test_mapear_aparelhos_jusante(self):
        # T1 (RES -> BAR)
        # T2 (BAR -> CHUV): chuveiro (peso 4)
        # T3 (BAR -> LAV): lavatorio (peso 3)
        t1 = TrechoInput("T1", "RES", "BAR", 1000, 0)
        t2 = TrechoInput("T2", "BAR", "CHUV", 1000, 0, aparelhos_diretos=[PontoConsumo("CHUVEIRO_ELETRICO", "Chuv", 1)])
        t3 = TrechoInput("T3", "BAR", "LAV", 1000, 0, aparelhos_diretos=[PontoConsumo("LAVATORIO", "Lav", 1)])

        ordenados = [t1, t2, t3]
        mapa = mapear_aparelhos_jusante(ordenados)

        self.assertEqual(len(mapa["T2"]), 1)
        self.assertEqual(mapa["T2"][0][0], "CHUVEIRO_ELETRICO")

        self.assertEqual(len(mapa["T3"]), 1)
        self.assertEqual(mapa["T3"][0][0], "LAVATORIO")

        # T1 alimenta ambos
        self.assertEqual(len(mapa["T1"]), 2)
        codigos_t1 = [a[0] for a in mapa["T1"]]
        self.assertIn("CHUVEIRO_ELETRICO", codigos_t1)
        self.assertIn("LAVATORIO", codigos_t1)

    def test_dimensionamento_completo_rede_simples(self):
        # Reservatório a 1,5m de altura (1500 mmca)
        # T1 desce 2,5m (2500 mm) até o chuveiro: desnivel = 2500 mm
        t1 = TrechoInput(
            id_trecho="T1",
            no_origem="RES",
            no_destino="CHUV",
            comprimento_real_mm=3000,
            desnivel_geometrico_mm=2500,
            conexoes=[
                ConexaoTrecho("SAIDA_CANALIZACAO", 1),
                ConexaoTrecho("JOELHO_90", 2),
                ConexaoTrecho("REGISTRO_PRESSAO_ABERTO", 1),
            ],
            aparelhos_diretos=[PontoConsumo("CHUVEIRO_ELETRICO", "Chuveiro", 1)],
        )
        projeto = InstalacaoPredialInput(
            nome_edificacao="Teste Simples",
            descricao="Chuveiro isolado",
            pressao_disponivel_inicial_mmca=1500,
            no_origem_principal="RES",
            trechos=[t1],
        )

        res = dimensionar_rede_hidraulica(projeto)
        self.assertEqual(res.total_trechos, 1)
        self.assertEqual(res.total_aparelhos, 1)
        self.assertTrue(res.todos_criterios_atendidos)

        td = res.trechos[0]
        self.assertEqual(td.dn_selecionado, 20)  # DN 20 suporta 200 mL/s com velocidade baixa
        self.assertGreater(td.comprimento_total_mm, 3000)  # inclui conexões
        self.assertGreater(td.pressao_dinamica_jusante_mmca, 1000)  # chuveiro requer >= 1000 mmca
        self.assertTrue(td.velocidade_conforme)
        self.assertTrue(td.pressao_dinamica_conforme)


if __name__ == "__main__":
    unittest.main()
