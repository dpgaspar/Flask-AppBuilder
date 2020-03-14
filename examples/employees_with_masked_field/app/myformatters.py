#=== begin logging stuff ===
import logging
logger = logging.getLogger(__name__)

import sys
def whoami(): 
    return sys._getframe(1).f_code.co_name + "()"
#=== end logging stuff ===



#============ THESE 2 CLASSES ARE USED ONLY FOR FIELDS IN LIST/SHOW SCREENS ================

class MyDecimalFormatter(object):  

    def __init__(self, locale_definitions):
        self.locale_definitions = locale_definitions
        from babel import numbers
        self.babel_numbers = numbers           


    def format_decimal_for_list_and_show(self, v):
        if v is None:    #Handle  NULL values (in case we accept empty inputs and NO default is set)
            return ""
        #get the locale that are currently set by FAB:
        locale_now = self.locale_definitions.get_locale()   
        valuefmt = self.babel_numbers.format_decimal(v, locale = locale_now, decimal_quantization=False)
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / valuefmt = ", locale_now, valuefmt) 
        return valuefmt
        


import datetime
class MyDateFormatter(object):   

    def __init__(self,locale_definitions ):
        self.locale_definitions = locale_definitions

    def format_date_for_list_and_show(self, v):
        if v is None:    #Handle  NULL values (in case we accept empty inputs and NO default is set)
            return ""
        #get the locale that are currently set by FAB:
        locale_now = self.locale_definitions.get_locale()
        #get the appropriate format, acoording to the current locale:
        dt_format_now = self.locale_definitions.get_dt_format_for_strftime()
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / dt_format_now = ", locale_now, dt_format_now) 
        return v.strftime(dt_format_now)  #<<-- "v" is a datetime.date object, so it works


 