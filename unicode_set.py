#!/usr/bin/python
# -*- coding: utf8 -*-
from icu import Collator, Locale, UCollAttribute, UCollAttributeValue
try:
    from thread import get_ident as _get_ident
except ImportError:
    from dummy_thread import get_ident as _get_ident

class unicode_set(set):
    '''Set that support unicode comparison as defined by icu (UCA)
    It uses a dict as the underlying storage instead of the built-in set
    despite the performance difference since it needs to keep anyway a mapping dict
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize a unicode set.  The signature is changed because the 
        kwargs are used to set the comparison details

        '''
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))

        if len(args) == 1 and isinstance(args[0],self.__class__):
            locale = args[0].locale if 'locale' not in kwargs else kwargs.pop('locale')
            comparison_level = args[0].comparison_level if 'comparison_level' \
                not in kwargs else kwargs.pop('comparison_level')
            case_sensitive = args[0].case_sensitive if 'case_sensitive' \
                not in kwargs else kwargs.pop('case_sensitive')
        else:
            locale = kwargs.pop('locale','en_US')
            comparison_level = max(0,min(3,kwargs.pop('comparison_level',0)))
            case_sensitive = kwargs.pop('case_sensitive', False)
        self.__locale = Locale(locale)
        self.__collator = Collator.createInstance(self.__locale)
        self.__collator.setStrength(comparison_level)
        self.__collator.setAttribute(UCollAttribute.CASE_LEVEL,
            UCollAttributeValue.ON if case_sensitive else UCollAttributeValue.OFF)
        self.__values = {} # set implementation
        if len(args) == 1:
            vals = args[0]
            for val in vals:
                self.add(val)

    @property
    def locale(self):
        return self.__locale.getName()

    @property
    def comparison_level(self):
        return self.__collator.getStrength()

    @property
    def case_sensitive(self):
        return self.__collator.getAttribute(UCollAttribute.CASE_LEVEL) == UCollAttributeValue.ON

    def __in_key(self,key):
        return self.__collator.getSortKey(key) if isinstance(key,basestring) else key

    def __in_equality(self,other):
        return self.locale == other.locale and\
            self.comparison_level == other.comparison_level and \
            self.case_sensitive == other.case_sensitive

    # LA: Code for EC

    # def get_stored_version(self, val):
    #     ''' Return the stored version of val if exists

    #     Raise an exception if the key is not in the set
    #     '''
    #     try:
    #         return self.__values[self.__in_key(val)]
    #     except KeyError:
    #         raise KeyError("The key %s is not in the set"%val)

    def add(self,val):
        '''Add an element to a set.
        
        This has no effect if the element is already present.
        '''
        self.__values[self.__in_key(val)] = val

    def clear(self):
        '''Remove all elements from this set.
        '''
        self.__values.clear()
    
    def copy(self):
        '''Return a shallow copy of a set.
        '''
        return self.__class__(self)
    
    def difference(self, *args):
        '''Return the difference of two or more sets as a new set.
        
        (i.e. all elements that are in this set but not the others.)
        '''
        ret = self.__class__(self)
        ret.difference_update(*args)

        return ret

    def difference_update(self, *args):
        '''Remove all elements of another set from this set.
        '''
        if len(args) > 1:
            for arg in args:
                self.difference_update(arg)
        else:
            arg = args[0]
            if isinstance(arg,self.__class__) and self.__in_equality(arg):
                for i in arg.__values.iterkeys():
                    if i in self.__values:
                        del self.__values[i]
            else:
                for i in arg:
                    i = self.__in_key(i)
                    if i in self.__values:
                        del self.__values[i]

    def discard(self,val):
        '''Remove an element from a set if it is a member.
        
        If the element is not a member, do nothing.
        '''
        try:
            self.remove(val)
        except KeyError:
            pass

    def intersection(self,*args):
        '''Return the intersection of two or more sets as a new set.
        
        (i.e. elements that are common to all of the sets.)
        '''
        ret = self.__class__(self)
        ret.intersection_update(*args)
        
        return ret

    def intersection_update(self,*args):
        '''Update a set with the intersection of itself and another.
        '''
        if len(args) > 1:
            for arg in args:
                self.intersection_update(arg)
        else:
            if isinstance(args[0],self.__class__) and self.__in_equality(args[0]):
                arg = args[0]
            else:
                arg = self.__class__(args[0],
                    locale = self.locale, 
                    case_sensitive = self.case_sensitive,
                    comparison_level = self.comparison_level)
            for k,v in self.__values.items():
                if v not in arg:
                    del self.__values[k]

    def isdisjoint(self,other):
        '''Return True if two sets have a null intersection.
        '''
        return len(self.intersection(other)) == 0

    def issubset(self,other):
        '''Report whether another set contains this set.
        '''
        return self.__class__(other,
            locale = self.locale, 
            case_sensitive = self.case_sensitive, 
            comparison_level = self.comparison_level).issuperset(self)

    def issuperset(self,other):
        '''Report whether this set contains another set.
        '''
        return len(self.__class__(other, 
            locale = self.locale, 
            case_sensitive = self.case_sensitive, 
            comparison_level = self.comparison_level)) == len(self.intersection(other))


    def pop(self):
        '''Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.
        '''
        return self.__values.popitem()[1]

    def remove(self,val):
        '''Remove an element from a set; it must be a member.
        
        If the element is not a member, raise a KeyError.
        '''
        del self.__values[self.__in_key(val)]

    def symmetric_difference(self,other):
        '''Return the symmetric difference of two sets as a new set.
        
        (i.e. all elements that are in exactly one of the sets.)
        '''
        ret = self.__class__(self)
        ret.update(other)
        ret.difference_update(self.intersection(other))

        return ret

    def symmetric_difference_update(self,other):
        '''Update a set with the symmetric difference of itself and another.
        '''
        bck = self.__class__(self)
        self.update(other)
        self.difference_update(bck.intersection(other))

    def union(self,*others):
        '''Return the union of sets as a new set.
        
        (i.e. all elements that are in either set.)
        '''
        ret = self.__class__(self)
        ret.update(*others)

        return ret

    def update(self,*others):
        '''Update a set with the union of itself and others.
        '''
        for other in others:
            if isinstance(other,self.__class__) and self.__in_equality(other):
                self.__values.update(other.__values)
            else:
                self.__values.update({self.__in_key(i):i for i in other})

    def __and__(self,other):
        '''x.__and__(y) <==> x&y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.intersection(other)

    def __contains__(self,obj):
        '''x.__contains__(y) <==> y in x.
        '''
        return self.__in_key(obj) in self.__values

    def __eq__(self,other):
        '''x.__eq__(y) <==> x==y
        '''
        return isinstance(other,self.__class__) and self.__in_equality(other) \
            and set(self.__values.keys()) == set(other.__values.keys())

    def __ge__(self,other):
        '''x.__ge__(y) <==> x>=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.issuperset(other)

    def __gt__(self,other):
        '''x.__gt__(y) <==> x>y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.issuperset(other) and self != other

    def __iand__(self,other):
        '''x.__iand__(y) <==> x&=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        self.intersection_update(other)
        return self

    def __ior__(self,other):
        '''x.__ior__(y) <==> x|=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")
        self.update(other)
        return self

    def __isub__(self,other):
        '''x.__isub__(y) <==> x-=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        self.difference_update(other)
        return self

    def __iter__(self):
        '''x.__iter__() <==> iter(x)
        '''
        return self.__values.itervalues()

    def __ixor__(self,other):
        '''x.__ixor__(y) <==> x^=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        self.symmetric_difference_update(other)
        return self

    def __le__(self,other):
        '''x.__le__(y) <==> x<=y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.issubset(other)

    def __len__(self):
        '''x.__len__() <==> len(x)
        '''
        return len(self.__values)

    def __lt__(self,other):
        '''x.__lt__(y) <==> x<y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.issubset(other) and self != other

    def __ne__(self,other):
        '''x.__ne__(y) <==> x!=y
        '''
        return not self == other

    def __or__(self,other):
        '''x.__or__(y) <==> x|y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.union(other)

    def __rand__(self,other):
        '''x.__rand__(y) <==> y&x
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return other & self

    def __repr__(self, _repr_running={}):
        '''x.__repr__() <==> repr(x)
        '''
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.__values.values())
        finally:
            del _repr_running[call_key]

    def __ror__(self,other):
        '''x.__ror__(y) <==> y|x
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return other | self

    def __rsub__(self,other):
        '''x.__rsub__(y) <==> y-x
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return other - self

    def __rxor__(self,other):
        '''x.__rxor__(y) <==> y^x
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return other ^ self

    def __sizeof__(self):
        '''S.__sizeof__() -> size of S in memory, in bytes
        '''
        return self.__value.__sizeof__()

    def __sub__(self,other):
        '''x.__sub__(y) <==> x-y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.difference(other)

    def __xor__(self,other):
        '''x.__xor__(y) <==> x^y
        '''
        if not isinstance(other,self.__class__):
            raise TypeError("can only compare to a unicode_set")

        if not self.__in_equality(other):
            raise TypeError("can only compare to a unicode_set with the same caracteristic")

        return self.symmetric_difference(other)

    def __reduce__(self):
        inst_dict = vars(self).copy()
        for k in vars(unicode_set()):
            inst_dict.pop(k, None)
        inst_dict.update({
            'locale':self.locale, 
            'comparison_level':self.comparison_level,
            'case_sensitive': self.case_sensitive
            })
        return (unicode_set_from_data, ([self.__values.values()],inst_dict))

def unicode_set_from_data(args,kwargs = None):
    if kwargs is None:
        kwargs = {}
    fwd_kwargs = {i:kwargs.pop(i) for i in ('locale', 'comparison_level', 'case_sensitive') if i in kwargs}
    r = unicode_set(*args,**fwd_kwargs)
    for i,v in kwargs.iteritems():
        setattr(r,i,v)
    return r

#### Tests ####
if __name__ == '__main__':
    test_set_a = [u'ábc', u'abc', u'Straße', u'echo', u'peña', u'pena']
    test_set_b = [u'àbc', u'Straße', u'live', u'xkcd', u'äbc', u'ábc']
    test_set_c = [u'ÀBC', u'Live', 'abc']

    # test_set = [u'', u'', u'', u'', u'', u'', u'', u'', u'']

    #Test creation, collation and len

    a = unicode_set(test_set_a)
    if len(a) != 4:
        raise Exception
    
    b = unicode_set(test_set_b)
    if len(b) != 4:
        raise Exception
    
    c = unicode_set(test_set_c)
    if len(c) != 2:
        raise Exception
    
    an = unicode_set(test_set_a,locale = 'ES_ES')
    if len(an) != 5:
        raise Exception

    cc = unicode_set(test_set_c,case_sensitive = True)
    if len(cc) != 3:
        raise Exception

    a3 = unicode_set(test_set_a, comparison_level=3)
    if len(a3) != len(test_set_a):
        raise Exception

    b3 = unicode_set(test_set_b, comparison_level=3)
    if len(b3) != len(test_set_b):
        raise Exception

    #Test contains
    if not 'abc' in a:
        raise Exception

    if not 'abc' in a:
        raise Exception

    if not 'abc' in b:
        raise Exception

    if 'abc' in b3:
        raise Exception

    if not 'live' in b:
        raise Exception

    if 'live' in a:
        raise Exception

    if not 'äbc' in b3:
        raise Exception

    if not 'Straße' in a:
        raise Exception

    if not 'Strasse' in a:
        raise Exception

    if not 'Straße' in a3:
        raise Exception

    if 'Strasse' in a3:
        raise Exception

    # Test add
    a.add('äbc')
    if len(a) != 4:
        raise Exception
    if 'äbc' not in a:
        raise Exception

    a3.add('äbc')
    if len(a3) != 7:
        raise Exception
    if 'äbc' not in a3:
        raise Exception

    a.add('máin')
    if len(a) != 5:
        raise Exception
    if 'máin' not in a:
        raise Exception

    # Test remove
    a.remove('äbc')
    if len(a) != 4:
        raise Exception
    if 'äbc' in a:
        raise Exception

    a3.remove('äbc')
    if len(a3) != 6:
        raise Exception
    if 'äbc' in a3:
        raise Exception

    a.remove('máin')
    if len(a) != 3:
        raise Exception
    if 'máin' in a:
        raise Exception

    a.remove('èchó')
    if len(a) != 2:
        raise Exception
    if 'echo' in a:
        raise Exception

    try:
        a.remove('echo')
    except KeyError:
        pass
    else:
        raise Exception

    try:
        a3.remove('èchó')
    except KeyError:
        pass
    else:
        raise Exception

    a3.discard('èchó')
    
    #Test iter and content
    a = unicode_set(test_set_a)
    a3 = unicode_set(test_set_a, comparison_level=3)

    for i in a3:
        if i not in test_set_a:
            raise Exception

    for i in a:
        if i not in test_set_a:
            raise Exception

    for i in a:
        if i not in set([u'abc', u'Straße', u'echo', u'pena']):
            raise Exception

    # pickle and copy
    import pickle
    a_c = pickle.loads(pickle.dumps(a))
    for i in a_c:
        if i not in set([u'abc', u'Straße', u'echo', u'pena']):
            raise Exception

    a_c = a.copy()
    for i in a_c:
        if i not in set([u'abc', u'Straße', u'echo', u'pena']):
            raise Exception

    # Equality
    if not a_c == a:
        raise Exception
    if a_c != a:
        raise Exception
    if a == a3:
        raise Exception

    if a == b:
        raise Exception

    if a == test_set_a:
        raise Exception

    if a == set(test_set_a):
        raise Exception

    # isdisjoint
    if not a.isdisjoint(['c','ech',u'traße']):
        raise Exception

    if a.isdisjoint(['c','echo',u'traße']):
        raise Exception

    # subset
    if a.issubset(['äbc']):
        raise Exception

    if not a.issubset(test_set_a):
        raise Exception

    if a.issubset(test_set_b):
        raise Exception

    if not a.issubset(test_set_a+["live"]):
        raise Exception

    if a <= unicode_set(['äbc']):
        raise Exception

    if not a <= unicode_set(test_set_a):
        raise Exception

    if a < unicode_set(test_set_a):
        raise Exception

    if a <= unicode_set(test_set_b):
        raise Exception

    if not a <= unicode_set(test_set_a+["live"]):
        raise Exception

    if not a.issubset(a3):
        raise Exception

    try:
        a <= a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a <= ['äbc']
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a <= set(['äbc'])
    except TypeError:
        pass
    else:
        raise Exception

    # superset
    if not a.issuperset(['äbc']):
        raise Exception

    if not a.issuperset(test_set_a):
        raise Exception

    if a.issuperset(test_set_b):
        raise Exception

    if a.issuperset(test_set_a+["live"]):
        raise Exception

    if not a >= unicode_set(['äbc']):
        raise Exception

    if not a >= unicode_set(test_set_a):
        raise Exception

    if a > unicode_set(test_set_a):
        raise Exception

    if a >= unicode_set(test_set_b):
        raise Exception

    if a >= unicode_set(test_set_a+["live"]):
        raise Exception

    if not a.issuperset(a3):
        raise Exception

    try:
        a >= a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a >= ['äbc']
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a >= set(['äbc'])
    except TypeError:
        pass
    else:
        raise Exception

    # union
    x = a.union(b)
    if len(x) != 6:
        raise Exception
    for i in x:
        if i not in [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc']:
            raise Exception

    x = a | b
    if len(x) != 6:
        raise Exception
    for i in x:
        if i not in [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc']:
            raise Exception

    x = a.copy()
    x.update(b)
    if len(x) != 6:
        raise Exception
    for i in x:
        if i not in [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc']:
            raise Exception

    x = a.copy()
    x |= b
    if len(x) != 6:
        raise Exception
    for i in x:
        if i not in [u'echo', u'pena', u'Straße', u'live', u'xkcd', u'ábc']:
            raise Exception

    try:
        a | test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a | a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a |= test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a |= a3
    except TypeError:
        pass
    else:
        raise Exception

    # intersection
    x = a.intersection(b)
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'abc', u'Straße']:
            raise Exception

    x = a & b
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'abc', u'Straße']:
            raise Exception

    x = a.copy()
    x.intersection_update(b)
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'abc', u'Straße']:
            raise Exception

    x = a.copy()
    x &= b
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [ u'abc', u'Straße']:
            raise Exception

    try:
        a & test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a & a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a &= test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a &= a3
    except TypeError:
        pass
    else:
        raise Exception

    # difference
    x = a.difference(b)
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena']:
            raise Exception

    x = a - b
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena']:
            raise Exception

    x = a.copy()
    x.difference_update(b)
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena']:
            raise Exception

    x = a.copy()
    x -= b
    if len(x) != 2:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena']:
            raise Exception

    try:
        a - test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a - a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a -= test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a -= a3
    except TypeError:
        pass
    else:
        raise Exception

    # symmetric difference
    x = a.symmetric_difference(b)
    if len(x) != 4:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena', u'live', u'xkcd']:
            raise Exception

    x = a ^ b
    if len(x) != 4:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena', u'live', u'xkcd']:
            raise Exception

    x = a.copy()
    x.symmetric_difference_update(b)
    if len(x) != 4:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena', u'live', u'xkcd']:
            raise Exception

    x = a.copy()
    x ^= b
    if len(x) != 4:
        raise Exception
    for i in x:
        if i not in [u'echo',  u'pena', u'live', u'xkcd']:
            raise Exception

    try:
        a ^ test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a ^ a3
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a ^= test_set_b
    except TypeError:
        pass
    else:
        raise Exception

    try:
        a ^= a3
    except TypeError:
        pass
    else:
        raise Exception

    # pop
    if len(a) != 4:
        raise Exception

    x = a.pop()
    if len(a) != 3:
        raise Exception
    if x not in set([u'abc', u'Straße', u'echo', u'pena']): 
        raise Exception

    x = a.pop()
    if len(a) != 2:
        raise Exception
    if x not in set([u'abc', u'Straße', u'echo', u'pena']): 
        raise Exception

    x = a.pop()
    if len(a) != 1:
        raise Exception
    if x not in set([u'abc', u'Straße', u'echo', u'pena']): 
        raise Exception

    x = a.pop()
    if len(a) != 0:
        raise Exception
    if x not in set([u'abc', u'Straße', u'echo', u'pena']): 
        raise Exception

    try:
        x = a.pop()
    except KeyError:
        pass
    else:
        raise Exception

    # clear
    if len(a3) != 6:
        raise Exception

    a3.clear()
    if len(a3) != 0:
        raise Exception
    for i in a3:
        raise Exception

    if len(cc) != 3:
        raise Exception

    cc.clear()
    if len(cc) != 0:
        raise Exception
    for i in cc:
        raise Exception

    if len(b) != 4:
        raise Exception

    b.clear()
    if len(b) != 0:
        raise Exception
    for i in b:
        raise Exception

    print "All test passed!"