from flask.ext.babelex import Domain

from flask.ext.appbuilder import translations

domain = CustomDomain(dirname=translations.__path__[0])
    
gettext = domain.gettext
ngettext = domain.ngettext
lazy_gettext = domain.lazy_gettext
