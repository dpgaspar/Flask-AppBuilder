REST Api
========

On this chapter we are going to describe how you can define a RESTfull API
using almost the same concept as defining your MVC views.

:note:
    Follow this example on Flask-AppBuilder project ./examples/base_api/

First let's see a basic example on how you can define your own
custom API endpoints::


    from flask_appbuilder.api import BaseApi, expose
    from . import appbuilder


    class MyFirstApi(BaseApi):
        @expose('/greeting')
        def greeting(self):
            return self.response(200, message="Hello")


    appbuilder.add_view_no_menu(MyFirstApi)


On the previous example, we are exposing an HTTP GET endpoint,
that returns the following JSON payload::


    {
        "message": "Hello"
    }

The ``@expose`` decorator registers your class method as a Flask route that is going
to be associated with a Flask blueprint. A ``BaseApi`` class defines a blueprint that
contains all exposed methods. By default the base route of the class blueprint is
defined by:

/api/v1/<LOWERCASE_CLASS_NAME>

So we can make a request to our method using::

    $ curl http://localhost:8080/api/v1/myfirstapi/greeting

To override the base route class blueprint, override the ``base_route`` property,
so on our previous example::

    from flask_appbuilder.api import BaseApi, expose
    from . import appbuilder


    class MyFirstApi(BaseApi):

        base_route = '/newapi/v2/nice'

        @expose('/greeting')
        def greeting(self):
            return self.response(200, message="Hello")


    appbuilder.add_view_no_menu(MyFirstApi)

Now our endpoint will be::

    $ curl http://localhost:8080/newapi/v2/nice/greeting

We can also just override the version and/or resource name,
using ``version`` and ``resource_name`` properties::

    from flask_appbuilder.api import BaseApi, expose
    from . import appbuilder


    class MyFirstApi(BaseApi):

        resource_name = 'nice'

        @expose('/greeting')
        def greeting(self):
            return self.response(200, message="Hello")


    appbuilder.add_view_no_menu(MyFirstApi)

Now our endpoint will be::

    $ curl http://localhost:8080/api/v1/nice/greeting


The other HTTP methods (PUT, POST, DELETE, ...) can be defined just like
a Flask route signature::

    from flask import request
    from flask_appbuilder.api import BaseApi, expose

    class MyFirstApi(BaseApi):

        ....

        @expose('/greeting2', methods=['POST', 'GET'])
        def greeting2(self):
            if request.method == 'GET':
                return self.response(200, message="Hello (GET)")
            return self.response(201, message="Hello (POST)")

The previous example will expose a new `greeting2` endpoint on HTTP GET and POST
so we can request it by::

    $ curl http://localhost:8080/api/v1/myfirstapi/greeting2
    {
        "message": "Hello (GET)"
    }
    $ curl -XPOST http://localhost:8080/api/v1/myfirstapi/greeting2
    {
        "message": "Hello (POST)"
    }

Let's make our method a bit more interesting, and send our name on the HTTP
GET method. You can optionally use a ``@rison`` decorator that will parse
the HTTP URI arguments from a *Rison* structure to a python data structure.
On this example it may seem a bit overboard but with *Rison* we can handle
complex HTTP GET arguments in a human readable and predictable way.
*Rison* is a slight variation of JSON that looks vastly superior after URI encoding.
Rison still expresses exactly the same set of data structures as JSON,
so data can be translated back and forth without loss or guesswork::

    from flask_appbuilder.api import BaseApi, expose, rison

    class MyFirstApi(BaseApi):

        ...

        @expose('/greeting3')
        @rison
        def greeting3(self, **kwargs):
            if 'name' in kwargs['rison']:
                return self.response(
                    200,
                    message="Hello {}".format(kwargs['rison']['name'])
                )
            return self.response_400(message="Please send your name")

And to test our method::

    $ curl 'http://localhost:8080/api/v1/myfirstapi/greeting3?q=(name:daniel)'
    {
        "message": "Hello daniel"
    }

