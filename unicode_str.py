#!/usr/bin/python
# -*- coding: utf8 -*-
from icu import Collator, Locale, StringSearch, USearchAttribute, UCollAttribute, UCollAttributeValue
import sys

class UnicodeStrFactory(object):
    def __init__(self,locale="EN_US",comparison_level=0,case_sensitive=False):
        comparison_level = max(0,min(3,comparison_level))

        self.__locale = Locale(locale)
        self.__collator = Collator.createInstance(self.__locale)
        self.__collator.setStrength(comparison_level)
        self.__collator.setAttribute(UCollAttribute.CASE_LEVEL,
            UCollAttributeValue.ON if case_sensitive else UCollAttributeValue.OFF)
        if comparison_level == 0 and case_sensitive == False:
            self.__base_coll = self.__collator
        else:
            self.__base_coll = Collator.createInstance(self.__locale)
            self.__base_coll.setStrength(0)
            self.__base_coll.setAttribute(UCollAttribute.CASE_LEVEL, UCollAttributeValue.OFF)

    @property
    def locale(self):
        return self.__locale.getName()

    @property
    def comparison_level(self):
        return self.__collator.getStrength()

    @property
    def case_sensitive(self):
        return self.__collator.getAttribute(UCollAttribute.CASE_LEVEL) == UCollAttributeValue.ON

    @property
    def collator(self):
        return self.__collator

    def coll_len(self,string):
        return len(self.__base_coll.getSortKey(string))-1

    __marker = object()

    def __call__(self,obj,encoding=__marker, errors='strict'):
        class unicode_str(unicode_str_base):
            _factory = self

        if encoding == self.__marker:
            return unicode_str(obj)
        else:
            return unicode_str(obj,encoding=encoding,errors=errors)

    def __reduce__(self):
        inst_dict = vars(self).copy()
        for k in vars(self.__class__()):
            inst_dict.pop(k, None)
        return (self.__class__, (self.locale,self.comparison_level,self.case_sensitive), inst_dict)

    def key_for_caching(self,word):
        return self(word).key_for_caching()

