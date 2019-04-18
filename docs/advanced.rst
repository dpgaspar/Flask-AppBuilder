Advanced Configuration
======================

Security
--------

To block or set the allowed permissions on a view, just set the *base_permissions* property with the base permissions

::

    class GroupModelView(ModelView):
        datamodel = SQLAInterface(Group)
        base_permissions = ['can_add','can_delete']

With this initial config, the framework will only create 'can_add' and 'can_delete'
permissions on GroupModelView as the only allowed. So users and even the administrator
of the application will not have the possibility to add list or show permissions on Group table view.
Base available permission are: can_add, can_edit, can_delete, can_list, can_show. More detailed info on :doc:`security`

Custom Fields
-------------

Custom Model properties can be used on lists. This is useful for formatting values like currencies, time or dates.
or for custom HTML. This is very simple to do, first define your custom property on your Model
and then use the **@renders** decorator to tell the framework to map you class method
with a certain Model property::

    
    from flask_appbuilder.models.decorators import renders

    class MyModel(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique = True, nullable=False)
        custom = Column(Integer(20))
                
        @renders('custom')
        def my_custom(self):
        # will render this columns as bold on ListWidget
            return Markup('<b>' + custom + '</b>')


On your view reference your method as a column on list::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyTable)
        list_columns = ['name', 'my_custom']


Base Filtering
--------------

To filter a views data, just set the *base_filter* property with your base filters. These will allways be applied first on any search.

It's very flexible, you can apply multiple filters with static values, or values based on a function you define.
On this next example we are filtering a view by the logged in user and with column *name* starting with "a"

*base_filters* is a list of lists with 3 values [['column name',FilterClass,'filter value],...]::


    from flask import g
    from flask_appbuilder import ModelView
    from flask_appbuilder.models.sqla.interface import SQLAInterface
    from flask_appbuilder.models.sqla.filters import FilterEqualFunction, FilterStartsWith
    # If you're using Mongo Engine you should import filters like this, everything else is exactly the same
    # from flask_appbuilder.models.mongoengine.filters import FilterStartsWith, FilterEqualFunction

    from .models import MyTable


    def get_user():
        return g.user


    class MyView(ModelView):
        datamodel = SQLAInterface(MyTable)
        base_filters = [['created_by', FilterEqualFunction, get_user],
                        ['name', FilterStartsWith, 'a']]

Since version 1.5.0 you can use base_filter with dotted notation, necessary joins will be handled for you on
the background. Study the following example to see how:

https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/extendsecurity


Default Order
-------------

Use a default order on your lists, this can be overridden by the user on the UI.
Data structure ('col_name':'asc|desc')::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyTable)
        base_order = ('my_col_to_be_ordered','asc')


Template Extra Arguments
------------------------

You can pass extra Jinja2 arguments to your custom template, using extra_args property::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyTable)
        extra_args = {'my_extra_arg':'SOMEVALUE'}
        show_template = 'my_show_template.html'

Your overriding the 'show' template to handle your extra argument.
You can still use F.A.B. show template using Jinja2 blocks, take a look at the :doc:`templates` chapter

Forms - Override automatic form creation
----------------------------------------

Define your own Add, Edit forms using WTForms to override the automatic form creation::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        add_form = AddFormWTF


Forms - Add or remove fields
----------------------------

Define what columns will be included on Add or Edit forms,
for example if you have automatic fields like user or date, you can remove them from the Add Form::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        add_columns = ['my_field1', 'my_field2']
        edit_columns = ['my_field1']

To contribute with any additional fields that are not on a table/model,
for example a confirmation field::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_extra_fields = {
            'extra': TextField(gettext('Extra Field'),
            description=gettext('Extra Field description'),
            widget=BS3TextFieldWidget())
        }

Forms - Readonly fields
----------------------------

Define/override readonly fields like this, first define a new **Readonly** field::

    from flask_appbuilder.fieldwidgets import BS3TextFieldWidget


    class BS3TextFieldROWidget(BS3TextFieldWidget):
        def __call__(self, field, **kwargs):
            kwargs['readonly'] = 'true'
            return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)