To test this concept let's create a new method where we send a somewhat complex
data structure that will use numbers, booleans and lists, and send it back JSON formatted.
First our data structure, let's first think JSON::

    {
        "bool": true,
        "list": ["a", "b", "c"],
        "number": 777,
        "string": "string"
        "null": null
    }

On *Rison* format::

    (bool:!t,list:!(a,b,c),null:!n,number:777,string:'string')

Behind the scenes FAB is using *prison* a very nicely done fork developed by @betodealmeida
We can use this package, to help us dump or load python structures to Rison::

    import prison
    b = {
        "bool": True,
        "list": ["a", "b", "c"],
        "number": 777,
        "string": "string",
        "null": None
    }

    print(prison.dumps(b))

So to test our concept::

    ...

    @expose('/risonjson')
    @rison
    def rison_json(self, **kwargs):
        return self.response(200, result=kwargs['rison'])

Then call it::

    $ curl 'http://localhost:8080/api/v1/myfirstapi/risonjson?q=(bool:!t,list:!(a,b,c),null:!n,number:777,string:'string')'
    {
      "result": {
        "bool": true,
        "list": [
          "a",
          "b",
          "c"
        ],
        "null": null,
        "number": 777,
        "string": "string"
      }
    }


Notice how the data types are preserved. Remember that we are building a Flask app
so you can always use *normal* URI arguments using Flask's ``request.args``

If we send an invalid *Rison* argument we get an error::

    $ curl -v 'http://localhost:8080/api/v1/myfirstapi/risonjson?q=(bool:!t'
    ...
    < HTTP/1.0 400 BAD REQUEST
    < Content-Type: application/json; charset=utf-8
    ...
    {
      "message": "Not valid rison argument"
    }

Finally to properly handle all possible exceptions use the ``safe`` decorator,
that will catch all uncaught exceptions for you and return a proper error response.
You can enable or disable stack trace response using the
``FAB_API_SHOW_STACKTRACE`` configuration key::

        from flask_appbuilder.api import BaseApi, expose, rison, safe

        ...

        @expose('/error')
        @safe
        def error(self):
            raise Exception


Security
--------

FAB offers user management, several authentication backends and granular role base access
so we can use these features on the API also. Default API authentication method is done
using JSON Web Tokens (JWT).

:tip:

    FAB's JWT authentication is done with flask-jwt-extended.
    Checkout it's documentation for custom configuration:
    https://flask-jwt-extended.readthedocs.io/en/latest/options.html

Next, let's see how to create a private method::

    from flask import request
    from flask_appbuilder.api import BaseApi, expose, rison
    from flask_appbuilder.security.decorators import protect
    from . import appbuilder


    class MyFirstApi(BaseApi):

        ...
        @expose('/private')
        @protect
        def rison_json(self):
            return self.response(200, message="This is private")


    appbuilder.add_view_no_menu(MyFirstApi)

Accessing this method as expected will
return an HTTP 401 not authorized code and message::

    $ curl -v 'http://localhost:8080/api/v1/myfirstapi/private'
    ...
    < HTTP/1.0 401 UNAUTHORIZED
    < Content-Type: application/json
    ...
    {
      "msg": "Missing Authorization Header"
    }

So we need to first obtain our JSON Web token, for this, FAB registers a login endpoint.
For this we POST request with a JSON payload using::

    {
        "username": "<USERNAME>",
        "password": "<PASSWORD>",
        "provider": "db|ldap"
    }

Notice the *provider* argument, FAB currently supports DB and LDAP
authentication backends for the Api.

Let's request our Token then::

    # If not already, create an admin user
    $ fabmanager create-admin
    Username [admin]:
    User first name [admin]:
    User last name [user]:
    Email [admin@fab.org]:
    Password:
    Repeat for confirmation:
    ...
    Admin User admin created.

    # Login to obtain a token
    $ curl -XPOST http://localhost:8080/api/v1/security/login -d \
      '{"username": "admin", "password": "password", "provider": "db"}' \
      -H "Content-Type: application/json"
    {
      "access_token": "<SOME TOKEN>"
    }
    # It's nice to use the Token as an env var
    $ export TOKEN="<SOME TOKEN>"

