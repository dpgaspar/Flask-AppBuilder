from flask_appbuilder import ModelView
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.interface import SQLAInterface
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_babel import lazy_gettext as _                                       # <<-- INCLUDED
from wtforms import validators                                                  # <<-- INCLUDED


from . import appbuilder, db, app
from .models import Benefit, Department, Employee, EmployeeHistory, Function

class EmployeeHistoryView(ModelView):
    datamodel = SQLAInterface(EmployeeHistory)
    list_columns = ["department", "begin_date", "end_date"]


#=================== BEGIN CUSTOMIZATION OF EmployeeView(ModelView) ===================

from .overrides import MyDecimalField, MyDateField, MySearchWidget, MyModelView

from .myglobals import gbl_department_query

from .myglobals import gbl_dec_formatter, gbl_dt_formatter

from .myvalidators import MySalaryValidator
class EmployeeView(MyModelView):                    # <<== ALWAYS USE this overrided/subclass of class ModelView here
    datamodel = SQLAInterface(Employee)
    list_columns = ["full_name", "employee_number", "salary", "begin_date", "department.name"]
    show_template = "appbuilder/general/model/show_cascade.html"
    related_views = [EmployeeHistoryView]

    #explicit fields labels, so they can be translated by Babel:  
    label_columns = {'full_name':_('Full Name'), 'address':_('Address'),
                     'fiscal_number':_('Fiscal Number'),
                     'employee_number':_('Employee Number'),
                     'salary':_('Salary'), 'department':_('Department'),
                     'function':_('Function'), 'benefits':_('Benefits'),
                     'begin_date':_('Begin Date'), 'end_date':_('End Date'),
                     'department.name':_('Department Name'), 
                    }

    #explicit the titles for each screen, so they can be translated by Babel:  
    add_title= _('Add Employee')
    edit_title= _('Edit Employee')
    list_title= _('List Employees')
    show_title= _('Show Employee')

    # Customized field/column validator: to validate input data, according to the business requirements:
    edit_form_validators={"salary":[MySalaryValidator(min=100000, max=100000000), validators.Required()]}


    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO FORMAT FIELDS PRESENTED IN LIST/SHOW SCREENS 
    #     **** CHANGE ACCORDING TO YOUR NEEDS    
    # Here we define some field/columns formatters to display numeral and date fields (must be globals)
    # Notice that formatters objects are used by FAB only to format fields for output in the LIST/SHOW screens
    formatters_columns = {'salary': gbl_dec_formatter.format_decimal_for_list_and_show,
                          'begin_date': gbl_dt_formatter.format_date_for_list_and_show,
                          'end_date': gbl_dt_formatter.format_date_for_list_and_show, 
                          } 
        
    
    # ==IMPORTANT==
    # The 'edit_form_extra_fields' attribute of a ModelView allows us to override FAB standard way
    # of dealing with a column/field shown in the WTForms Form of the ADD/EDIT screens.
    #  So, the appearance of the column/field for ADD/EDIT screens will be set in 'edit_form_extra_fields' below.
    #  (For LIST/SHOW screens, we need to create formatters, and set "formatters_columns", as seen above).
    # === Below a customized definition for the 'salary' column/field, which is a NUMERAL WITH DECIMALS
    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO FORMAT/MASK ANY DECIMALFIELD
    #     **** CHANGE ACCORDING TO YOUR NEEDS
    edit_form_extra_fields = { 
        "salary": MyDecimalField(            #<<-- Use this OVERRIDED subclass of DecimalField
            label=_("Salary"),               # 'salary' is a numeral with decimals, so we want it nicely formatted for output/display 
                                             # (in the LIST/SHOW screens) and nicely masked/formatted in the ADD/EDIT forms/screens
            description='',
            validators=edit_form_validators.get("salary"),  #or[validators.Optional()]
            default=datamodel.get_col_default('salary'),
            places = 4,                     # SET this whith the same number of decimal places defined in Model for this field
            positive_only = True,           # No negative salaries allowed in this example    		 
            #use_locale = True,             # DON't set this, MyDecimalField will always use the current locale set by FAB
            #widget=BS3TextFieldWidget()    # # DON't set the 'widget' attribute, MyDecimalField will choose it
        ),                                    
    # === Below a customized definition for the column/field 'department':
        "department": QuerySelectField(       #  just keeping this demo from the original example  
            label=_("Department"),               
            query_factory=gbl_department_query,  # must be global
            widget=Select2Widget(extra_classes="readonly"), # makes 'department' readonly
        ),
    # === Below a customized definition for the DATE field/column 'begin_date'
    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO FORMAT/MASK ANY DATEFIELD (WITH DATEPICKER)
    #     **** CHANGE ACCORDING TO YOUR NEEDS
        "begin_date": MyDateField(            #<<-- Use this OVERRIDED customized subclass of DateField
            label=_("Begin Date"),
            description='',
            validators=[validators.Optional()],  #or [validators.Required()]
            default = datamodel.get_col_default('begin_date'),  # default value to be assumed when Model has None or for new fields
            #format = 'xxxxxxxx',          #  DON't set this; MyDateField uses dynamic formats, according to the current locale in FAB
            #widget=MyDatePickerWidget()   # DON't set 'widget' attribute; MyDateField will choose it according to 'has_picker'
            has_picker = True,             #  If true, a DateTimePicker will be shown for this field in the browser (default=True)
        ),
    # === Below an ALTERNATIVE WAY of customizing a DATE field/column - in this case, 'end_date' WON'T have a datepicker
    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO FORMAT/MASK ANY DATEFIELD (NO DATEPICKER SHOWN)
    #     **** CHANGE ACCORDING TO YOUR NEEDS
        "end_date": MyDateField(              #<<-- Use this OVERRIDED customized subclass of DateField
            label= _("End Date"),
            description='',
            validators=[validators.Optional()],   #or [validators.Required()] 
            #default = datamodel.get_col_default('end_date'),   #actually, there is no default for this field - there will be NULLs
            #widget=MyDatePickerWidget()    # # DON't set the 'widget' attribute, MyDateField will choose it according to 'has_picker'
            has_picker = False,             #  If false, a plain text field (with date mask) will be used in the browser 
         ), 
    }

    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO customize the add_form_extra_fields
    #     **** CHANGE ACCORDING TO YOUR NEEDS (normally it should be equals edit_form_extra_fields or a tweaked version of that)
    add_form_extra_fields = edit_form_extra_fields.copy() # copied, to use the same definitions as 'add_form_extra_fields"
    del add_form_extra_fields["department"]               # but removed the restriction on "department" 

    #     **** __TEMPLATE_BLOCK__ 
    #     **** THE BLOCK BELOW CAN BE USED AS A TEMPLATE TO SET search_form_extra_fields
    #     **** CHANGE ACCORDING TO YOUR NEEDS (normally, it should be equals add_form_extra_fields)
    search_form_extra_fields = add_form_extra_fields #<-- normally equals add_form_extra_fields 


#=================== END CUSTOMIZATION OF EmployeeView(ModelView) ===================
   

class FunctionView(ModelView):
    datamodel = SQLAInterface(Function)
    related_views = [EmployeeView]


class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeView]
        

class BenefitView(ModelView):
    datamodel = SQLAInterface(Benefit)
    add_columns = ["name"]
    edit_columns = ["name"]
    show_columns = ["name"]
    list_columns = ["name"]



db.create_all()


appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")

appbuilder.add_view(
    EmployeeView, "Employees", icon="fa-folder-open-o", category="Company", label=_('Employees')
)

appbuilder.add_separator(_('Company'))

appbuilder.add_view(
    DepartmentView, "Departments", icon="fa-folder-open-o", category="Company", label=_('Departments')
)
    
appbuilder.add_view(
    FunctionView, "Functions", icon="fa-folder-open-o", category="Company", label=_('Functions' )
)
appbuilder.add_view(
    BenefitView, "Benefits", icon="fa-folder-open-o", category="Company", label=_('Benefits' )
)

