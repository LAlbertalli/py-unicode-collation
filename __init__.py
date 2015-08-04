from .unicode_dict import unicode_dict, unicode_defaultdict
from .unicode_str  import UnicodeStrFactory
from .unicode_set  import unicode_set

utf8_unicode_ci = UnicodeStrFactory(locale="en_US", comparison_level=0, case_sensitive=False)
utf8_unicode_cs = UnicodeStrFactory(locale="en_US", comparison_level=0, case_sensitive=True)