Next we can use our token on protected endpoints::

    $ curl 'http://localhost:8080/api/v1/myfirstapi/private' -H "Authorization: Bearer $TOKEN"
    {
      "message": "This is private"
    }

As always FAB created a new **can_private** permission
on the DB and as associated it to the *Admin* Role.
So the Admin role as a new permission on
a view named "can private on MyFirstApi"
Note that you can protect all your methods and make
them public or not by adding them to the *Public* Role.

Also to restrict the default permissions we can use ``base_permissions``
list property. This can be specially useful on ``ModelRestApi`` (up next)
where we can restrict our Api resources to be read only, or only allow POST
methods::

    class MyFirstApi(BaseApi):
        base_permissions = ['can_private']


Model REST Api
--------------

To automatically create a RESTfull CRUD Api from a database *Model*, use ``ModelRestApi`` class and
define it almost like an MVC ``ModelView``. This class will expose the following REST endpoints

    .. cssclass:: table-bordered table-hover

+-----------------------------+-------------------------------------------------------+-----------------+--------+
| URL                         | Description                                           | Permission Name | HTTP   |
+=============================+=======================================================+=================+========+
| /_info                      | Returns info about the CRUD model and security        | can_get         | GET    |
+-----------------------------+-------------------------------------------------------+-----------------+--------+
| /                           | Queries models data, receives args as Rison           | can_get         | GET    |
+-----------------------------+-------------------------------------------------------+-----------------+--------+
| /<PK>                       | Returns a single model from it's primary key (id)     | can_get         | GET    |
+-----------------------------+-------------------------------------------------------+-----------------+--------+
| /                           | Receives a JSON payload as POST and creates record    | can_post        | POST   |
+-----------------------------+-------------------------------------------------------+-----------------+--------+
| /                           | Receives a JSON payload as PUT and updates record     | can_put         | PUT    |
+-----------------------------+-------------------------------------------------------+-----------------+--------+
| /<PK>                       | Deletes a single model from it's primary key (id)     | can_delete      | DELETE |
+-----------------------------+-------------------------------------------------------+-----------------+--------+

For each ``ModelRestApi`` you will get 5 CRUD endpoints and an extra information method.
Let's dive into a simple example using the quickhowto.
The quickhowto example as a Contact's Model and a Group Model, so each Contact belongs to a Group.

First let's define a CRUD REST Api for our Group model resource::

    from flask_appbuilder.models.sqla.interface import SQLAInterface
    from flask_appbuilder.api import ModelRestApi
    from . import appbuilder


    class GroupModelRestApi(ModelRestApi):
        resource_name = 'group'
        datamodel = SQLAInterface(ContactGroup)

    appbuilder.add_view_no_menu(MyFirstApi)

Behind the scenes FAB uses marshmallow-sqlalchemy to infer the Model to a Marshmallow Schema,
that can be safely serialized and deserialized. Let's recall our Model definition for ``ContactGroup``::

    class ContactGroup(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True, nullable=False)

        def __repr__(self):
            return self.name


All endpoints are protected so we need to request a JWT and use it on our REST resource,
like shown before we need to make a PUT request to the login API endpoint::

    # Login to obtain a token
    $ curl -XPOST http://localhost:8080/api/v1/security/login -d \
      '{"username": "admin", "password": "password", "provider": "db"}' \
      -H "Content-Type: application/json"
    {
      "access_token": "<SOME TOKEN>"
    }
    # It's nice to use the Token as an env var
    $ export TOKEN="<SOME TOKEN>"

First let's create a Group::

    $ curl -XPOST http://localhost:8080/api/v1/group/ -d \
     '{"name": "Friends"}' \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN"
    {
      "id": 1,
      "result": {
        "name": "Friends"
      }
    }

We got back a response with the model id and result with the inserted data.
Now let's query our newly created Group::

    $ curl http://localhost:8080/api/v1/group/1 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN"

    {
      "description_columns": {},
      "include_columns": [
        "name"
      ],
      "label_columns": {
        "name": "Name"
      },
      "id": "1",
      "result": {
        "name": "Friends"
      }
    }

