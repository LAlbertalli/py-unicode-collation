from ..unicode_dict import unicode_defaultdict
from collections import Counter
from itertools import chain, repeat

class FreqCounter(object):
    class __v(object):
        __marker = object()
        def __init__(self,val = __marker):
            self.count = 0
            self.counter = Counter()
            if val is not self.__marker:
                self.add(val)
        
        def add(self,val):
            self.count += 1
            self.counter[val] += 1
        
        def rem(self,val):
            self.count -= 1
            self.counter[val] -= 1

        @property
        def value(self):
            return self.counter.most_common(1)[0][0]

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))

        if len(args) == 1 and isinstance(args[0],self.__class__):
            locale = args[0].locale if 'locale' not in kwargs else kwargs.pop('locale')
            comparison_level = args[0].comparison_level if 'comparison_level' \
                not in kwargs else kwargs.pop('comparison_level')
            case_sensitive = args[0].case_sensitive if 'case_sensitive' \
                not in kwargs else kwargs.pop('case_sensitive')
            vals = args[0].elements(dump = True)
        else:
            locale = kwargs.pop('locale','en_US')
            comparison_level = max(0,min(3,kwargs.pop('comparison_level',0)))
            case_sensitive = kwargs.pop('case_sensitive', False)
            vals = args[0] if len(args) == 1 else []

        self.__dict = unicode_defaultdict(
            self.__v,
            locale = locale,
            comparison_level = comparison_level,
            case_sensitive = case_sensitive,
            )
        
        for val in vals:
            self.add(val)

    def add(self,val):
        self.__dict[val].add(val)

    def rem(self, val):
        self.__dict[val].rem(val)

    def __getitem__(self, key):
        return self.__dict[key].count

    def elements(self,dump = False):
        if dump:
            return chain(*(i.counter.elements() for i in self.__dict.itervalues()))
        else:
            return chain(*(repeat(i.value, i.count) for i in self.__dict.itervalues()))

    def iteritems(self):
        return ((i.value,i.count) for i in self.__dict.itervalues())

    def items(self):
        return list(self.iteritems())

    def itervalues(self):
        for _,i in self.iteritems(): yield i 

    def values(self):
        return [i for _,i in self.iteritems()]

    def iterkeys(self):
        for i,_ in self.iteritems(): yield i

    def __iter__(self):
        return self.iterkeys()

    def keys(self):
        return [i for i,_ in self.iteritems()]

    __marker = object()

    def most_common(self, count = __marker):
        mc = sorted(self.iteritems(), key = lambda x:x[1], reverse = True)
        if count == self.__marker:
            return mc
        else:
            return mc[:count]

    def key_most_common(self, key, count = __marker):
        if count == self.__marker:
            return self.__dict[key].counter.most_common()
        else:
            return self.__dict[key].counter.most_common(count)