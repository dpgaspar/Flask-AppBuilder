#=== begin logging stuff ===
import logging
logger = logging.getLogger(__name__)

import sys
def whoami(): 
    return sys._getframe(1).f_code.co_name + "()"
#=== end logging stuff ===



#========== LOCALIZED MASKS DEFINITIONS FOR EDIT/ADD FORMS TEMPLATES ============ 
#========== AND LOCALIZED FORMATS FOR SHOW/LIST FORMATTERS           ============

class LocaleDefinitions(object):

    # note: Thousand delimiters and decimal separators below were defined to match those returned 
    #       by Babel, via babel.numbers.format_decimal().
    #       But Date delimiters and date years/month 'places' were not based on Babel's format_date()
    #       because Babel's formats for some languages are not consistent with the information required
    #       (i.e 'places' for years are only 2 digits for some languages)
    #       So, for Dates, we don't use Babel, but python datetime.strftime() for formatting the Date and 
    #       datetime.strptime() to remove the masks/formatting chars - JUST LIKE class DecimalField does !!!
    #       Anyway, you can adjust the table below, whenever needed.
    dic_definitions  = \
        {"pt_BR": [".", ",", "/", 'd', 'm', 'Y', "dd/MM/yyyy"],
        "pt": [".", ",", "/", 'd', 'm', 'Y', "dd/MM/yyyy"],   
        "en": [",", ".", "-", 'Y', 'm', 'd', "yyyy-MM-dd"],
        "es": [".", ",", "/", 'd', 'm', 'Y', "dd/MM/yyyy"],
        "fr": ["\u202f", ",", "/", 'd', 'm', 'Y', "dd/MM/yyyy"],  #format_decimal(1234567.456, locale='fr') -> '1\u202f234\u202f567,456'
        "de": [".", ",", ".", 'd', 'm', 'Y', "dd.MM.yyyy"],
        "ru": ["\xa0", ",", ".", 'd', 'm', 'Y', "dd.MM.yyyy"],    #format_decimal(1234567.456, locale='ru') ->  '1\xa0234\xa0567,456'
        "zh": [",", ".", "-", 'Y', 'm', 'd', "yyyy-MM-dd"],
        "ja": [",", ".", "-", 'Y', 'm', 'd', "yyyy-MM-dd"],
        "pl": ["\xa0", ",", ".", 'd', 'm', 'Y', "dd.MM.yyyy"],    #format_decimal(1234567.456, locale='pl') ->  '1\xa0234\xa0567,456'
        "el": [".", ",", "/", 'd', 'm', 'Y', "dd/MM/yyyy"],       #<<-not sure about this
    }

    def __init__(self, appbld):
        self.appbuilder = appbld
        
    def get_locale(self):
        return self.appbuilder.bm.get_locale()  # get the locale that is currently set in FAB
        #Note: when some flag icon is clicked on FAB menu, that lang/locale end up set as session['locale']
        #      and this attribute is consulted by FAB's function babel.manager.py.BabelManager.get_locale()
        #      See code at navbar_right.html and at flask_appbuilder.base.py.Appbuilder.get_url_for_locale(self, lang) 
        #      and code at flask_appbuilder.babel.manager.py.BabelManager.get_locale()
        

    def get_th_delim(self):
        l = self.get_locale()
        tdlm = self.dic_definitions.get(l)[0]
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / hex(tdlm) or unicode(tdlm) = ", l, hex(ord(tdlm)))
        return tdlm
        
    def get_dec_sep(self):
        l = self.get_locale()
        return self.dic_definitions.get(l)[1]
                  
    def get_dt_delim(self):
        l = self.get_locale()
        return self.dic_definitions.get(l)[2]

    # The method below should ONLY be called from inside an EDIT/ADD form template
    def get_dt_pattern_for_cleave(self):   #pattern for date masks when using Cleave.js; it's a string like "['d', 'm', 'Y']" 
        l = self.get_locale()
        ptrn = "['" + self.dic_definitions.get(l)[3] + "', '" +  self.dic_definitions.get(l)[4] + "', '" + self.dic_definitions.get(l)[5] + "']"
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / ptrn = ", l, ptrn) 
        return ptrn
 
    def get_dt_format_for_strftime(self):   #date output format will be used by strftime(); must be something like: "%d/%m/%Y"
        l = self.get_locale()
        z = self.get_dt_delim()
        fmt = "%" + self.dic_definitions.get(l)[3] + z + "%" + self.dic_definitions.get(l)[4] + z + "%" + self.dic_definitions.get(l)[5] 
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / fmt = ", l, fmt) 
        return fmt

    def get_dt_format_for_datepicker(self):   # date format to be set on DateTimePicker objects
        l = self.get_locale()
        fmtpick = "'" + self.dic_definitions.get(l)[6] + "'"
        logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " fmtpick = ", l, fmtpick) 
        return fmtpick