As you can see, the API returns the model data, and extra meta data so you can properly render
a page with labels, descriptions and defined column order. This way it should be possible
to develop a React component (for example) that renders any model just by switching between HTTP endpoints.
It's also possible to just ask for certain meta data keys, we will talk about this later.

Next let's change our newly created model (HTTP PUT)::

    $ curl -XPUT http://localhost:8080/api/v1/group/1 -d \
     '{"name": "Friends Changed"}' \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN"
    {
      "result": {
        "name": "Friends Changed"
      }
    }

And finally test the delete method (HTTP DELETE)::

    $ curl -XDELETE http://localhost:8080/api/v1/group/1 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN"
    {
      "message": "OK"
    }

Let's check if it exists (HTTP GET)::

    $ curl http://localhost:8080/api/v1/group/1 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN"
    {
      "message": "Not found"
    }


We get an HTTP 404 (Not found).

Validation and Custom Validation
--------------------------------

Notice that by using marshmallow with SQLAlchemy,
we are validating field size, type and required fields out of the box.
This is done by marshmallow-sqlalchemy that automatically creates ModelSchema's
inferred from our SQLAlchemy Models.
But you can always use your own defined Marshmallow schemas independently
for add, edit, list and show endpoints.

A validation error for PUT and POST methods returns HTTP 400 and the following JSON data::

    {
        "message": {
            "<COL_NAME>": [
                "<ERROR_MESSAGE>",
                ...
            ],
            ...
        }
    }

Next we will test some basic validation, first the field type
by sending a name that is a number::

    $ curl XPOST http://localhost:8080/api/v1/group/ -d \
    '{"name": 1234}' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "message": {
        "name": [
          "Not a valid string."
        ]
      }
    }

And we get an HTTP 400 (Bad request).

How to add custom validation? On our next example we only allow
group names that start with a capital "A"::

    from marshmallow import Schema, fields, ValidationError, post_load


    def validate_name(n):
        if n[0] != 'A':
            raise ValidationError('Name must start with an A')

    class GroupCustomSchema(Schema):
        name = fields.Str(validate=validate_name)

        @post_load
        def process(self, data):
            return ContactGroup(**data)

Then on our Api class::

    class GroupModelRestApi(ModelRestApi):
        resource_name = 'group'
        add_model_schema = GroupCustomSchema()
        edit_model_schema = GroupCustomSchema()
        datamodel = SQLAInterface(ContactGroup)

Let's try it out::

    $ curl -v XPOST http://localhost:8080/api/v1/group/ -d \
    '{"name": "BOLA"}' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "message": {
        "name": [
          "Name must start with an A"
        ]
      }
    }

Information endpoint
--------------------

This endpoint serves as a method to fetch meta information about our CRUD
methods. Again the main purpose to serve meta data is to make possible for a frontend
layer to be able to render dynamically:

- Search options

- Forms

- Enable/disable features based on permissions.

First a birds eye view from the output of the **_info** endpoint::

    {
        "add_fields": [...],
        "edit_fields": [...],
        "filters": {...},
        "permissions": [...]
    }

Let's drill down this data structure, ``add_fields`` and ``edit_fields`` are similar
and serve to aid on rendering forms for add and edit so their response contains the
following data structure::

    {
        "add_fields": [
            {
                "description": "<COL_DESCRIPTION>",
                "label": "<COL_LABEL>",
                "name": "<COL_NAME>",
                "required": true|false,
                "type": "String|Integer|Related|RelatedList|...",
                "validate": [ ... list of validation methods ... ]
                "values" : [ ... optional with all possible values for a related field ... ]
            },
            ...
        ]
    }

Edit fields ``edit_fields`` is similar, but it's content may be different, since
we can configure it in a distinct way

