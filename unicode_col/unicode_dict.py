from icu import Collator, Locale, UCollAttribute, UCollAttributeValue
try:
    from thread import get_ident as _get_ident
except ImportError:
    from dummy_thread import get_ident as _get_ident

from unicode_set import unicode_set

from collections import Mapping, Callable

class unicode_dict(dict):
    '''Dictionary that support unicode comparison as defined by icu (UCA)
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize a unicode dictionary.  The signature is changed because the 
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
        if len(args) == 1:
            if isinstance(args[0],Mapping):
                vals = args[0].items()
            else:
                vals = args[0]
            for key,val in vals:
                self.__setitem__(key,val)

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

    def __setitem__(self, key, value):
        super(unicode_dict,self).__setitem__(self.__in_key(key),(key,value))

    def __getitem__(self, key):
        try:
            return super(unicode_dict,self).__getitem__(self.__in_key(key))[1]
        except KeyError:
            raise KeyError(key)

    def get(self, key, default = None):
        try:
            return super(unicode_dict,self).__getitem__(self.__in_key(key))[1]
        except KeyError:
            return default
    
    def __delitem__(self, key):
        try:
            super(unicode_dict,self).__delitem__(self.__in_key(key))
        except KeyError:
            raise KeyError(key)
    
    def __iter__(self):
        for i,_ in super(unicode_dict,self).itervalues():
            yield i

    def __contains__(self,key):
        return super(unicode_dict,self).__contains__(self.__in_key(key))

    def clear(self):
        super(unicode_dict,self).clear()
    
    def keys(self):
        return list(self)

    def values(self):
        return [i for _,i in super(unicode_dict,self).itervalues()]

    def items(self):
        return [i for i in super(unicode_dict,self).itervalues()]
    
    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for _,i in super(unicode_dict,self).itervalues():
            yield i

    def iteritems(self):
        for i in super(unicode_dict,self).itervalues():
            yield i

    def update(self, *args,**kwargs):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        
        if isinstance(args[0],Mapping):
            vals = args[0].items()
        else:
            vals = args[0]
        for key,val in vals:
            self.__setitem__(key,val)

        for key,val in kwargs:
            self.__setitem__(key,val)

    __marker = object()

    def pop(self, key, default=__marker):
        if key in self:
            r = self[key]
            del self[key]
            return r
        if default is self.__marker:
            raise KeyError(key)
        return default
    
    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def popitem(self):
        _,v = super(unicode_dict,self).popitem()
        return v

    def __repr__(self, _repr_running={}):
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, dict(self.items()))
        finally:
            del _repr_running[call_key]

    def __reduce__(self):
        items = self.items()
        inst_dict = vars(self).copy()
        for k in vars(unicode_dict()):
            inst_dict.pop(k, None)
        inst_dict.update({
            'locale':self.locale, 
            'comparison_level':self.comparison_level,
            'case_sensitive': self.case_sensitive
            })
        return (unicode_dict_from_data, ([items],inst_dict))
    
    def copy(self):
        return self.__class__(self)

    def __eq__(self, other):
        ''' Two unicode_dict are equal only if have all keys equal and the matching val is equal
        unicode_dict are equal only with themselves

        '''
        if not isinstance(other,self.__class__):
            return False
        return self.locale == other.locale and self.comparison_level == other.comparison_level and \
            self.case_sensitive == other.case_sensitive and \
            unicode_set(self.iterkeys()) == unicode_set(other.iterkeys()) and \
            all(self[k] == other[k] for k in self)

    def __ne__(self, other):
        return not self == other

##
# Helper for pickle
def unicode_dict_from_data(args,kwargs = None):
    if kwargs is None:
        kwargs = {}
    fwd_kwargs = {i:kwargs.pop(i) for i in ('locale', 'comparison_level', 'case_sensitive') if i in kwargs}
    r = unicode_dict(*args,**fwd_kwargs)
    for i,v in kwargs.iteritems():
        setattr(r,i,v)
    return r

class unicode_defaultdict(unicode_dict):
    def __init__(self, *args, **kwargs):
        '''Initialize a unicode dictionary.  The signature is changed because the 
        kwargs are used to set the comparison details

        '''
        if len(args) > 2:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))

        if len(args) == 0:
            self.default_factory = None
        else:
            self.default_factory = args[0]
            args = args[1:]
            if not isinstance(self.default_factory, Callable):
                raise TypeError("first argument must be callable")

        super(unicode_defaultdict,self).__init__(*args,**kwargs)

    def __getitem__(self,key):
        self.__key = key
        try:
            return super(unicode_defaultdict,self).__getitem__(key)
        finally:
            del self.__key

    def __missing__(self,key):
        if self.default_factory is None:
            raise KeyError(key)
        ret = self.default_factory()
        super(unicode_defaultdict,self).__setitem__(self.__key,ret)
        return (None,ret) # Use None because it is used by the underlying implementation

    def __reduce__(self):
        items = self.items()
        inst_dict = vars(self).copy()
        for k in vars(unicode_dict()):
            inst_dict.pop(k, None)
        inst_dict.update({
            'locale':self.locale, 
            'comparison_level':self.comparison_level,
            'case_sensitive': self.case_sensitive
            })
        return (unicode_defaultdict_from_data, ([self.default_factory, items],inst_dict))

    def __repr__(self, _repr_running={}):
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            return '%s(%s, %r)' % (self.__class__.__name__, self.default_factory, dict(self.items()))
        finally:
            del _repr_running[call_key]

def unicode_defaultdict_from_data(args,kwargs = None):
    if kwargs is None:
        kwargs = {}
    fwd_kwargs = {i:kwargs.pop(i) for i in ('locale', 'comparison_level', 'case_sensitive') if i in kwargs}
    r = unicode_defaultdict(*args,**fwd_kwargs)
    for i,v in kwargs.iteritems():
        setattr(r,i,v)
    return r