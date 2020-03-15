#=== begin logging stuff ===
import logging
logger = logging.getLogger(__name__)

import sys
def whoami(): 
    return sys._getframe(1).f_code.co_name + "()"
#=== end logging stuff ===


# This file contains some subclasses that override behaviors of WTForms and FAB classes.
# The overrides assure that formatters for LIST/SHOW screens and masks for EDIT/ADD forms are compatible
# with each other. Main tasks: add formatting chars on values for output/display, and extract masks/formatting 
# chars from client-side submitted data, before it is made available to be stored in the DataBase.



#============================== MySearchWidget ==============================
# NOTE: DON'T FORGET to set this clas name as the attribute "search_widget" of the MyModelView class (in 'views.py')
from flask_appbuilder.widgets import FormWidget, ListWidget, SearchWidget, ShowWidget
from flask_appbuilder._compat import as_unicode
class MySearchWidget(SearchWidget):

    template = "my_search_widget_template.html"      #parent has set this to default, but we NEED to use our customized html

    #Overrided this method to pass the Wtform Form object to Jinja when rendering the search form...
    def __call__(self, **kwargs):
        label_columns = {}
        form_fields = {}
        search_filters = {}
        dict_filters = self.filters.get_search_filters()
        wtform_fields_attrs = {}
        for col in self.template_args["include_cols"]:
            label_columns[col] = as_unicode(self.template_args["form"][col].label.text)
            form_fields[col] = self.template_args["form"][col]()  # notice the '()', this only gets the 'widget'/html of the Wtform field
            search_filters[col] = [as_unicode(flt.name) for flt in dict_filters[col]]
            wtform_fields_attrs[col] = { k:v for k, v in self.template_args["form"][col].__dict__.items() \
                                            if type(v) in [int, float, bool, str] }    # ADDED - create dictionary of Field primitives attrs 
        kwargs["label_columns"] = label_columns
        kwargs["form_fields"] = form_fields
        kwargs["search_filters"] = search_filters
        kwargs["active_filters"] = self.filters.get_filters_values_tojson() 
        
        #logger.info( "%s.%s - %s %s", self.__class__.__name__, whoami(), "active_filters = ", kwargs["active_filters"])   
        active_filters_localized = []
        self.localize_filter_values(active_filters_localized, wtform_fields_attrs)     #ADDED - localize the active filters values 
        logger.info( "%s.%s - %s %s", self.__class__.__name__, whoami(), \
                      "active_filters_localized = ", active_filters_localized)
        kwargs["active_filters_localized"] = active_filters_localized 
        
        return super(MySearchWidget, self).__call__(**kwargs)


    def localize_filter_values(self, active_filters_localized, wtform_fields_attrs):

        #see https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/models/filters.py#get_filters_values_tojson
        active_filters = self.filters.get_filters_values_tojson()
        for flt in active_filters:   # each flt is a tuple with 3 elements of the filter here
            column_name = flt[0]
            operator = flt[1]
            value1 = flt[2]
            logger.info( "%s.%s - %s %s %s %s", self.__class__.__name__, whoami(), \
                    " colname, operator and value of active_filter = = ",  column_name, operator, value1)
                
            search_col_wtfield = wtform_fields_attrs.get(column_name)
            
            logger.info( "%s.%s - %s %s", self.__class__.__name__, whoami(), \
                    " search_col_wtfield type of colname = ",  search_col_wtfield['type'])

            #At this point, the WTForm Form has all the instantiated Field s, so there is a 'type' in this dict:
            if value1 == "":
                value = value1
            elif  search_col_wtfield['type'] == 'MyDateField':
                iso_format = '%Y-%m-%d'
                value2 = datetime.strptime(value1, iso_format)  #value2 now has a datetime object
                # now get the appropriate format, compatible with the locale:
                dt_format_now = gbl_locale_definitions.get_dt_format_for_strftime() 
                value3 = datetime.strftime(value2, dt_format_now) #value3 has now a string
                value = value3                
            elif search_col_wtfield['type'] == 'MyDecimalField':
                value2 = parse_decimal(value1, 'en') # value2 has now a decimal.Decimal object
                locale_now = gbl_locale_definitions.get_locale()
                value3 = format_decimal(value2, locale = locale_now, decimal_quantization=False) #value3 has now a string
                value = value3  #convert to string                
            else:
                value = value1

            logger.info( "%s.%s - %s %s %s %s", self.__class__.__name__, whoami(), 
                         " Appending in active_filters_localized : ",  column_name, operator, value)
                
            active_filters_localized.append((column_name, operator, value))




