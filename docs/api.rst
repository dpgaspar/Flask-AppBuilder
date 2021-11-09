=============
API Reference
=============

flask_appbuilder
====================

AppBuilder
----------

.. automodule:: flask_appbuilder.base

    .. autoclass:: AppBuilder
        :members:

        .. automethod:: __init__

flask_appbuilder.security.decorators
========================================

.. automodule:: flask_appbuilder.security.decorators

    .. autofunction:: protect
    .. autofunction:: has_access
    .. autofunction:: permission_name

flask_appbuilder.models.decorators
========================================

.. automodule:: flask_appbuilder.models.decorators

    .. autofunction:: renders

flask_appbuilder.hooks
======================
.. automodule:: flask_appbuilder.hooks

    .. autofunction:: before_request

flask_appbuilder.api
==============================

.. automodule:: flask_appbuilder.api

    .. autofunction:: expose
    .. autofunction:: rison
    .. autofunction:: safe

BaseApi
-------

.. autoclass:: BaseApi
    :members:

ModelRestApi
------------

.. autoclass:: ModelRestApi
    :members:

flask_appbuilder.baseviews
==============================

.. automodule:: flask_appbuilder.baseviews

    .. autofunction:: expose

BaseView
--------

.. autoclass:: BaseView
    :members:

BaseFormView
------------

.. autoclass:: BaseFormView
    :members:

BaseModelView
-------------

.. autoclass:: BaseModelView
    :members:

BaseCRUDView
------------

.. autoclass:: BaseCRUDView
    :members:

flask_appbuilder.views
==========================

.. automodule:: flask_appbuilder.views

IndexView
---------

.. autoclass:: IndexView
    :members:

SimpleFormView
--------------

.. autoclass:: SimpleFormView
    :members:

PublicFormView
--------------

.. autoclass:: PublicFormView
    :members:

ModelView
-----------

.. autoclass:: ModelView
    :members:

MultipleView
----------------

.. autoclass:: MultipleView
    :members:

MasterDetailView
----------------

.. autoclass:: MasterDetailView
    :members:

CompactCRUDMixin
----------------

.. autoclass:: CompactCRUDMixin
    :members:

flask_appbuilder.actions
============================

.. automodule:: flask_appbuilder.actions

    .. autofunction:: action

flask_appbuilder.security
=============================

.. automodule:: flask_appbuilder.security.manager

BaseSecurityManager
-------------------

.. autoclass:: BaseSecurityManager
    :members:

BaseRegisterUser
----------------

.. automodule:: flask_appbuilder.security.registerviews

    .. autoclass:: BaseRegisterUser
        :members:

flask_appbuilder.filemanager
================================

.. automodule:: flask_appbuilder.filemanager

    .. autofunction:: get_file_original_name

Aggr Functions for Group By Charts
==================================

.. automodule:: flask_appbuilder.models.group

    .. autofunction:: aggregate_count
    .. autofunction:: aggregate_avg
    .. autofunction:: aggregate_sum

flask_appbuilder.charts.views
=================================

.. automodule:: flask_appbuilder.charts.views

BaseChartView
-------------

.. autoclass:: BaseChartView
    :members:

DirectByChartView
-----------------

.. autoclass:: DirectByChartView
    :members:

GroupByChartView
----------------

.. autoclass:: GroupByChartView
    :members:

(Deprecated) ChartView
----------------------

.. autoclass:: ChartView
    :members:

(Deprecated) TimeChartView
--------------------------

.. autoclass:: TimeChartView
    :members:

(Deprecated) DirectChartView
----------------------------

.. autoclass:: DirectChartView
    :members:


flask_appbuilder.models.mixins
==================================

.. automodule:: flask_appbuilder.models.mixins

    .. autoclass:: BaseMixin
        :members:

    .. autoclass:: AuditMixin
        :members:

Extra Columns
-------------

.. autoclass:: FileColumn
    :members:

.. autoclass:: ImageColumn
    :members:

Generic Data Source (Beta)
--------------------------

flask_appbuilder.models.generic
===================================

.. automodule:: flask_appbuilder.models.generic

    .. autoclass:: GenericColumn
        :members:

    .. autoclass:: GenericModel
        :members:

    .. autoclass:: GenericSession
        :members:
