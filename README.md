# py-unicode-collation
Library of helper functions for Python to easily support string collation.

## Rationale
One of the main issue you face when working with text stored in a database and you process it in Python, especially Unicode text, is that databases runs comparison using a specific collations while Python runs byte comparison. For this reason `home` and `Home` are the same for MySQL but not for Python. For this specific example, it is possible to convert both strings to lower or upper case before the comparison. But it could be a problem for internationalized strings where for example `Straße` and `Strasse` are formally the same.

To solve this issue, the Unicode standard introduced the Unicode Collation Algorithm (UCA). [Standard](http://unicode.org/reports/tr10/) and [Wikipedia](https://en.wikipedia.org/wiki/Unicode_collation_algorithm). Fortunately, Python provides access to collation algorithms using [ICU (International Component for Unicode)](http://site.icu-project.org/), a battle tested set of algorithms for Unicode strings manipulation. The Python binding is [pyICU](https://pypi.python.org/pypi/PyICU/).

Although pyICU is great, the API provided are low level and difficult to use. Since in our projects we run a lot of comparison with Unicode strings considering the collation, I've decided to write some simple functions and classes to simplify my everyday life.

## Installation
Just download the package and run
```
sudo python setup.py install
```
in the code directory. The library depends on pyICU 1.4 or better, but it will take care of download and install the dependency (compiling pyICU could require libicu: almost all the Linux distro I'm aware of ships a version of libicu, check the [ICU site](http://site.icu-project.org/) for Mac and Windows)
### Python 3
This library has been written for Python 2 (2.6 and upper) and ported to Python 3 using `2to3`. The Python 3 porting passed all the tests in the test case and I'm not aware of bugs, but I cannot guarantee it works properly, especially for the strings helper functions for which the test coverage is low.

## Usage
The library provides the following facilities:
* `UnicodeStrFactory` a facility functions that return specific Unicode string classes. To make the use simpler there are two classes already initialized: `utf8_unicode_ci` and `utf8_unicode_cs`, modeled on the same collations from MySQL (although the MySQL collation algorithm is slightly different).
* `unicode_set`, an implementation of sets using the selected collations level.
* `unicode_dict` and `unicode_defaultdict`, the implementations of dicts and defaultdicts using the collation.

All the classes are available in the package `unicode_col`. To access them it is enough to run:
```python
from unicode_col import *
```
### Collation Algorithm configuration
All the provided classes accept the following keyword parameters to configure the UCA:
* `locale`: the local described in ISO 639-2 standard. E.g. American English is `en_US`. Default is `en_US`.
* `comparison_level`: the strictness level of the comparison. An integer from 0 (the most permissive) to 3 (the strictest). Default is `0`.
* `case_sensitive`: a boolean to decide if the comparison should be case-sensitive or case-insensitive. Default is `False`.

The same name are used for the read-only properties of the objects.
### Dicts and sets
Dict and Set and classes have the same signature of the standard Python primaries. Passing an instance of `unicode_dict` as first parameter to the `unicode_dict` constructor create a copy of the dict. Passing different UCA parameters cast the object to different space. The same for `unicode_set`.
```python
from unicode_col import unicode_set
a = unicode_set([u'ábc',u'ñ',u'abc'], comparison_level=3) # a contains 3 elements
b = unicode_set(a) # create an exact copy of a, it contains 3 elements
c = unicode_set(a, comparison_level=0) # c use the comparison level 0, It contains only two elements because ábc and abc are the same
```
### Strings
Strings are created instantiating the proper class with the required params and then creating the string objects with the class.
```python
from unicode_col import utf8_general_ci, UnicodeStrFactory
myunicode = UnicodeStrFactory(comparison_level = 3)
utf8_general_ci(u'ábc') == utf8_general_ci(u'abc') # True
myunicode(u'ábc') == myunicode(u'abc') # False
```
_Special consideration is necessary when comparing string with different collations_. Since the comparison assumes the collation of the left element, the result could be unexpected. In particular `a == b` does not imply that `b == a`.
This strings are immutable and hashable and could be used as keys in dict or in set. Using these strings with the standard dict and set class of Python give the same results as `unicode_dict` and `unicode_set`. Nevertheless, due to the unexpected behaviors related to mixing different collations, it is strongly suggested to use `unicode_dict` and `unicode_set`instead.