class unicode_str_base(unicode):
    _factory = None

    __marker = object()
    # Use utf8 as default encoding instead of ascii
    def __init__(self, string, encoding=__marker, errors='strict'):
        if self._factory is None:
            raise NotImplementedError("Cannot instatiate. You should use a UnicodeStrFactory instance")
        # The inizialization of unicode is done in __new__
        # if encoding == self.__marker:
        #     super(unicode_str_base,self).__init__(string)
        # else:
        #     super(unicode_str_base,self).__init__(string,encoding=encoding,errors=errors)
        self.__strKey = self._factory.collator.getSortKey(self)

    def key_for_caching(self):
        '''Only method added. Used to extract a key suitable for external caching (e.g: redis)
        return the comparison string base64 encoded without final \\n
        '''
        return self.__strKey.encode('base64')[:-1]

    def __add__(self,other):
        '''x.__add__(y) <==> x+y
        '''
        self.__class__(self+other)

    def __contains__(self,other):
        '''x.__contains__(y) <==> y in x
        '''
        if self == '':
            return other == ''

        if other == '':
            return True

        it = StringSearch(other,self,self._factory.collator)
        while True:
            try:
                it.next()
                match = it.getMatchedText()
                if self.__class__(match) == self.__class__(other):
                    return True
            except StopIteration:
                return False

    def __eq__(self,other):
        '''x.__eq__(y) <==> x==y
        '''
        if not isinstance(other,basestring):
            return False
        return self._factory.collator.compare(self,other) == 0

    def __lt__(self,other):
        '''x.__lt__(y) <==> x<y
        '''
        if not isinstance(other,basestring):
            return False
        return self._factory.collator.compare(self,other) == -1

    def __ne__(self,other):
        '''x.__ne__(y) <==> x!=y
        '''
        return not self == other

    def __gt__(self,other):
        '''x.__gt__(y) <==> x>y
        '''
        return not (self == other or self < other)

    def __ge__(self,other):
        '''x.__gt__(y) <==> x>=y
        '''
        return not self < other

    def __le__(self,other):
        '''x.__gt__(y) <==> x<=y
        '''
        return self == other or self < other 

    def __hash__(self):
        '''x.__hash__() <==> hash(x)
        '''
        return hash(self.__strKey)

    def __getitem__(self, index):
        '''x.__getitem__(y) <==> x[y]
        '''
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError("string index out of range")
        x = 0
        while self._factory.coll_len(unicode.__getslice__(self,0,x)) <= index:
            x+=1
        return self.__class__(unicode.__getitem__(self,x-1))

    def __len__(self):
        '''x.__len__() <==> len(x)
        '''
        return self._factory.coll_len(self)

    def __getslice__(self,start,stop):
        '''x.__getslice__(i, j) <==> x[i:j]
        '''
        if stop > len(self):
            stop = len(self)
        if start >= stop:
            return self.__class__("") #shortcut
        x = 0
        while self._factory.coll_len(unicode.__getslice__(self,0,x)) <= start:
            x+=1
        if stop == len(self):
            y = sys.maxint
        else:
            y = 0
            while self._factory.coll_len(unicode.__getslice__(self,0,y)) < stop:
                y+=1
        return self.__class__(unicode.__getslice__(self,x-1,y))

    def __mod__(self,x):
        '''x.__mod__(y) <==> x%y
        '''
        return self.__class__(unicode.__mod__(self,x))

    def __mul__(self,x):
        '''x.__mul__(y) <==> x%y
        '''
        return self.__class__(unicode.__mul__(self,x))

    def __rmod__(self,x):
        '''x.__mod__(y) <==> x%y
        '''
        return self.__class__(unicode.__mod__(self,x))

    def __rmul__(self,x):
        '''x.__mul__(y) <==> x%y
        '''
        return self.__class__(unicode.__mul__(self,x))

    def __repr__(self):
        if not self:
            return 'unicode_str()'
        return 'unicode_str(%s, locale=%s, comparison_level=%d)' % \
            (unicode.__repr__(self)[1:],self._factory.locale, self._factory.comparison_level)

    def capitalize(self):
        '''S.capitalize() -> unicode
        
        Return a capitalized version of S, i.e. make the first character
        have upper case and the rest lower case.
        '''
        return self.__class__(unicode.capitalize(self))
    
    def center(self, width, fillchar=' '): 
        '''S.center(width[, fillchar]) -> unicode
        
        Return S centered in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space)
        '''
        return self.__class__(unicode.center(self, width, fillchar))
    
    def count(self, sub, start=0, end = sys.maxint):
        '''S.count(sub[, start[, end]]) -> int
        
        Return the number of non-overlapping occurrences of substring sub in
        Unicode string S[start:end].  Optional arguments start and end are
        interpreted as in slice notation.
        '''
        string=self[start:end]
        c = 0
        # corner cases
        if string == '':
            return 1 if sub == '' else 0
        if sub == '':
            return len(string)+1

        it = StringSearch(sub,string,self._factory.collator)
        it.setAttribute(USearchAttribute.OVERLAP,False)
        try:
            while True:
                it.next()
                match = it.getMatchedText()
                if self.__class__(match) == self.__class__(sub):
                    c+=1
        except StopIteration:
            pass

        return c

    def decode(self,encoding=__marker,errors='strict'):
        '''S.decode([encoding[,errors]]) -> string or unicode
        
        Decodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeDecodeError. Other possible values are 'ignore' and 'replace'
        as well as any other name registered with codecs.register_error that is
        able to handle UnicodeDecodeErrors.
        '''
        if encoding == self.__marker:
            return self.__class__(unicode.decode(self))
        else:
            return self.__class__(unicode.decode(self, encoding, errors))

    def encode(self,encoding=__marker,errors='strict'):
        '''S.encode([encoding[,errors]]) -> string or unicode
        
        Encodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeEncodeError. Other possible values are 'ignore', 'replace' and
        'xmlcharrefreplace' as well as any other name registered with
        codecs.register_error that can handle UnicodeEncodeErrors.
        '''
        if encoding == self.__marker:
            return self.__class__(unicode.encode(self))
        else:
            return self.__class__(unicode.encode(self, encoding, errors))

    def endswith(suffix, start = 0, end = sys.maxint):
        '''S.endswith(suffix[, start[, end]]) -> bool
        
        Return True if S ends with the specified suffix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.
        '''
        string = self[start:end]
        return string[-len(suffix):] == suffix


    def expandtabs(self, tabsize = 8):
        '''S.expandtabs([tabsize]) -> unicode
        
        Return a copy of S where all tab characters are expanded using spaces.
        If tabsize is not given, a tab size of 8 characters is assumed.
        '''
        return self.__class__(unicode.expandtabs(self,tabsize))

    def find(self,sub, start = 0, end = sys.maxint):
        '''S.find(sub [,start [,end]]) -> int
        
        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.
        
        Return -1 on failure.
        '''
        string = self[start:end]
        c = 0
        # corner cases
        if string == '':
            return 0 if sub == '' else -1
        if sub == '':
            return 0

        it = StringSearch(sub,string,self._factory.collator)
        it.setAttribute(USearchAttribute.OVERLAP,False)
        while True:
            try:
                r = it.next()
                match = it.getMatchedText()
                if self.__class__(match) == self.__class__(sub):
                    return start+r
            except StopIteration:
                return -1

    def format(self, *args, **kwargs):
        '''S.format(*args, **kwargs) -> unicode
        
        Return a formatted version of S, using substitutions from args and kwargs.
        The substitutions are identified by braces ('{' and '}').
        '''
        return self.__class__(unicode.format(self,*args,**kwargs))

    def index(self,sub, start = 0, end = sys.maxint):
        '''S.index(sub [,start [,end]]) -> int
        
        Like S.find() but raise ValueError when the substring is not found.
        '''
        l=self.find(sub,start,end)
        if l == -1:
            raise ValueError(sub)
        return l

    def join(self, iterable):
        '''S.join(iterable) -> unicode
        
        Return a string which is the concatenation of the strings in the
        iterable.  The separator between elements is S.
        '''
        return self.__class__(unicode.join(self, iterable))

    def ljust(self, witdh, fillchar=' '):
        '''S.ljust(width[, fillchar]) -> int
        
        Return S left-justified in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space).
        '''
        return self.__class__(unicode.ljust(self, witdh, fillchar=' '))

    def lower(self):
        '''S.lower() -> unicode
        
        Return a copy of the string S converted to lowercase.
        '''
        return self.__class__(unicode.lower(self))

    def lstrip(self,chars = None):
        '''S.lstrip([chars]) -> unicode
        
        Return a copy of the string S with leading whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        '''
        if chars is None:
            chars = self.__class__(' ')
        else:
            chars = self.__class__(chars)
        c=0
        while self[c] in chars:
            c+=1
        return self[c:]

    def partition(self,sep):
        '''S.partition(sep) -> (head, sep, tail)
        
        Search for the separator sep in S, and return the part before it,
        the separator itself, and the part after it.  If the separator is not
        found, return S and two empty strings.
        '''
        sep = self.__class__(sep)
        index = self.find(sep)
        if index > -1:
            return(self[:index],sep,self[index+len(sep):])
        else:
            return(self.__class__(""),sep,self.__class__(""))

    def replace(old, new, count = sys.maxint):
        '''S.replace(old, new[, count]) -> unicode
        
        Return a copy of S with all occurrences of substring
        old replaced by new.  If the optional argument count is
        given, only the first count occurrences are replaced.
        '''
        return NotImplementedError

    def rfind(self, sub ,start = 0 ,end = sys.maxint):
        '''S.rfind(sub [,start [,end]]) -> int
        
        Return the highest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.
        
        Return -1 on failure.
        '''
        string = self[start:end]
        # corner cases
        if string == '':
            return 0 if sub == '' else -1
        if sub == '':
            return len(string)+start

        c = 0
        it = StringSearch(sub,self,self._factory.collator)
        it.setAttribute(USearchAttribute.OVERLAP,False)
        r = it.last()
        while r>= 0:
            match = it.getMatchedText()
            if self.__class__(match) == self.__class__(sub):
                return start + r
            r = it.preceding(r)
        return r

    def rindex(self, sub ,start = 0 ,end = sys.maxint):
        '''S.rindex(sub [,start [,end]]) -> int
        
        Like S.rfind() but raise ValueError when the substring is not found.
        '''
        r = self.rfind(sub,start,end)
        if r == -1:
            raise ValueError(sub)
        else:
            return r

    def rjust(self, witdh, fillchar=' '):
        '''S.rjust(width[, fillchar]) -> unicode
        
        Return S right-justified in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space).
        '''
        return self.__class__(unicode.rjust(self, witdh, fillchar=' '))

    def rpartition(self,sep):
        '''S.rpartition(sep) -> (head, sep, tail)
        
        Search for the separator sep in S, starting at the end of S, and return
        the part before it, the separator itself, and the part after it.  If the
        separator is not found, return two empty strings and S.
        '''
        sep = self.__class__(sep)
        index = self.rfind(sep)
        if index > -1:
            return(self[:index],sep,self[index+len(sep):])
        else:
            return(self.__class__(""),sep,self.__class__(""))

    def rsplit(self, sep = None, maxsplit = sys.maxint):
        '''S.rsplit([sep [,maxsplit]]) -> list of strings
        
        Return a list of the words in S, using sep as the
        delimiter string, starting at the end of the string and
        working to the front.  If maxsplit is given, at most maxsplit
        splits are done. If sep is not specified, any whitespace string
        is a separator.
        '''
        raise NotImplementedError

    def rstrip(self,chars = None):
        '''S.rstrip([chars]) -> unicode
        
        Return a copy of the string S with trailing whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        '''
        if chars is None:
            chars = self.__class__(' ')
        else:
            chars = self.__class__(chars)
        c=len(self)
        while self[c-1] in chars:
            c-=1
        return self[:c]

    def split(self, sep = None, maxsplit = sys.maxint):
        '''S.split([sep [,maxsplit]]) -> list of strings
        
        Return a list of the words in S, using sep as the
        delimiter string.  If maxsplit is given, at most maxsplit
        splits are done. If sep is not specified or is None, any
        whitespace string is a separator and empty strings are
        removed from the result.
        '''
        raise NotImplementedError

    def splitlines(self, keepends=False):
        '''S.splitlines(keepends=False) -> list of strings
        
        Return a list of the lines in S, breaking at line boundaries.
        Line breaks are not included in the resulting list unless keepends
        is given and true.
        '''
        raise NotImplementedError

    def startswith(prefix, start = 0, end = sys.maxint):
        '''S.startswith(prefix[, start[, end]]) -> bool
        
        Return True if S starts with the specified prefix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        prefix can also be a tuple of strings to try.
        '''
        string = self[start:end]
        return string[:len(prefix)] == prefix

    def strip(self,chars = None):
        '''S.strip([chars]) -> unicode
        
        Return a copy of the string S with leading and trailing
        whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        '''
        return self.lstrip(self.rstrip(chars),chars)

    def swapcase(self):
        '''S.swapcase() -> unicode
        
        Return a copy of S with uppercase characters converted to lowercase
        and vice versa.
        '''
        return self.__class__(unicode.swapcase(self))

    def title(self):
        '''S.title() -> unicode
        
        Return a titlecased version of S, i.e. words start with title case
        characters, all remaining cased characters have lower case.
        '''
        return self.__class__(unicode.title(self))
        
    def translate(self, table):
        '''S.translate(table) -> unicode
        
        Return a copy of the string S, where all characters have been mapped
        through the given translation table, which must be a mapping of
        Unicode ordinals to Unicode ordinals, Unicode strings or None.
        Unmapped characters are left untouched. Characters mapped to None
        are deleted.
        '''
        return self.__class__(unicode.translate(self, table))
        
    def upper(self):
        '''S.upper() -> unicode
        
        Return a copy of S converted to uppercase.
        '''
        return self.__class__(unicode.upper(self))
        
    def zfill(self,width):
        '''S.zfill(width) -> unicode
        
        Pad a numeric string S with zeros on the left, to fill a field
        of the specified width. The string S is never truncated.
        '''
        return self.__class__(unicode.zfill(self,width))

    def __reduce__(self):
        inst_dict = vars(self).copy()
        for k in vars(self.__class__('')):
            inst_dict.pop(k, None)
        return (self._factory, (unicode(self),), inst_dict)