#============ MyModelView ====================================

from flask_appbuilder.views import ModelView
import re
from flask import request
from flask_appbuilder.urltools import (
#    get_filter_args, #overrided
    get_order_args,
    get_page_args,
    get_page_size_args,
)
from . import gbl_locale_definitions    # gbl_locale_definitions was set in __init__.py
from datetime import datetime
from babel.numbers import parse_decimal, format_decimal
class MyModelView(ModelView): 

    # THIS IS MANDATORY, to allow customization/localization of the SearchWidget object and the search form:
    search_widget = MySearchWidget  


    # ModelView inherits this method from flask_appbuilder.baseviews.BaseCRUDView
    # NOTICE that the "list" request only has parameters when some filters were set in the SEARCH FORM part of the list view/page
    # This method handled these parameters calling get_filter_args(), now overrided to self.my_get_filter_args()
    def _list(self):
        """
            list function logic, override to implement different logic
            returns list and search widget
        """
        if get_order_args().get(self.__class__.__name__):
            order_column, order_direction = get_order_args().get(
                self.__class__.__name__
            )
        else:
            order_column, order_direction = "", ""
        page = get_page_args().get(self.__class__.__name__)
        page_size = get_page_size_args().get(self.__class__.__name__)
        #get_filter_args(self._filters)  #overrided below
        self.my_get_filter_args(self._filters, self.search_form_extra_fields)  #<<-- here overrided get_filter_args
        widgets = self._get_list_widget(
            filters=self._filters,
            order_column=order_column,
            order_direction=order_direction,
            page=page,
            page_size=page_size,
        )
        form = self.search_form.refresh()
        self.update_redirect()
        return self._get_search_widget(form=form, widgets=widgets)



    def my_get_filter_args(self, filters, search_form_extra_fields):
        logger.info( "%s.%s - %s %s", self.__class__.__name__, whoami(), " request.args = ",  request.args)
        filters.clear_filters()
        try:    
            for arg in request.args:
                re_match = re.findall("_flt_(\d)_(.*)", arg)
                if re_match:

                    # Object 're' now has: column_name, filter_instance_index/operator, value
                    # as we can see in flask_appbuilder/models/filters.py                    
                
                    column_name = re_match[0][1]
                    operator_index = int(re_match[0][0])
                    value1 = request.args.get(arg)
               
                    search_col_wtfield = search_form_extra_fields.get(column_name)
                    cls = ""
                    #It seems that the search fields are WTForm UnboundField at this point in "runtime"...
                    if search_col_wtfield is None:
                        pass
                    elif  hasattr(search_col_wtfield, 'field_class'):   # <- deal with UnboundField of WTForm Fields
                        cls = search_col_wtfield.field_class.__name__
                    elif hasattr(search_col_wtfield, 'type'):          # <- deal with initialized WTForm Fields, just in case
                        cls = search_col_wtfield.type
                    
                    if value1 == "":
                        value = value1
                    elif cls == 'MyDateField':
                        # get the appropriate format, compatible with the locale
                        dt_format_now = gbl_locale_definitions.get_dt_format_for_strftime() 
                        value2 = datetime.strptime(value1, dt_format_now)  #value2 now has a datetime object
                        iso_format = '%Y-%m-%d'
                        value3 = datetime.strftime(value2, iso_format) #value3 has now a string
                        value = value3                        
                    elif cls == 'MyDecimalField': 
                        locale_now = gbl_locale_definitions.get_locale()
                        value2 = ''.join(c for c in value1 if c.isdigit() or c in ['.',',','+','-']) 
                        value3 = parse_decimal(value2, locale_now) # value3 has now a decimal.Decimal object
                        value = str(value3)  #convert to string
                    else:
                        value = value1

                    logger.info( "%s.%s - %s %s %s %s", self.__class__.__name__, whoami(), 
                                    " calling filters.add_filter_index with ",  column_name, operator_index, value)
                                    
                    filters.add_filter_index(                
                        #re_match[0][1], int(re_match[0][0]), request.args.get(arg)  #original line
                        column_name, operator_index, value
                    )
        except  Exception as ex:
                    logger.info("%s.%s - %s %s", self.__class__.__name__, whoami(), "This exception caused clearing of all filters: ", ex)
                    logger.exception(ex)
                    # THE identified exception occurs when there are active search filters set and the user changes the 
                    #     locale/language(with FAB flags menu).In this case, the url for 'list' is sent with the filters 
                    #     args/parameters formatted for the OLD language. 
                    #     This situation causes a mismatch between those formats and the mask/formats expected here, 
                    #     which are based in the NEW locale/lang, raising an error. 
                    #     For now, just cleaning all the filters, because language changing during searchs is uncommom ...
                    filters.clear_filters()




