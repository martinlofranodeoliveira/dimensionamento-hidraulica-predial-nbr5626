"""Testes unitários das tabelas normativas e interpolações hidráulicas NBR 5626.

LOFRANO TECNOLOGIA.
"""

from fractions import Fraction
import unittest

from hidraulica_predial.tabelas_nbr5626 import (
    APARELHOS_SANITARIOS,
    COMPRIMENTOS_EQUIVALENTES_MM,
    DIAMETROS_PVC,
    MAPA_DIAMETROS_PVC,
    calcular_perda_carga_unitaria_racional,
    obter_comprimento_equivalente_conexao,
)


class TestTabelas(unittest.TestCase):
    """Testes unitários do catálogo de aparelhos, conexões e diâmetros."""

    def test_catalogo_aparelhos(self):
        self.assertIn("CHUVEIRO_ELETRICO", APARELHOS_SANITARIOS)
        self.assertIn("BACIA_VALVULA_DESCARGA", APARELHOS_SANITARIOS)
        self.assertIn("PIA_COZINHA", APARELHOS_SANITARIOS)

        chuv = APARELHOS_SANITARIOS["CHUVEIRO_ELETRICO"]
        self.assertEqual(chuv.peso_relativo_decimos, 4)
        self.assertEqual(chuv.vazao_minima_mls, 200)
        self.assertEqual(chuv.pressao_minima_mmca, 1000)

        valv = APARELHOS_SANITARIOS["BACIA_VALVULA_DESCARGA"]
        self.assertEqual(valv.peso_relativo_decimos, 320)
        self.assertEqual(valv.vazao_minima_mls, 1700)
        self.assertEqual(valv.pressao_minima_mmca, 1500)

    def test_diametros_pvc_ordenados_e_monotonicos(self):
        dns = [d.dn for d in DIAMETROS_PVC]
        self.assertEqual(dns, sorted(dns))

        # Diâmetros internos devem ser estritamente crescentes
        d_ints = [d.diametro_interno_decimos_mm for d in DIAMETROS_PVC]
        for i in range(len(d_ints) - 1):
            self.assertLess(d_ints[i], d_ints[i + 1])

        # Verificar mapa
        self.assertIn(20, MAPA_DIAMETROS_PVC)
        self.assertEqual(MAPA_DIAMETROS_PVC[25].diametro_interno_decimos_mm, 216)

    def test_comprimentos_equivalentes_conexoes(self):
        # Joelho 90º em DN 20 deve ter 1100 mm (1,1 m)
        leq = obter_comprimento_equivalente_conexao("JOELHO_90", 20)
        self.assertEqual(leq, 1100)

        # Joelho 90º em DN 50 deve ter 3200 mm (3,2 m)
        leq50 = obter_comprimento_equivalente_conexao("JOELHO_90", 50)
        self.assertEqual(leq50, 3200)

        # Conexão desconhecida deve retornar 0
        self.assertEqual(obter_comprimento_equivalente_conexao("CONEXAO_INEXISTENTE", 20), 0)
        # DN inexistente deve retornar 0
        self.assertEqual(obter_comprimento_equivalente_conexao("JOELHO_90", 999), 0)

    def test_perda_carga_vazao_zero(self):
        j = calcular_perda_carga_unitaria_racional(25, 0)
        self.assertEqual(j, Fraction(0, 1))
        j_neg = calcular_perda_carga_unitaria_racional(25, -100)
        self.assertEqual(j_neg, Fraction(0, 1))

    def test_perda_carga_ponto_exato(self):
        # Em DN 20, para 100 mL/s, J tabelado é 27 mmca/m
        j = calcular_perda_carga_unitaria_racional(20, 100)
        self.assertEqual(j, Fraction(27, 1))

    def test_perda_carga_interpolada_racional(self):
        # Em DN 20, entre 100 (J=27) e 150 (J=55) mL/s
        # Ponto médio exato 125 mL/s:
        # delta_q = 50, delta_j = 28 => J = 27 + 28 * 25 / 50 = 27 + 14 = 41 mmca/m
        j_medio = calcular_perda_carga_unitaria_racional(20, 125)
        self.assertEqual(j_medio, Fraction(41, 1))

    def test_perda_carga_monotonia(self):
        # Para um mesmo DN, J deve ser estritamente crescente com a vazão
        j1 = calcular_perda_carga_unitaria_racional(25, 100)
        j2 = calcular_perda_carga_unitaria_racional(25, 200)
        j3 = calcular_perda_carga_unitaria_racional(25, 500)
        self.assertLess(j1, j2)
        self.assertLess(j2, j3)


if __name__ == "__main__":
    unittest.main()
