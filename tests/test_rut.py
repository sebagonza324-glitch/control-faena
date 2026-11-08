"""Pruebas unitarias para la validación de RUT ficticios."""

import unittest

from src.utils.rut import RutInvalidoError, calcular_dv, normalizar_rut


class RutTests(unittest.TestCase):
    """Prueba el cálculo y la normalización de RUT."""

    def test_calcular_dv(self) -> None:
        """Calcula dígitos verificadores de ejemplos ficticios."""
        self.assertEqual(calcular_dv("11111111"), "1")
        self.assertEqual(calcular_dv("12345678"), "5")
        self.assertEqual(calcular_dv("6"), "K")

    def test_normalizar_rut_con_formatos_validos(self) -> None:
        """Normaliza formatos equivalentes de un RUT ficticio."""
        for rut in (
            "11.111.111-1",
            "11111111-1",
            "111111111",
            " 11.111.111 - 1 ",
        ):
            with self.subTest(rut=rut):
                self.assertEqual(normalizar_rut(rut), "11111111-1")

    def test_rechazar_rut_invalido(self) -> None:
        """Rechaza dígitos verificadores y entradas inválidas."""
        for rut in ("11.111.111-2", "abc", ""):
            with self.subTest(rut=rut):
                with self.assertRaises(RutInvalidoError):
                    normalizar_rut(rut)


if __name__ == "__main__":
    unittest.main()
