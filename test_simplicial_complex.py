from math import inf
from unittest import TestCase

from simplicial_complex import SimplicialComplex, Simplex


class TestSimplicialComplex(TestCase):
    def test_add_simplex(self):
        sc = SimplicialComplex()
        sc.add_simplex(Simplex(0, 0, (0,)))
        self.assertEqual(len(sc.simplicies), 1)
        sc.add_simplex(Simplex(0, 0, (1,)))
        sc.add_simplex(Simplex(0, 1, (0, 1)))
        self.assertEqual(len(sc.simplicies), 3)

    def test_compute_boundary_matrix(self):
        sc = SimplicialComplex()
        sc.add_simplex(Simplex(0, 0, [0]))
        sc.add_simplex(Simplex(1, 0, [1]))
        sc.add_simplex(Simplex(2, 1, [0, 1]))
        sc.update_indexes()

        boundary_matrix = sc.compute_boundary_matrix()
        self.assertEqual(str(boundary_matrix).replace('\n', ''), "001001000")

    def test_get_barcode(self):
        sc = SimplicialComplex()
        sc.add_simplex(Simplex(0, 0, [0]))
        sc.add_simplex(Simplex(1, 0, [1]))
        sc.add_simplex(Simplex(2, 1, [0, 1]))
        sc.update_indexes()

        barcode = sc.get_extended_barcode()
        self.assertListEqual(barcode, [(0, 0, inf), (0, 1, 2)])

        sc = SimplicialComplex()
        sc.add_simplex(Simplex(0, 0, [0]))
        sc.add_simplex(Simplex(1, 0, [1]))
        sc.add_simplex(Simplex(2, 1, [0, 1]))
        sc.add_simplex(Simplex(3, 0, [2]))
        sc.add_simplex(Simplex(4, 1, [0, 2]))
        sc.add_simplex(Simplex(5, 0, [3]))
        sc.add_simplex(Simplex(6, 1, [1, 3]))
        sc.add_simplex(Simplex(8, 1, [2, 3]))
        sc.update_indexes()

        barcode = sc.get_extended_barcode()
        self.assertListEqual(barcode, [(0, 0, inf), (0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 8, inf)])
