Under MIT License, see LICENSE.txt
import unittest
import math as m
import RULEngine.Util.Vector


class TestVector(unittest.TestCase):

    def setUp(self):
        self.vector = RULEngine.Util.Vector.Vector()
        self.vector2 = RULEngine.Util.Vector.Vector(30, m.pi)
        self.vector3 = RULEngine.Util.Vector.Vector(30, m.pi)
        self.vector4 = RULEngine.Util.Vector.Vector(2016, m.pi/4)
        self.vector5 = RULEngine.Util.Vector.Vector(40, m.pi/2)

    def test_getlength(self):
        self.assertEqual(self.vector.length, 1.0)

    def test_setlength(self):
        self.vector.length = 10
        self.assertEqual(self.vector.length, 10)
        self.assertEqual(self.vector.x, 10)
        self.assertEqual(self.vector.y, 0)

    def test_getdirection(self):
        self.assertEqual(self.vector.direction, 0.0)

    def test_setdirection(self):
        self.vector.direction = m.pi
        self.assertEqual(self.vector.direction, m.pi)
        self.assertEqual(self.vector.x, -1)
        self.assertAlmostEqual(self.vector.y, 0, 10)

    def test_getx(self):
        self.assertEqual(self.vector.x, 1.0)

    def test_setx(self):
        self.vector.x = 123
        self.assertEqual(self.vector.x, 123)
        self.assertEqual(self.vector.length, 123)
        self.assertEqual(self.vector.direction, 0)

    def test_gety(self):
        self.assertEqual(self.vector.y, 0.0)

    def test_sety(self):
        self.vector.y = 456
        self.assertEqual(self.vector.y, 456)
        self.assertAlmostEqual(self.vector.length, 456.0010964899, 10)
        self.assertAlmostEqual(self.vector.direction, 1.56860334785, 10)

    def test_eqtrue(self):
        b00l = self.vector2 == self.vector3
        self.assertEqual(b00l, True)

    def test_eqfalse(self):
        b00l = self.vector == self.vector2
        self.assertEqual(b00l, False)

    def test_netrue(self):
        b00l = self.vector != self.vector2
        self.assertEqual(b00l, True)

    def test_nefalse(self):
        b00l = self.vector2 != self.vector3
        self.assertEqual(b00l, False)

    def test_addposition(self):
        p = RULEngine.Util.Position.Position()
        p2 = self.vector5 + p
        reference = RULEngine.Util.Position.Position(0, 40)
        self.assertAlmostEqual(p2.x, reference.x, 10)
        self.assertAlmostEqual(p2.y, reference.y, 10)

    def test_addpose(self):
        p = RULEngine.Util.Pose.Pose()
        p2 = self.vector4 + p
        reference = RULEngine.Util.Pose.Pose(RULEngine.Util.Position.Position(2016*m.cos(m.pi/4), 2016*m.sin(m.pi/4)), m.pi/4)
        self.assertAlmostEqual(p2.position.x, reference.position.x, 10)
        self.assertAlmostEqual(p2.position.y, reference.position.y, 10)
        self.assertAlmostEqual(p2.orientation, reference.orientation,10)

    def test_addvector(self):
        a = self.vector2 + self.vector5
        b = RULEngine.Util.Vector.Vector(m.sqrt(30**2 + 40**2), m.atan2(40, -30))
        self.assertEqual(a, b)

    def test_raddposition(self):
        p = RULEngine.Util.Position.Position()
        p2 = p + self.vector5
        reference = RULEngine.Util.Position.Position(0, 40)
        self.assertAlmostEqual(p2.x, reference.x, 10)
        self.assertAlmostEqual(p2.y, reference.y, 10)

    def test_raddpose(self):
        p = RULEngine.Util.Pose.Pose()
        p2 = p + self.vector4
        reference = RULEngine.Util.Pose.Pose(RULEngine.Util.Position.Position(2016*m.cos(m.pi/4), 2016*m.sin(m.pi/4)), m.pi/4)
        self.assertAlmostEqual(p2.position.x, reference.position.x, 10)
        self.assertAlmostEqual(p2.position.y, reference.position.y, 10)
        self.assertAlmostEqual(p2.orientation, reference.orientation,10)

    def test_iadd(self):
        self.vector += self.vector4
        self.assertEqual(self.vector, RULEngine.Util.Vector.Vector(2016.7072307456, 0.78504753898))

    def test_sub(self):
        a = self.vector5 - self.vector3
        self.assertEqual(a, RULEngine.Util.Vector.Vector(50, 0.9272952180))

    def test_sub2(self):
        a = self.vector5 - self.vector4
        self.assertEqual(a, RULEngine.Util.Vector.Vector(1987.9169545859, -2.3704230653))

    def test_subzero(self): #fatality, Subzero wins
        a = self.vector - self.vector
        self.assertEqual(a, RULEngine.Util.Vector.Vector(0, 0))

    def test_isub(self):
        self.vector5 -= self.vector4
        self.assertEqual(self.vector5, RULEngine.Util.Vector.Vector(1987.9169545859, -2.3704230653))

    def test_neg(self):
        self.assertEqual(-self.vector4, RULEngine.Util.Vector.Vector(2016, -m.pi/4))

    def test_mul(self):
        self.assertEqual(self.vector5*2, RULEngine.Util.Vector.Vector(80, m.pi/2))

    def test_mul0(self):
        self.assertEqual(self.vector5*0, RULEngine.Util.Vector.Vector(0, m.pi/2))

    def test_mulneg(self):
        self.assertEqual(self.vector3*-1, RULEngine.Util.Vector.Vector(30, -m.pi))

    def test_rmul(self):
        self.assertEqual(2*self.vector5, RULEngine.Util.Vector.Vector(80, m.pi/2))

    def test_imul(self):
        self.vector4 *= 8
        self.assertEqual(self.vector4, RULEngine.Util.Vector.Vector(16128, m.pi/4))

    def test_imul0(self):
        self.vector4 *= 0
        self.assertEqual(self.vector4, RULEngine.Util.Vector.Vector(0, m.pi/4))

    def test_imulneg(self):
        self.vector4 *= -2
        self.assertEqual(self.vector4, RULEngine.Util.Vector.Vector(4032, -m.pi/4))

    def test_str(self):
        string = str(self.vector)
        self.assertEqual(string, "(Length = 1.0, Direction = 0.0)")

    def test_dotperp(self):
        a = self.vector2.dot(self.vector5)
        self.assertEqual(round(a, 10), 0.0)

    def test_dot(self):
        a = self.vector4.dot(self.vector5)
        self.assertEqual(round(a, 10), 57021.0908348832)

    def test_dot2(self):
        a = self.vector2.dot(self.vector3)
        self.assertEqual(a, 900)

    def test_unit(self):
        u = self.vector2.unit()
        self.assertEqual(u.length, 1)
        self.assertEqual(u.direction, m.pi)

    def test_normalplus(self):
        n = self.vector.normal()
        self.assertEqual(n.length, 1)
        self.assertEqual(n.direction, m.pi/2)

    def test_normalminus(self):
        n = self.vector.normal(False)
        self.assertEqual(n.length, 1)
        self.assertEqual(n.direction, -m.pi/2)

    def test_normal2(self):
        n = self.vector4.normal()
        self.assertEqual(n.length, 1)
        self.assertEqual(n.direction, 3*m.pi/4)

    def test_getangle(self):
        a = self.vector3.getangle(self.vector4)
        self.assertEqual(a, 3*m.pi/4)

    def test_getanglereverse(self):
        a = self.vector4.getangle(self.vector3)
        self.assertEqual(a, 3*m.pi/4)


if __name__ == '__main__':
    unittest.main()
