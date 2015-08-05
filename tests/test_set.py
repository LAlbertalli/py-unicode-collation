#!/usr/bin/python
# -*- coding: utf8 -*-
import unittest
from unicode_col import unicode_set

class TestUnicodeSet(unittest.TestCase):
    def setUp(self):
        self.test_set_a = [u'ábc', u'abc', u'Straße', u'echo', u'peña', u'pena']
        self.test_set_b = [u'àbc', u'Straße', u'live', u'xkcd', u'äbc', u'ábc']
        self.test_set_c = [u'ÀBC', u'Live', 'abc']
        self.a = unicode_set(self.test_set_a)
        self.b = unicode_set(self.test_set_b)
        self.a3 = unicode_set(self.test_set_a, comparison_level=3)
        self.b3 = unicode_set(self.test_set_b, comparison_level=3)

    def test_create(self):
        a = unicode_set(self.test_set_a)
        self.assertEqual(len(a), 4)
        
        b = unicode_set(self.test_set_b)
        self.assertEqual(len(b), 4)
        
        c = unicode_set(self.test_set_c)
        self.assertEqual(len(c), 2)
        
    def test_create_collations(self):
        an = unicode_set(self.test_set_a,locale = 'ES_ES')
        self.assertEqual(len(an), 5)

        cc = unicode_set(self.test_set_c,case_sensitive = True)
        self.assertEqual(len(cc), 3)

        a3 = unicode_set(self.test_set_a, comparison_level=3)
        self.assertEqual(len(a3), len(self.test_set_a))

        b3 = unicode_set(self.test_set_b, comparison_level=3)
        self.assertEqual(len(b3), len(self.test_set_b))

    def test_contains(self):
        self.assertIn('abc', self.a)
        self.assertIn('abc', self.a)
        self.assertIn('abc', self.b)
        self.assertNotIn('abc', self.b3)
        self.assertIn('live', self.b)
        self.assertNotIn('live', self.a)
        self.assertIn('äbc', self.b3)
        self.assertIn('Straße', self.a)
        self.assertIn('Strasse', self.a)
        self.assertIn('Straße', self.a3)
        self.assertNotIn('Strasse', self.a3)


    def test_add(self):
        self.a.add('äbc')
        self.assertEqual(len(self.a), 4)
        self.assertIn('äbc', self.a)

        self.a3.add('äbc')
        self.assertEqual(len(self.a3), 7)
        self.assertIn('äbc', self.a3)

        self.a.add('máin')
        self.assertEqual(len(self.a), 5)
        self.assertIn('máin', self.a)

    def test_remove(self):
        self.a.add('äbc')
        self.a3.add('äbc')
        self.a.add('máin')

        self.a.remove('äbc')
        self.assertEqual(len(self.a), 4)
        self.assertNotIn('äbc', self.a)

        self.a3.remove('äbc')
        self.assertEqual(len(self.a3), 6)
        self.assertNotIn('äbc', self.a3)

        self.a.remove('máin')
        self.assertEqual(len(self.a), 3)
        self.assertNotIn('máin', self.a)

        self.a.remove('èchó')
        self.assertEqual(len(self.a), 2)
        self.assertNotIn('echo', self.a)

        with self.assertRaises(KeyError) as cm:
            self.a.remove('echo')

        with self.assertRaises(KeyError) as cm:
            self.a3.remove('èchó')

        self.a3.discard('èchó')
        
    def test_iterators(self):
        for i in self.a3:
            self.assertIn(i, self.test_set_a)

        for i in self.a:
            self.assertIn(i, self.test_set_a)

        for i in self.a:
            self.assertIn(i, set([u'abc', u'Straße', u'echo', u'pena']))

    def test_pickle(self):
        import pickle
        a_c = pickle.loads(pickle.dumps(self.a))
        for i in a_c:
            self.assertIn(i, set([u'abc', u'Straße', u'echo', u'pena']))

    def test_copy(self):
        a_c = self.a.copy()
        for i in a_c:
            self.assertIn(i, set([u'abc', u'Straße', u'echo', u'pena']))

    def test_equality(self):
        a_c = self.a.copy()
        # Don't use assert(Not)Equal, testing the operators
        self.assertFalse(not a_c == self.a)
        self.assertFalse(a_c != self.a)
        self.assertFalse(self.a == self.a3)

        self.assertFalse(self.a == self.b)
        self.assertFalse(self.a == self.test_set_a)
        self.assertFalse(self.a == set(self.test_set_a))

    def test_isdisjoint(self):
        self.assertTrue(self.a.isdisjoint(['c','ech',u'traße']))
        self.assertFalse(self.a.isdisjoint(['c','echo',u'traße']))

    def test_subset(self):
        self.assertFalse(self.a.issubset(['äbc']))
        self.assertTrue(self.a.issubset(self.test_set_a))
        self.assertFalse(self.a.issubset(self.test_set_b))
        self.assertTrue(self.a.issubset(self.test_set_a+["live"]))
        self.assertFalse(self.a <= unicode_set(['äbc']))
        self.assertTrue(self.a <= unicode_set(self.test_set_a))
        self.assertFalse(self.a < unicode_set(self.test_set_a))
        self.assertFalse(self.a <= unicode_set(self.test_set_b))
        self.assertTrue(self.a <= unicode_set(self.test_set_a+["live"]))
        self.assertTrue(self.a.issubset(self.a3))
        
        with self.assertRaises(TypeError):
            self.a <= self.a3
        with self.assertRaises(TypeError):
            self.a <= ['äbc']
        with self.assertRaises(TypeError):
            self.a <= set(['äbc'])

    def test_superset(self):
        self.assertTrue(self.a.issuperset(['äbc']))
        self.assertTrue(self.a.issuperset(self.test_set_a))
        self.assertFalse(self.a.issuperset(self.test_set_b))
        self.assertFalse(self.a.issuperset(self.test_set_a+["live"]))
        self.assertTrue(self.a >= unicode_set(['äbc']))
        self.assertTrue(self.a >= unicode_set(self.test_set_a))
        self.assertFalse(self.a > unicode_set(self.test_set_a))
        self.assertFalse(self.a >= unicode_set(self.test_set_b))
        self.assertFalse(self.a >= unicode_set(self.test_set_a+["live"]))
        self.assertTrue(self.a.issuperset(self.a3))
        
        with self.assertRaises(TypeError) as cm:
            self.a >= self.a3
        with self.assertRaises(TypeError) as cm:
            self.a >= ['äbc']
        with self.assertRaises(TypeError) as cm:
            self.a >= set(['äbc'])

    def test_union(self):
        x = self.a.union(self.b)
        self.assertEqual(len(x), 6)
        for i in x:
            self.assertIn(i, [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc'])

        x = self.a | self.b
        self.assertEqual(len(x), 6)
        for i in x:
            self.assertIn(i, [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc'])

        x = self.a.copy()
        x.update(self.b)
        self.assertEqual(len(x), 6)
        for i in x:
            self.assertIn(i, [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc'])

        x = self.a.copy()
        x |= self.b
        self.assertEqual(len(x), 6)
        for i in x:
            self.assertIn(i, [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc'])

        with self.assertRaises(TypeError) as cm:
            self.a | self.test_set_b
        
        with self.assertRaises(TypeError) as cm:
            self.a | self.a3
        
        with self.assertRaises(TypeError) as cm:
            self.a |= self.test_set_b
        
        with self.assertRaises(TypeError) as cm:
            self.a |= self.a3
        
    def test_intersection(self):
        x = self.a.intersection(self.b)
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'abc', u'Straße'])

        x = self.a & self.b
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'abc', u'Straße'])

        x = self.a.copy()
        x.intersection_update(self.b)
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'abc', u'Straße'])

        x = self.a.copy()
        x &= self.b
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'abc', u'Straße'])

        with self.assertRaises(TypeError) as cm:
            self.a & self.test_set_b
        
        with self.assertRaises(TypeError) as cm:
            self.a & self.a3
        
        with self.assertRaises(TypeError) as cm:
            self.a &= self.test_set_b
        
        with self.assertRaises(TypeError) as cm:
            self.a &= self.a3
        
    def test_difference(self):
        x = self.a.difference(self.b)
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena'])

        x = self.a - self.b
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena'])

        x = self.a.copy()
        x.difference_update(self.b)
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena'])

        x = self.a.copy()
        x -= self.b
        self.assertEqual(len(x), 2)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena'])

        with self.assertRaises(TypeError):
            self.a - self.test_set_b

        with self.assertRaises(TypeError):
            self.a - self.a3

        with self.assertRaises(TypeError):
            self.a -= self.test_set_b

        with self.assertRaises(TypeError):
            self.a -= self.a3

    def test_symmetric_difference(self):
        x = self.a.symmetric_difference(self.b)
        self.assertEqual(len(x), 4)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena', u'live', u'xkcd'])

        x = self.a ^ self.b
        self.assertEqual(len(x), 4)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena', u'live', u'xkcd'])

        x = self.a.copy()
        x.symmetric_difference_update(self.b)
        self.assertEqual(len(x), 4)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena', u'live', u'xkcd'])

        x = self.a.copy()
        x ^= self.b
        self.assertEqual(len(x), 4)
        for i in x:
            self.assertIn(i,[u'echo',  u'pena', u'live', u'xkcd'])

        with self.assertRaises(TypeError) as cm:
            self.a ^ self.test_set_b

        with self.assertRaises(TypeError) as cm:
            self.a ^ self.a3

        with self.assertRaises(TypeError) as cm:
            self.a ^= self.test_set_b

        with self.assertRaises(TypeError) as cm:
            self.a ^= self.a3

    def test_pop(self):
        x = self.a.pop()
        self.assertEqual(len(self.a), 3)
        self.assertIn(x, set([u'abc', u'Straße', u'echo', u'pena']))

        x = self.a.pop()
        self.assertEqual(len(self.a), 2)
        self.assertIn(x, set([u'abc', u'Straße', u'echo', u'pena']))

        x = self.a.pop()
        self.assertEqual(len(self.a), 1)
        self.assertIn(x, set([u'abc', u'Straße', u'echo', u'pena']))

        x = self.a.pop()
        self.assertEqual(len(self.a), 0)
        self.assertIn(x, set([u'abc', u'Straße', u'echo', u'pena']))

        with self.assertRaises(KeyError) as cm:
            x = self.a.pop()
        
    def test_clear(self):
        self.a3.clear()
        self.assertEqual(len(self.a3),0)
        for i in self.a3:
            self.fail()
        
        cc = unicode_set(self.test_set_c,case_sensitive = True)
        cc.clear()
        self.assertEqual(len(cc),0)
        for i in cc:
            self.fail()

        self.b.clear()
        self.assertEqual(len(self.b),0)
        for i in self.b:
            self.fail()

### MAIN ###
if __name__ == '__main__':
    unittest.main()