Next override your field using your new widget::

    class ExampleView(ModelView):
        datamodel = SQLAInterface(ExampleModel)
        edit_form_extra_fields = {
            'field2': TextField('field2', widget=BS3TextFieldROWidget())
        }

Readonly select fields are a special case, but it's solved in a simpler way::

    # Define the field query
    def department_query():
        return db.session.query(Department)


    class EmployeeView(ModelView):
        datamodel = SQLAInterface(Employee)

        list_columns = ['employee_number', 'full_name', 'department']

        # override the 'department' field, to make it readonly on edit form
        edit_form_extra_fields = {
            'department':  QuerySelectField(
                                'Department',
                                query_factory=department_query,
                                widget=Select2Widget(extra_classes="readonly")
                           )
        }

Forms - Custom validation rules
-------------------------------

Contribute with your own additional form validations rules.
Remember FAB will automatically validate any field that is defined on the database
with *Not Null* (Required) or Unique constraints::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        validators_columns = {
            'my_field1':[EqualTo('my_field2', message=gettext('fields must match'))]
        }


Forms - Custom query on related fields
--------------------------------------

You can create a custom query filter for all related columns like this::

    from flask_appbuilder.models.sqla.filters import FilterStartsWith


    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_query_rel_fields = {'group': [['name', FilterStartsWith, 'W']]}


This will filter list combo on Contact's model related with ContactGroup model.
The combo will be filtered with entries that start with W.
You can define individual filters for add,edit and search using **add_form_quey_rel_fields**,
**edit_form_query_rel_fields**, **search_form_query_rel_fields** respectively. Take a look at the :doc:`api`
If you want to filter multiple related fields just add new keys to the dictionary,
remember you can add multiple filters for each field also, take a look at the *base_filter* property::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_query_rel_fields = {
            'group': [['name', FilterStartsWith, 'W']],
            'gender': [['name', FilterStartsWith, 'M']]
        }

Forms - Related fields
----------------------

To use AJAX select2 (combo) fields and make use of the REST API, by default all fields are previously populated on the server.
Here's a simple example::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)

        add_form_extra_fields = {
            'contact_group': AJAXSelectField(
                                'contact_group',
                                description='This will be populated with AJAX',
                                datamodel=datamodel,
                                col_name='contact_group',
                                widget=Select2AJAXWidget(endpoint='/contactmodelview/api/column/add/contact_group')
                             ),
        }


Even better you can (since 1.7.0) create related select2 fields, if you have two (or more) relationships that are
related them self's, like a group and subgroup on a contact, when the user selects the group the second select2 combo
will be populated with the subgroup values that belong to the group. Extending the previous example::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)

        add_form_extra_fields = {
                        'contact_group': AJAXSelectField('contact_group',
                        description='This will be populated with AJAX',
                        datamodel=datamodel,
                        col_name='contact_group',
                        widget=Select2AJAXWidget(endpoint='/contactmodelview/api/column/add/contact_group')),

                        'contact_sub_group': AJAXSelectField('Extra Field2',
                        description='Extra Field description',
                        datamodel=datamodel,
                        col_name='contact_sub_group',
                        widget=Select2SlaveAJAXWidget(master_id='contact_group',
                        endpoint='/contactmodelview/api/column/add/contact_sub_group?_flt_0_contact_group_id={{ID}}'))
                        }


So as seen before add_form_extra_fields is a dictionary that expects keys as column names and values as WTF Fields.

AJAXSelectField is expecting the following parameters for the constructor:
- label: A label for the column.
- description: A description to render on the form.
- datamodel: SQLAlchemy initialized with the model.
- col_name: The column name.
- widget: Use Select2AJAXWidget (for the master) and Select2SlaveAJAXWidget for the slave.
- endpoint: The REST API that will be used to populate the select2.

You have 3 endpoint's API that will return data ready to use by this fields:

- /<YOUR MODELVIEW NAME>/api/column/add|edit/<COLUMN NAME> : you can append query string's to filter data. This will return all values of the related column on the model.
- /<YOUR MODELVIEW NAME>/api/readvalues: This will return all values on the modelview prepared to be used on a select2.