Next, filters, this returns all the necessary info to render all possible filters allowed
by the backend database for each field on the model::

    {
        "filters": {
            "<COL_NAME>": [
                {
                    "name": "<HUMAN READABLE AND I18N>",
                    "operator": "<OPERATION_NAME>"
                },
                ...
            ],
            ...
        }
    }

Note that the **operator** value can be used to filter our list queries,
more about this later.

Finally the permissions, this declares all allowed permissions for the current user.
Remember that these can extend the automatic HTTP methods generated by ``ModelRestApi``
by just defining new methods and protecting them with the ``protect`` decorator::

    {
        "permissions": ["can_get", "can_put", ... ]
    }

On all GET HTTP methods we can select which meta data keys we want, this can
be done using *Rison* URI arguments. So the **_info** endpoint is no exception.
The across the board way to filter meta data is to send a GET request
using the following structure::

    {
        "keys": [ ... LIST OF META DATA KEYS ... ]
    }

That translates to the following in *Rison* for fetching just the permissions meta data::

    (keys:!(permissions))

So, back to our example::

    $ curl 'http://localhost:8080/api/v1/group/_info?q=(keys:!(permissions))' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "permissions": [
        "can_get",
        "can_post",
        "can_put",
        "can_delete"
      ]
    }

And to fetch the permissions and Add form fields info::

    $ curl 'http://localhost:8080/api/v1/group/_info?q=(keys:!(permissions,add_fields))' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "add_fields": [ ... ],
      "permissions": [
        "can_get",
        "can_post",
        "can_put",
        "can_delete"
      ]
    }

To fetch meta data with internationalization use **_l_** URI key argument with i18n
country code as the value. This will work on any HTTP GET endpoint::

    $ curl 'http://localhost:8080/api/v1/group/_info?q=(keys:!(permissions,add_fields))&_l_=pt' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "add_fields": [ ... ],
      "permissions": [
        "can_get",
        "can_post",
        "can_put",
        "can_delete"
      ]
    }

Render meta data with *Portuguese*, labels, description, filters

The ``add_fields`` and ``edit_fields`` keys also render all possible
values from related fields, using our *quickhowto* example::

    {
        "add_fields": [
            {
              "description": "",
              "label": "Gender",
              "name": "gender",
              "required": false,
              "type": "Related",
              "values": [
                {
                  "id": 1,
                  "value": "Male"
                },
                {
                  "id": 2,
                  "value": "Female"
                }
              ]
            },
            ...
        ]
    }

These related field values can be filtered server side using the ``add_query_rel_fields``
or ``edit_query_rel_fields``::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        add_query_rel_fields = {
            'gender': [['name', FilterStartsWith, 'F']]
        }

The previous example will filter out only the **Female** gender from our list
of possible values

We can also restrict server side the available fields for add and edit using ``add_columns``
and ``edit_columns``. Additionally you can use ``add_exclude_columns`` and ``edit_exclude_columns``::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        add_columns = ['name']

Will only return the field *name* from our *Contact* model information endpoint for ``add_fields``

Get Item
--------

The get item endpoint is very simple, and was already covered to some extent.
The response data structure is::

    {
        "id": "<Primary Key>"
        "description_columnns": {},
        "label_columns": {},
        "include_columns": [],
        "result": {}
    }

Now we are going to cover the *Rison* arguments for custom fetching
meta data keys or columns. This time the accepted arguments is slightly extended::

    {
        "keys": [ ... List of meta data keys to return ... ],
        "columns": [ ... List of columns to return ... ]
    }

So for fetching only the *name* and *address* for a certain *Contact*, using *Rison*::

    (columns:!(name,address))

Our *curl* command will look like::

    curl 'http://localhost:8080/api/v1/contact/1?q=(columns:!(name,address))' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "description_columns": {},
      "id": "1",
      "include_columns": [
        "name",
        "address"
      ],
      "label_columns": {
        "address": "Address",
        "name": "Name"
      },
      "result": {
        "address": "Street phoung",
        "name": "Wilko Kamboh"
      }
    }

And to only include the *label_columns* meta data, *Rison* data structure::

    (columns:!(name,address),keys:!(label_columns))

