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

Custom Model properties can be used on lists. This is usefull for formating values like currencies, time or dates.
or for custom HTML. This is very simple to do, first define your custom property on your Model
and use the **@renders** decorator to tell the framework to map you class method
with a certain Model property::

    
    from flask.ext.appbuilder.models.decorators import renders

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

It's very flexible, you can apply multiple filters with static values, or values based on a function you define. On this next example we are filtering a view by the logged in user and with column *name* starting with "a"

*base_filters* is a list of lists with 3 values [['column name',FilterClass,'filter value],...]

::
    from flask import g
    from flask.ext.appbuilder import ModelView
    from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
    from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction
    from .models import MyTable

    def get_user():
        return g.user

    class MyView(ModelView):
        datamodel = SQLAInterface(MyTable)
        base_filters = [['created_by', FilterEqualFunction, get_user],
                        ['name', FilterStartsWith, 'a']]


Default Order
-------------

Use a default order on your lists, this can be overridden by the user on the UI.
Data structure ('col_name':'asc|desc')

::

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

Forms
-----

- You can create a custom query filter for all related columns like this::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_query_rel_fields = {'group': [['name',FilterStartsWith,'W']]}


This will filter list combo on Contact's model related with ContactGroup model.
The combo will be filtered with entries that start with W.
You can define individual filters for add,edit and search using **add_form_quey_rel_fields**,
**edit_form_query_rel_fields**, **search_form_query_rel_fields** respectively. Take a look at the :doc:`api`
If you want to filter multiple related fields just add new keys to the dictionary,
remember you can add multiple filters for each field also, take a look at the *base_filter* property::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_query_rel_fields = {'group': [['name',FilterStartsWith,'W']],
                                    'gender': [['name',FilterStartsWith,'M']]}


- You can define your own Add, Edit forms to override the automatic form creation::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        add_form = AddFormWTF


- You can define what columns will be included on Add or Edit forms,
  for example if you have automatic fields like user or date, you can remove this from the Add Form::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        add_columns = ['my_field1','my_field2']
        edit_columns = ['my_field1']

- You can contribute with any additional fields that are not on a table/model,
  for example a confirmation field::

    class ContactModelView(ModelView):
        datamodel = SQLAInterface(Contact)
        add_form_extra_fields = {'extra': TextField(gettext('Extra Field'),
                        description=gettext('Extra Field description'),
                        widget=BS3TextFieldWidget())}


- You can define/override readonly fields like this, first define a new **Readonly** field::

    from flask_appbuilder.fieldwidgets import BS3TextFieldWidget

    class BS3TextFieldROWidget(BS3TextFieldWidget):
        def __call__(self, field, **kwargs):
            kwargs['readonly'] = 'true'
            return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)


Next override your field using your new widget::

    class ExampleView(ModelView):
        datamodel = SQLAInterface(ExampleModel)
        edit_form_extra_fields = {'field2': TextField('field2',
                                    widget=BS3TextFieldROWidget())}

For select fields to be readonly is a special case, but it's solved in a simpler way::

    # Define the field query
    def department_query():
        return db.session.query(Department)

    class EmployeeView(ModelView):
        datamodel = SQLAInterface(Employee)

        list_columns = ['employee_number', 'full_name', 'department']

        # override the 'department' field, to make it readonly on edit form
        edit_form_extra_fields = {'department':  QuerySelectField('Department',
                                    query_factory=department_query,
                                    widget=Select2Widget(extra_classes="readonly"))}


- You can contribute with your own additional form validations rules.
  Remember the framework will automatically validate any field that is defined on the database
  with *Not Null* (Required) or Unique constraints::

    class MyView(ModelView):
        datamodel = SQLAInterface(MyModel)
        validators_columns = {'my_field1':[EqualTo('my_field2',
                                            message=gettext('fields must match'))
                                          ]
        }

Take a look at the :doc:`api`. Experiment with *add_form*, *edit_form*, *add_columns*, *edit_columns*, *validators_columns*, *add_form_extra_fields*, *edit_form_extra_fields*
