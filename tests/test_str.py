#!/usr/bin/python
# -*- coding: utf8 -*-
import unittest
from unicode_col import UnicodeStrFactory

class TestUnicodeDict(unittest.TestCase):
    def setUp(self):
        self.ger = u'Straße'
        self.acc = u'àèìòùáéíóúaeiouãẽĩõũâêîôû'
        self.noacc = u'aeiouaeiouaeiouaeiouaeiou'
        self.csacc = u'AEIOUaeiouaeiouaeiouaeiou'

        self.unicode_ci = UnicodeStrFactory()
        self.unicode_cs = UnicodeStrFactory(case_sensitive=True)
        self.unicode_st = UnicodeStrFactory(comparison_level=2, case_sensitive=True)

    def test_len(self):
        self.assertEqual(len(self.unicode_ci(self.acc)), 25)

    def test_char_exp(self):
        self.assertEqual(len(self.unicode_ci(self.ger)), 7)

    def test_comparison(self):
        # Use assert True to be sure the right comparison is used
        self.assertFalse(self.unicode_ci(self.ger) != self.unicode_ci(u'Straße'))
        self.assertFalse(self.unicode_ci(self.acc) != self.unicode_ci(self.noacc))
        self.assertTrue(self.unicode_ci(self.acc) == self.unicode_ci(self.noacc))
        
        self.assertFalse(self.unicode_ci(self.acc) != self.unicode_ci(self.csacc))
        self.assertTrue(self.unicode_ci(self.acc) == self.unicode_ci(self.csacc))

        self.assertFalse(self.unicode_cs(self.acc) != self.unicode_cs(self.noacc))
        self.assertTrue(self.unicode_cs(self.acc) == self.unicode_cs(self.noacc))
        
        self.assertFalse(self.unicode_cs(self.acc) == self.unicode_cs(self.csacc))
        self.assertTrue(self.unicode_cs(self.acc) != self.unicode_cs(self.csacc))

        self.assertTrue(self.unicode_cs(self.acc) < self.unicode_cs(self.csacc))
        self.assertTrue(self.unicode_cs(self.csacc) > self.unicode_cs(self.acc))

        self.assertFalse(self.unicode_st(self.acc) == self.unicode_st(self.noacc))
        self.assertTrue(self.unicode_st(self.acc) != self.unicode_st(self.noacc))
        
        self.assertFalse(self.unicode_st(self.acc) == self.unicode_st(self.csacc))
        self.assertTrue(self.unicode_st(self.acc) != self.unicode_st(self.csacc))

        # Accented letters compare higher (in strict mode) 
        # than not accented (despite of case)
        # The expected ordering (lower to higher no case) is:
        # a á à â ä ã 
        self.assertTrue(self.unicode_st(self.acc) > self.unicode_st(self.csacc))
        self.assertTrue(self.unicode_st(self.csacc) < self.unicode_st(self.acc))

        # Test different locales
        spanish_ci = UnicodeStrFactory(locale="es_ES")
        self.assertFalse(self.unicode_ci(u'ñ') != self.unicode_ci(u'n'))
        self.assertFalse(self.unicode_st(u'ñ') == self.unicode_st(u'n'))
        self.assertFalse(spanish_ci(u'ñ') == spanish_ci(u'n'))

    def test_hash(self):
        # Check it plays well with __hash__ (use dict)
        # Consider that == is no more commutative when
        # Used between different collations ((a == b) != (b == a))
        a={}
        a[self.unicode_ci(self.acc)] = 1
        
        self.assertEqual(a[self.unicode_ci(self.noacc)], 1)
        with self.assertRaises(KeyError) as cm:
            a[self.unicode_cs(self.noacc)]
        with self.assertRaises(KeyError) as cm:
            a[self.unicode_st(self.noacc)]
        self.assertEqual(a[self.unicode_ci(self.csacc)], 1)

        with self.assertRaises(KeyError) as cm:
            a[self.unicode_cs(self.csacc)]
        with self.assertRaises(KeyError) as cm:
            a[self.unicode_st(self.csacc)]
        
        a[self.unicode_ci(self.csacc)] = 2
        self.assertEqual(a[self.unicode_ci(self.acc)], 2)

        a[self.unicode_ci(self.noacc)] = 3
        self.assertEqual(a[self.unicode_ci(self.acc)], 3)

        self.assertIn(self.unicode_ci(self.acc),a)
        self.assertIn(self.unicode_ci(self.noacc),a)
        self.assertIn(self.unicode_ci(self.csacc),a)

    def test_in(self):
        self.assertIn('ss', self.unicode_ci(self.ger))
        self.assertIn('AEIOU', self.unicode_ci(self.acc))
        self.assertNotIn('AEIOU', self.unicode_cs(self.acc))
        self.assertIn('AEIOU', self.unicode_cs(self.csacc))

    def test_find(self):
        # find and rfind / index and rindex use find so no test needed
        self.assertEqual(self.unicode_ci(self.ger).find('ss'), 4)
        self.assertEqual(self.unicode_ci(self.ger).rfind('ss'), 4)
        self.assertEqual(self.unicode_ci(self.acc).find('aeiou'), 0)
        self.assertEqual(self.unicode_ci(self.acc).rfind('aeiou'), 20)
        self.assertEqual(self.unicode_ci(self.acc).find('aeiou',3), 5)
        self.assertEqual(self.unicode_st(self.acc).find('aeiou'), 10)
        self.assertEqual(self.unicode_cs(self.csacc).rfind('AEIOU'), 0)

### MAIN ###
if __name__ == '__main__':
    unittest.main()
