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
        self.assertEqual("Top 40/Top 60", normalisation("N51", "H"))
        self.assertEqual("Top 60/Top 100", normalisation("N51", "F"))
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


if __name__ == '__main__':
    unittest.main()