#============ MyDecimalField ================================

from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from wtforms.fields.core import DecimalField, DateField 
import decimal	
from wtforms.utils import unset_value
class MyDecimalField(DecimalField):

    def __init__(self, positive_only=False, places=2, **kwargs):
        self.positive_only = positive_only  #this is only used to set this field mask when the form is shown in the browser
        self.decimal_scale = places         #this is only used to set this field mask when the form is shown in the browser 

        mywidget = MyBS3TextFieldWidget(custom_classes='my_appbuilder_num_decimal a_test') #<<--- just a "plain" text field  (but a javascript mask will be set to this field, by the ab.js script, afterwards)
                
        #DecimalField does not accept places > 2 when use_locale=True, so let's force use_locale = False before calling super()...
        kwargs['use_locale'] = False
 
        super(MyDecimalField, self).__init__(widget=mywidget, places=places, **kwargs)
        
        self.use_locale = True    # Actually, irrelevant, because MyDecimalField._value() and .process_formdata() ALWAYS use locale
        self.format = None        # Irrelevant, MyDecimalField always uses a format compatible with the current locale

        from babel import numbers     # 2 lines of code copied from parent; babel is used by _value() and process_formdata() methods
        self.babel_numbers = numbers

        #self.render_kw={'class':'MyDecimalField','data-decimal_scale':self.decimal_scale, 'data-positive_only':lambda x: 1 if self.positive_only else 0}
        # Note: the 'class' in render_kw does NOT override NOR appends the 'class' already in the widget template; 
        # If needed, set the 'class' through the overrided widget, as we did above in MyBS3TextFieldWidget.
        # SO, here with render_kw only sending attributes of the field, to be rendered in the html page:
        self.render_kw={'data-decimal_scale':self.decimal_scale, \
                        'data-positive_only':self.positive_only} #if True, positive_only will appear in the html page, if False it will simply NOT be present in the html page...

				
    # Returns the value of self.data nicely formatted for output/display
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]     # copyed from parent, not sure about that...
        elif self.data is not None:    
            locale_now = gbl_locale_definitions.get_locale() # current locale/lang set by FAB 
            valuefmt = self.babel_numbers.format_decimal(self.data, locale = locale_now, decimal_quantization=False)
            #valuefmt = self.clean_numeral(valuefmt) #could get rid of strange chars, if needed
            logger.info( "%s.%s %s - %s %s / %s", self.__class__.__name__, whoami(), self.name, " locale now / valuefmt = ", locale_now, valuefmt) 
            return valuefmt
        else:
            return ""


    # This method receives the (sometimes masked/formatted) data submitted from the browser
    # and remove extra characters, also correct the decimal mark and store the data as decimal.Decimal
    # Below we use babel.numbers.parse_decimal() to do the hard work !!!    
    def process_formdata(self, valuelist):
        if not valuelist:
            return            
        if valuelist[0] == '' and (self.data == self.default): 
            pass      # THEN, nothing to do: there is already a Decimal object with default value in self.data (or None)
        else:
            try:
                locale_now = gbl_locale_definitions.get_locale() # get FAB current locale/lang        
                logger.info( "%s.%s - %s %s / %s", self.__class__.__name__, whoami(), " locale now / valuelist = ", locale_now, valuelist) 
                #Remove mask characters, keeping only ".", ",", "+-" and digits:
                cleaned = self.clean_numeral(valuelist[0]) 
                self.data = self.babel_numbers.parse_decimal(cleaned, locale_now) #babel returns a decimal.Decimal
                logger.info( "%s.%s %s - %s %s", self.__class__.__name__, whoami(), self.name, "self.data = ", self.data) 
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(_("Not a valid decimal value"))


    #Function to remove mask characters from submitted data, keeps only "+", "-", ".", "," and digits:
    def clean_numeral(self, x):
        return ''.join(elem for elem in x if elem.isdigit() or elem in ['.',',','+','-'])




#============ MyDateField =================================

