import unittest
from XPoint import XPoint
from XFigure import XFigure

class TestXPoint(unittest.TestCase):
    def test_point_equality(self):
        point1 = XPoint(1, 2, 3, 4, 5, 6)
        point2 = XPoint(1, 2, 3, 4, 5, 6)
        point3 = XPoint(6, 5, 4, 3, 2, 1)
        self.assertEqual(point1, point2)
        self.assertNotEqual(point1, point3)

    def test_point_hash(self):
        point1 = XPoint(1, 2, 3, 4, 5, 6)
        point2 = XPoint(1, 2, 3, 4, 5, 6)
        self.assertEqual(hash(point1), hash(point2))

class TestXFigure(unittest.TestCase):
    def setUp(self):
        self.figure = XFigure("TestFigure")
        self.point1 = XPoint(1, 2, 3, 4, 5, 6)
        self.point2 = XPoint(6, 5, 4, 3, 2, 1)

    def test_add_point(self):
        self.figure.add_point(self.point1)
        self.assertIn(self.point1, self.figure.points)

    def test_edit_point(self):
        self.figure.add_point(self.point1)
        self.figure.edit_point(self.point1, self.point2)
        self.assertIn(self.point2, self.figure.points)
        self.assertNotIn(self.point1, self.figure.points)

    def test_delete_point(self):
        self.figure.add_point(self.point1)
        self.figure.delete_point(self.point1)
        self.assertNotIn(self.point1, self.figure.points)

if __name__ == '__main__':
    unittest.main()
