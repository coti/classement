from __future__ import unicode_literals

import unittest
from classement import *


class TestClassement(unittest.TestCase):

    def test_estNumerote(self):
        self.assertFalse(estNumerote("NC"))
        self.assertFalse(estNumerote("ND"))
        self.assertFalse(estNumerote("30"))
        self.assertFalse(estNumerote("-15"))
        self.assertTrue(estNumerote("N10"))
        self.assertTrue(estNumerote("T100"))

    def test_normalisation(self):
        self.assertEqual("Top 40/Top 60", normalisation("N40", "F"))
        self.assertEqual("Top 60/Top 100", normalisation("N41", "F"))
        self.assertEqual("Top 40/Top 60", normalisation("N60", "H"))
        self.assertEqual("Top 60/Top 100", normalisation("N61", "H"))
        self.assertEqual("Top 40/Top 60", normalisation("T40", "H"))
        self.assertEqual("Top 40/Top 60", normalisation("Top 40/Top 60", "H"))
        self.assertEqual("NC", normalisation("NC (2014)", "H"))

    def test_normalisationTab(self):
        self.assertEqual([("Top 40/Top 60", False, 1)], normalisationTab([("N51", False, 1)], "H"))

    def test_nbWO(self):
        self.assertEqual(0, nbWO([]))
        self.assertEqual(0, nbWO([("NC", False, 1)]))
        self.assertEqual(1, nbWO([("NC", True, 1)]))
        self.assertEqual(1, nbWO([("NC", False, 1), ("NC", True, 1)]))

    def test_echelonInferieur(self):
        self.assertEqual("NC", echelonInferieur("NC"))
        self.assertEqual("NC", echelonInferieur("ND"))
        self.assertEqual("NC", echelonInferieur("40"))
        self.assertEqual("40", echelonInferieur("30/5"))
        self.assertEqual("30/5", echelonInferieur("30/4"))
        self.assertEqual("-15", echelonInferieur("Top 60/Top 100"))
        self.assertEqual("Top 60/Top 100", echelonInferieur("Top 40/Top 60"))
        self.assertRaises(KeyError, lambda: echelonInferieur("toto"))

    def test_absenceDef(self):
        self.assertTrue(absenceDef([], "15"))  # Aucune défaite
        self.assertTrue(absenceDef([("4/6", False, 1)], "15"))  # Défaite à classement supérieur
        self.assertFalse(absenceDef([("15", False, 1)], "15"))  # Défaite à classement égal
        self.assertFalse(absenceDef([("15/1", False, 1)], "15"))  # Défaite à classement inférieur
        self.assertFalse(absenceDef([("4/6", False, 1), ("15", False, 1)], "15"))  # 2 défaites dont une à classement égal
        self.assertTrue(absenceDef([("30/5", True, 1)], "15"))  # Les défaites par WO ne comptent pas

    def test_lstInf(self):
        d_15 = ("15", False, 1)
        d_15_1 = ("15/1", False, 1)
        d_4_6 = ("4/6", False, 1)
        d_wo = ("30", True, 1)
        d_wo_3 = ("S", True, 1)

        self.assertEqual([], lstInf("15", [], 0))  # Aucune défaite

        # Calcul des défaites à échelon égal
        self.assertEqual([], lstInf("15", [d_15_1], 0))  # Défaite à échelon -1 : ne compte pas
        self.assertEqual([d_15], lstInf("15", [d_15], 0))  # Défaite à échelon égal
        self.assertEqual([], lstInf("15", [d_4_6], 0))  # Défaite à échelon supérieur : ne compte pas
        self.assertEqual([], lstInf("15", [d_wo], 0))  # Défaite par WO : ne compte pas

        # Calcul des défaites à échelon -1
        self.assertEqual([d_15_1], lstInf("15", [d_15_1], 1))  # Défaite à échelon -1
        self.assertEqual([], lstInf("15", [d_15], 1))  # Défaite à échelon égal : ne compte pas
        self.assertEqual([], lstInf("15", [d_4_6], 1))  # Défaite à échelon supérieur : ne compte pas
        self.assertEqual([], lstInf("15", [d_wo], 1))  # Défaite par WO : ne compte pas

        # Calcul des défaites à échelon -2 ou moins
        self.assertEqual([d_15_1], lstInf("5/6", [d_15_1], -1))  # Défaite à échelon -2
        self.assertEqual([], lstInf("5/6", [d_15], -1))  # Défaite à échelon -1 : ne compte pas
        self.assertEqual([], lstInf("5/6", [d_4_6], -1))  # Défaite à échelon supérieur : ne compte pas
        self.assertEqual([], lstInf("5/6", [d_wo], -1))  # Défaite par WO : ne compte pas

        # Les WO à partir du 3ème (classement "S") comptent comme une défaite à -2
        self.assertEqual([], lstInf("15", [d_wo_3], 0))
        self.assertEqual([], lstInf("15", [d_wo_3], 1))
        self.assertEqual([d_wo_3], lstInf("15", [d_wo_3], -1))

    def test_arrondi(self):
        self.assertEqual(0, arrondi(0))
        self.assertEqual(1, arrondi(1))
        self.assertEqual(0, arrondi(0.4))
        self.assertEqual(1, arrondi(0.5))
        self.assertEqual(1, arrondi(0.6))
        self.assertEqual(0, arrondi(-0.5))
        self.assertEqual(-1, arrondi(-0.6))
        self.assertEqual(-1, arrondi(-0.9))
        self.assertEqual(-1, arrondi(-1))
        self.assertEqual(-1, arrondi(-1.5))
        self.assertEqual(-2, arrondi(-1.6))

    def test_VE2I5G(self):
        victoires = [("15", False, 1)]

        # Défaites à coefficients entiers
        defaites = [("15", False, 1), ("15/1", False, 1), ("15/2", False, 1)]
        self.assertEqual(-7, VE2I5G("15", victoires, defaites))
        self.assertEqual(-2, VE2I5G("15/1", victoires, defaites))
        self.assertEqual(0, VE2I5G("15/2", victoires, defaites))

        # Défaites à coefficients non entiers
        defaites_coeff = [("15", False, 0.7), ("15/1", False, 0.6), ("15/2", False, 0.5)]
        self.assertEqual(-3, VE2I5G("15", victoires, defaites_coeff))    # -3.4 -> -3
        self.assertEqual(-1, VE2I5G("15/1", victoires, defaites_coeff))  # -0.6 -> -1
        self.assertEqual(1, VE2I5G("15/2", victoires, defaites_coeff))   # 0.5 -> 1

        # Un WO compte pour les victoires mais pas pour les défaites
        self.assertEqual(1, VE2I5G("15", [("15", True, 1)], []))  # Victoire WO
        self.assertEqual(0, VE2I5G("15", [], [("15", True, 1)]))  # Défaite WO

    def test_nbVictoiresComptant(self):
        self.assertEqual(6, nbVictoiresComptant("30/1", "M", -1))
        self.assertEqual(7, nbVictoiresComptant("30/1", "M", 0))
        self.assertEqual(8, nbVictoiresComptant("30/1", "M", 5))
        self.assertEqual(12, nbVictoiresComptant("30/1", "M", 25))

        self.assertEqual(8, nbVictoiresComptant("15/1", "M", -1))
        self.assertEqual(9, nbVictoiresComptant("15/1", "M", 0))
        self.assertEqual(10, nbVictoiresComptant("15/1", "M", 8))

        self.assertEqual(11, nbVictoiresComptant("1/6", "M", -100))  # Cas de sanction géré distinctement
        self.assertEqual(8, nbVictoiresComptant("1/6", "M", -41))
        self.assertEqual(9, nbVictoiresComptant("1/6", "M", -40))
        self.assertEqual(10, nbVictoiresComptant("1/6", "M", -25))
        self.assertEqual(11, nbVictoiresComptant("1/6", "M", -1))
        self.assertEqual(17, nbVictoiresComptant("1/6", "M", 41))

        self.assertEqual(19, nbVictoiresComptant("-15", "M", -100))  # Cas de sanction géré distinctement
        self.assertEqual(14, nbVictoiresComptant("-15", "M", -81))
        self.assertEqual(19, nbVictoiresComptant("-15", "M", -1))
        self.assertEqual(26, nbVictoiresComptant("-15", "M", 45))

        self.assertEqual(17, nbVictoiresComptant("-15", "F", -100))  # Cas de sanction géré distinctement
        self.assertEqual(12, nbVictoiresComptant("-15", "F", -81))
        self.assertEqual(17, nbVictoiresComptant("-15", "F", -1))
        self.assertEqual(24, nbVictoiresComptant("-15", "F", 45))


if __name__ == '__main__':
    unittest.main()
