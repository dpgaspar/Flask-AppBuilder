The Employees application with enhancements to support "masked" fields
----------------------------------------------------------------------


This is a modified version of the simple Employee app example.

It overrides some F.A.B python classes and templates to allow the use of "masks" for fields inside forms (add/edit screens).

This app also demonstrates how one can use the same "masks" as "formats" for fields inside list and show screens.

Every "mask" and "format" is automatically localized, that is, it uses the locale of the language currently set in F.A.B.

How to use this demo app as a prototype to create any app that needs consistent and “localized” masks/formats for input and output fields/columns:
    
    •	Extract the folder structure of the demo app from the above zip file.
    
    •	The __init__.py and config.py files have some mandatory code, so keep that lines as they are (or customize them, as long as the mandatory things are kept)
    
    •	Modify ‘views.py’– important things to note: 
    
        - from .overrides import MyDecimalField, MyDateField, MySearchWidget, MyModelView
        
        - from .myglobals import gbl_dec_formatter, gbl_dt_formatter (if you want to use customized “formatters_columns” for fields displayed in list/show views)
        
    •	Still inside ‘views.py’, for each view class that you want to customize fields/columns masks and formats:
    
        - Inherit the view class from MyModelView, instead of ModelView
        
        - use the view class EmployeeView in this example as a sketch for your own view class (rename the class, use the appropriate datamodel etc.; F.A.B as usual)
        
        - look for the sections marked with “__TEMPLATE_BLOCK__” and change/customize the fields/column according to your needs (create similar blocks, for any other field/column you want to customize).
        
    

Run it::

    $ export FLASK_APP=app/__init__.py
    $ flask fab create-admin
    $ flask run


Tested with Flask Appbuilder version 2.2.4 
(may not work with higher versions, if F.A.B itself eventually overrides some of the overrides made here). 