from flask_appbuilder.fieldwidgets import DatePickerWidget
class MyDateField(DateField):

    def __init__(self, has_picker=True, **kwargs):
        mywidget = None
        if has_picker:
            mywidget =  MyDatePickerWidget() #<<---OVERRIDES original DatePickerWidget to prevent auto instantiation of old datetimepicker objects
        else:
            mywidget = MyBS3TextFieldWidget(custom_classes='my_appbuilder_date_no_picker a_test') #<<--- just a "plain" text field to display the date (but a javascript mask will be set to this field, by the ab.js script, afterwards)
   
        super(MyDateField, self).__init__(widget = mywidget, **kwargs) 

        #TESTING render_kw:
        #self.render_kw = {'class':'MyDateField','data-some_attribute':'aaa-bbb-ccc'}
        # The 'class' in render_kw does NOT override NOR appends the 'class' already in the widget template; 
        # If needed, set the 'class' through the overrided widget, as we did above with MyBS3TextFieldWidget.
        # SO, here with render_kw only sending attributes of the field, to be rendered in the html page:
        self.render_kw = {'data-some_attribute':'aaa-bbb-ccc'}

                

    def _value(self):
        locale_now = gbl_locale_definitions.get_locale() #get the locale that is currently set in FAB       
        dt_format_now = gbl_locale_definitions.get_dt_format_for_strftime()  # get the appropriate format, compatible with the locale 
        logger.info( "%s.%s %s - %s %s / %s", self.__class__.__name__, whoami(), self.name, " locale now / dt_format_now = ", locale_now, dt_format_now) 
        self.format = dt_format_now # will be used by strftime() in the _value() method at the parent class
        return super(MyDateField, self)._value()   

    def process_formdata(self, valuelist):
        if not valuelist:
            return            
        locale_now = gbl_locale_definitions.get_locale() #get the locale that is currently set in FAB         
        dt_format_now = gbl_locale_definitions.get_dt_format_for_strftime()  # get the appropriate format, compatible with the locale 
        logger.info( "%s.%s %s - %s %s / %s / %s / %s", self.__class__.__name__, whoami(), self.name, " locale now / dt_format_now /valuelist= ", locale_now, dt_format_now, valuelist, self.data) 
        #IF WTForms.Field.process() method has set the value of self.data to self.default        
        if valuelist[0] == '' and (self.data == self.default): 
            pass      # THEN, nothing to do: there is already a Date object with default value in self.data (or None)
        else:
            self.format = dt_format_now # will be used by strptime() in the method of the parent class
            super(MyDateField, self).process_formdata(valuelist)   


#========================= MyDatePickerWidget =========================

from flask_appbuilder.fieldwidgets import DatePickerWidget
from wtforms.widgets import html_params, HTMLString
class MyDatePickerWidget(DatePickerWidget):
    # Because format will be dynamically set, removed 'data-format=' from the "<input" tag (not important, but done). 
    data_template = (
        '<div class="input-group date my_appbuilder_date" id="mydatepicker">'
        '<span class="input-group-addon"><i class="fa fa-calendar cursor-hand"></i>'
        "</span>"
        '<input class="form-control" %(text)s />'
        "</div>"
    )

    #Override of this method was necessary in order to use field._value(), not field.data. 
    # This is because field.data gets an unformatted date string, which we don't want.
    # On the other hand, the _value() function of MyDateField returns a Date formatted
    # according to the current locale that is set by FAB, which is what we want).
    def __call__(self, field, **kwargs):    
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        if not field.data:
            field.data = ""
        template = self.data_template
        return HTMLString(
            #template % {"text": html_params(type="text", value=field.data, **kwargs)}    # replaced by line below
            template % {"text": html_params(type="text", value=field._value(), **kwargs)}
        )



#========================= MyBS3TextFieldWidget =========================

# This overrides BS3TextFieldWidget only to include other html 'class'(es) to be handled by javascripts 
class MyBS3TextFieldWidget(BS3TextFieldWidget):

    def __init__(self, custom_classes='', **kwargs):
        self.custom_classes = custom_classes                     # store this for use in __call__ method
        super(MyBS3TextFieldWidget, self).__init__(**kwargs)     



    def __call__(self, field, **kwargs):
        kwargs["class"] = u"form-control"   #original line        
        if self.custom_classes:
            kwargs["class"] = kwargs["class"] + " " + self.custom_classes # custom_classes have to be already separated by " "        
        if field.label:
            kwargs["placeholder"] = field.label.text
        if "name_" in kwargs:
            field.name = kwargs["name_"]            
        #logger.info( "%s.%s - %s %s", self.__class__.__name__, whoami(), " === kwargs now = ", kwargs)            

        #NOTICE - here we HAVE to call the method __call__ of the grandparent, otherwise we'll lose 
        # the modified kwargs['class]' above - So, we call super with BS3TextFieldWidget NOT MyBS3TextFieldWidget
        return super(BS3TextFieldWidget, self).__call__(field, **kwargs)


