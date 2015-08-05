#!/usr/bin/python
# -*- coding: utf8 -*-
import unittest
from unicode_col import unicode_dict, unicode_defaultdict

class TestUnicodeDict(unittest.TestCase):
    def setUp(self):
        self.empty = unicode_dict()
        self.withdata = unicode_dict({'ábc':1, 'd':2})
        self.compdata = unicode_dict({'ábc':1, 'd':2},comparison_level=3)

    def test_comparison(self):
        self.assertNotEqual(self.withdata, self.compdata)
        self.assertNotEqual(self.withdata, self.empty)

    def test_len(self):
        self.assertEqual(len(self.withdata), 2)
        self.assertEqual(len(self.compdata), 2)
        self.assertEqual(len(self.empty), 0)

    def test_in(self):
        self.assertNotIn('abc', self.compdata)
        self.assertIn('abc', self.withdata)
        self.assertNotIn('abc', self.empty)

    def test_del(self):
        del self.withdata['abc']
        self.assertNotIn('abc', self.withdata)
        self.assertEqual(len(self.withdata), 1)

    def test_copy(self):
        test = self.empty.copy()
        self.assertNotEqual(id(self.empty), id(test))
        self.assertEqual(self.empty, test)
        test = self.compdata.copy()
        self.assertNotEqual(id(self.compdata), id(test))
        self.assertEqual(self.compdata, test)

    def test_copy_advanced(self):
        test = self.empty.copy()
        del self.withdata['abc']
        # update copy the values but use the original comp_level and locale
        test.update(self.compdata)
        self.assertNotEqual(self.empty, test)
        self.assertNotEqual(self.empty, self.compdata)
        del test['abc']
        self.assertEqual(test, self.withdata)
        test.clear()
        self.assertEqual(self.empty, test)

    def test_comparison(self):
        test = unicode_dict({'abc':1, 'd':2})
        self.assertEqual(test, self.withdata)

    def test_copy_constructor(self):
        test = unicode_dict(self.compdata,comparison_level=self.withdata.comparison_level)
        self.assertNotEqual(self.compdata, test)
        self.assertEqual(self.withdata, test)
        self.assertIn('abc', test)
        

    def test_iterators(self):
        tupl = [('ábc',1), ('d',2)]
        self.assertEqual(set(self.withdata), set(i for i,_ in tupl))
        self.assertEqual(set(self.withdata.keys()), set(i for i,_ in tupl))
        self.assertEqual(set(self.withdata.iterkeys()), set(i for i,_ in tupl))
        self.assertEqual(set(self.withdata.values()), set(i for _,i in tupl))
        self.assertEqual(set(self.withdata.itervalues()), set(i for _,i in tupl))
        self.assertEqual(set(self.withdata.items()), set(i for i in tupl))
        self.assertEqual(set(self.withdata.iteritems()), set(i for i in tupl))

    def test_pickling(self) :
        import pickle

        self.assertEqual(self.withdata, pickle.loads(pickle.dumps(self.withdata)))
        self.assertEqual(self.compdata, pickle.loads(pickle.dumps(self.compdata)))
        self.assertNotEqual(self.withdata, pickle.loads(pickle.dumps(self.compdata)))
        self.assertNotEqual(self.compdata, pickle.loads(pickle.dumps(self.withdata)))
        
        withdata = pickle.loads(pickle.dumps(self.withdata))
        self.assertIn('abc', withdata)

    def test_pop_exc(self):
        self.assertEqual(self.withdata.pop('abc'), 1)
        
        with self.assertRaises(KeyError) as cm:
            self.withdata.pop('abc')
        self.assertEqual(cm.exception.args[0], 'abc')

        with self.assertRaises(KeyError) as cm:
            self.withdata.pop('ábc')
        self.assertEqual(cm.exception.args[0], 'ábc')

        self.assertEqual(self.withdata.pop('abc',3), 3)

    def test_setdefault(self):
        self.withdata.pop('abc')
        self.assertEqual(self.withdata.setdefault('abc',2), 2)
        self.assertEqual(self.compdata.setdefault('abc',2), 2)
        self.assertEqual(len(self.withdata),2)
        self.assertEqual(len(self.compdata),3)

        self.assertEqual(self.withdata.setdefault('abc',4), 2)
        self.assertEqual(self.compdata.setdefault('abc',4), 2)
        self.assertEqual(self.withdata.setdefault('ábc',4), 2)
        self.assertEqual(self.compdata.setdefault('ábc',4), 1)
        self.assertEqual(len(self.withdata),2)
        self.assertEqual(len(self.compdata),3)


    def test_popitem(self):
        t = []
        t+= [self.withdata.popitem()]
        t+= [self.withdata.popitem()]
        
        with self.assertRaises(KeyError) as cm:
            t+= [self.withdata.popitem()]

        for i in [('ábc',1), ('d',2)]:
            self.assertIn(i,t)

    def test_compvalue(self):
        self.withdata['abc'] = 2
        self.assertEqual(self.withdata['ábc'], 2)

    def test_case_sensitive(self):
        csdata   = unicode_dict([('ábc',1), ('d',2)], case_sensitive = True)
        self.assertTrue(csdata.case_sensitive)
        self.assertFalse(self.withdata.case_sensitive)

        self.assertNotEqual(self.withdata,csdata)

        self.assertIn('abc', self.withdata)
        self.assertIn('Abc', self.withdata)
        self.assertIn('abc', csdata)
        self.assertNotIn('Abc', csdata)

        csdata['Abc'] = 4
        self.withdata['Abc'] = 4

        self.assertEqual(self.withdata['abc'], self.withdata['Abc'])
        self.assertEqual(self.withdata['ábc'], 4)
        
        self.assertNotEqual(csdata['abc'], csdata['Abc'])
        self.assertEqual(csdata['ábc'], 1)
        self.assertEqual(csdata['Abc'], 4)
        self.assertEqual(csdata['Ábc'], 4)

        cidata = unicode_dict(csdata, case_sensitive=False) #explicit casting to case insensitive
        self.assertNotEqual(cidata, csdata)

        self.assertNotEqual(len(cidata), len(csdata))
        
        self.assertEqual(len(cidata), 2)
        self.assertEqual(len(csdata), 3)

        self.assertTrue(cidata['abc'] == 1 or cidata['abc'] == 4) # casting down doesn't guarantee the result

#UnicodeDefaultDict
class TestUnicodeDefaultDict(unittest.TestCase):
    def test_int(self):
        udict = unicode_defaultdict(int)

        self.assertEqual(udict[1],0)
        self.assertEqual(udict['a'], 0)
        udict['à'] += 1
        self.assertEqual(udict['a'], 1)
        self.assertEqual(udict['à'], 1)
    
    def test_obj(self):
        class test(object):
            def __init__(self):
                self.val = 0

        udict = unicode_defaultdict(test)

        self.assertEqual(udict[1].val, 0)
        self.assertEqual(udict['a'].val, 0)
        udict['à'].val = 1
        self.assertEqual(udict['a'].val, 1)
        self.assertEqual(udict['à'].val, 1)


### MAIN ###
if __name__ == '__main__':
    unittest.main()
