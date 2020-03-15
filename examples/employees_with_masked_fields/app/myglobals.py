

from . import db, gbl_locale_definitions  # gbl_locale_definitions was set in __init__.py

from .models import Department
def gbl_department_query():
    return db.session.query(Department)


from .myformatters import MyDecimalFormatter, MyDateFormatter
gbl_dec_formatter = MyDecimalFormatter(gbl_locale_definitions) 
gbl_dt_formatter = MyDateFormatter(gbl_locale_definitions)