#### Tests ####
if __name__ == '__main__':
    ger = u'Straße'
    acc = u'àèìòùáéíóúaeiouãẽĩõũâêîôû'
    noacc = u'aeiouaeiouaeiouaeiouaeiou'
    csacc = u'AEIOUaeiouaeiouaeiouaeiou'

    unicode_ci = UnicodeStrFactory()
    unicode_cs = UnicodeStrFactory(case_sensitive=True)
    spanish_ci = UnicodeStrFactory(locale="es_ES")
    unicode_st = UnicodeStrFactory(comparison_level=2, case_sensitive=True)

    # Test len
    if len(unicode_ci(acc)) != 25:
        raise Exception

    # Standard expansion of ß to ss
    if len(unicode_ci(ger)) != 7:
        raise Exception

    # Test comparison
    if unicode_ci(ger) != unicode_ci(u'Straße'):
        raise Exception

    if unicode_ci(acc) !=unicode_ci(noacc):
        raise Exception

    if not (unicode_ci(acc) == unicode_ci(noacc)):
        raise Exception
    
    if unicode_ci(acc) != unicode_ci(csacc):
        raise Exception
    
    if not (unicode_ci(acc) == unicode_ci(csacc)):
        raise Exception

    if unicode_cs(acc) !=unicode_cs(noacc):
        raise Exception

    if not (unicode_cs(acc) == unicode_cs(noacc)):
        raise Exception
    
    if unicode_cs(acc) == unicode_cs(csacc):
        raise Exception
    
    if not (unicode_cs(acc) != unicode_cs(csacc)):
        raise Exception

    if not (unicode_cs(acc) < unicode_cs(csacc)):
        raise Exception

    if not (unicode_cs(csacc) > unicode_cs(acc)):
        raise Exception

    if unicode_st(acc) ==unicode_st(noacc):
        raise Exception

    if not (unicode_st(acc) != unicode_st(noacc)):
        raise Exception
    
    if unicode_st(acc) == unicode_st(csacc):
        raise Exception
    
    if not (unicode_st(acc) != unicode_st(csacc)):
        raise Exception

    # Accented letters compare higher (in strict mode) 
    # than not accented (despite of case)
    # The expected ordering (lower to higher no case) is:
    # a á à â ä ã 
    if not (unicode_st(acc) > unicode_st(csacc)):
        raise Exception

    if not (unicode_st(csacc) < unicode_st(acc)):
        raise Exception

    # Test different locales
    if unicode_ci(u'ñ') != unicode_ci(u'n'):
        raise Exception

    if unicode_st(u'ñ') == unicode_st(u'n'):
        raise Exception

    if spanish_ci(u'ñ') == spanish_ci(u'n'):
        raise Exception

    # Check it plays well with __hash__ (use dict)
    # Consider that == is no more commutative when
    # Used between different collations ((a == b) != (b == a))
    a={}
    a[unicode_ci(acc)] = 1
    
    if a[unicode_ci(noacc)] != 1:
        raise Exception # Should not raise a KeyError

    try:
        a[unicode_cs(noacc)]
    except KeyError:
        pass
    else:
        raise Exception # Should raise a KeyError

    try:
        a[unicode_st(noacc)]
    except KeyError:
        pass
    else:
        raise Exception # Should raise a KeyError

    if a[unicode_ci(csacc)] != 1:
        raise Exception # Should not raise a KeyError

    try:
        a[unicode_cs(csacc)]
    except KeyError:
        pass
    else:
        raise Exception # Should raise a KeyError

    try:
        a[unicode_st(csacc)]
    except KeyError:
        pass
    else:
        raise Exception # Should raise a KeyError

    a[unicode_ci(csacc)] = 2

    if a[unicode_ci(acc)] != 2:
        raise Exception

    a[unicode_ci(noacc)] = 3

    if a[unicode_ci(acc)] != 3:
        raise Exception

    if unicode_ci(acc) not in a:
        raise Exception

    if unicode_ci(noacc) not in a:
        raise Exception

    if unicode_ci(csacc) not in a:
        raise Exception

    ## Test in
    if 'ss' not in unicode_ci(ger):
        raise Exception

    if 'AEIOU' not in unicode_ci(acc):
        raise Exception

    if 'AEIOU' in unicode_cs(acc):
        raise Exception

    if 'AEIOU' not in unicode_cs(csacc):
        raise Exception

    # find and rfind / index and rindex use find so no test needed

    if unicode_ci(ger).find('ss') != 4:
        raise Exception

    if unicode_ci(ger).rfind('ss') != 4:
        raise Exception

    if unicode_ci(acc).find('aeiou') != 0:
        raise Exception

    if unicode_ci(acc).rfind('aeiou') != 20:
        raise Exception

    if unicode_ci(acc).find('aeiou',3) != 5:
        raise Exception

    if unicode_st(acc).find('aeiou') != 10:
        raise Exception

    if unicode_cs(csacc).rfind('AEIOU') != 0:
        raise Exception

    ### ADD TEST for other functionality when needed, this cover the basic

    print "All test passed!"
    