Our *curl* command will look like::

    curl 'http://localhost:8080/api/v1/contact/1?q=(columns:!(name,address),keys:!(label_columns))' \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN"
    {
      "id": "1",
      "label_columns": {
        "address": "Address",
        "name": "Name"
      },
      "result": {
        "address": "Street phoung",
        "name": "Wilko Kamboh"
      }
    }

We can restrict or add fields for the get item endpoint using
the ``show_columns`` property. This takes precedence from the *Rison* arguments::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        show_columns = ['name']

We can add fields that are python functions also, for this on the SQLAlchemy definition,
let's add a new function::

    class Contact(Model):
        id = Column(Integer, primary_key=True)
        name = Column(String(150), unique=True, nullable=False)
        address = Column(String(564))
        birthday = Column(Date, nullable=True)
        personal_phone = Column(String(20))
        personal_celphone = Column(String(20))
        contact_group_id = Column(Integer, ForeignKey('contact_group.id'), nullable=False)
        contact_group = relationship("ContactGroup")
        gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
        gender = relationship("Gender")

        def __repr__(self):
            return self.name

        def some_function(self):
            return "Hello {}".format(self.name)

And then on the REST API::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        show_columns = ['name', 'some_function']

The ``show_columns`` is also useful to impose an order on the columns.
Again this is useful to develop a dynamic frontend show item page/component
by using the *include_columns* meta data key.

Note that this can be done on the query list endpoint also using ``list_columns``

Lists and Queries
-----------------

Finally for our last HTTP endpoint, and the most feature rich.
The response data structure is::

    {
        "count": <RESULT_COUNT">
        "ids": [ ... List of PK's ordered by result ... ],
        "description_columnns": {},
        "label_columns": {},
        "list_columns": [ ... An ordered list of columns ...],
        "order_columns": [ ... List of columns that can be ordered ... ],
        "result": {}
    }

As before meta data can be chosen using *Rison* arguments::

    (keys:!(label_columns))

Will only fetch the *label_columns* meta data key

And we can choose which columns to fetch::

    (columns:!(name,address))

To reduce or extend the default inferred columns from our *Model*.
On server side we can use the ``list_columns`` property,
this takes precedence over *Rison* arguments::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        list_columns = ['name', 'address']

For ordering the results, the following will order contacts by name descending Z..A::

    (order_column:name,order_direction:desc)

To set a default order server side use ``base_order`` tuple::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        base_order = ('name', 'desc')

Pagination, get the second page using page size of two (just an example)::

    (page:2,page_size:2)

To set the default page size server side::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        page_size = 20

And last, but not least, *filters*. The query *filters* data structure::

    {
        "filters": [
            {
                "col": <COL_NAME>,
                "opr": <Operation type>,
                "value": <VALUE>
            },
            ...
        ]
    }

All filters are **AND** operations. We can filter by several column names
using different operations, so using *Rison*::

    (filters:!((col:name,opr:sw,value:a),(col:name,opr:ew,value:z)))

The previous filter will query all contacts whose **name** starts with "a" and ends with "z".
The possible operations for each field can be obtained from the information endpoint.
FAB can filter your models by any field type and all possible operations

Note that all *Rison* arguments can be used alone or in combination::

    (filters:!((col:name,opr:sw,value:a),(col:name,opr:ew,value:z)),columns:!(name),order_columns:name,order_direction:desc)

Will filter all contacts whose **name** starts with "a" and ends with "z", using descending name order by, and
just fetching the **name** column.

To impose base filters server side::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        base_filters = [['name', FilterStartsWith, 'A']]

The filter will act on all HTTP endpoints, protecting delete, create, update and display
operations

Simple example using doted notation, FAB will infer the necessary join operation::

    class ContactModelRestApi(ModelRestApi):
        resource_name = 'contact'
        datamodel = SQLAInterface(Contact)
        base_filters = [['contact_group.name', FilterStartsWith, 'F']]

Locks all contacts, to groups whose name starts with "F". Using the provided test data
on the quickhowto example, limits the contacts to family and friends.

