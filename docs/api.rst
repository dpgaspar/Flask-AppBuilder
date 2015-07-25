=============
API Reference
=============

flask.ext.appbuilder
====================

AppBuilder
----------

.. automodule:: flask.ext.appbuilder.base

    .. autoclass:: AppBuilder
        :members:
        
        .. automethod:: __init__

flask.ext.appbuilder.security.decorators
========================================

.. automodule:: flask.ext.appbuilder.security.decorators

    .. autofunction:: has_access
    .. autofunction:: permission_name

flask.ext.appbuilder.models.decorators
========================================

.. automodule:: flask.ext.appbuilder.models.decorators

    .. autofunction:: renders

flask.ext.appbuilder.baseviews
==============================

.. automodule:: flask.ext.appbuilder.baseviews

    .. autofunction:: expose

BaseView
--------

.. autoclass:: BaseView
    :members:

BaseModelView
-------------

.. autoclass:: BaseModelView
    :members:

BaseCRUDView
------------

.. autoclass:: BaseCRUDView
    :members:

flask.ext.appbuilder.views
==========================

.. automodule:: flask.ext.appbuilder.views

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

flask.ext.appbuilder.actions
============================

.. automodule:: flask.ext.appbuilder.actions

    .. autofunction:: action

flask.ext.appbuilder.security
=============================

.. automodule:: flask.ext.appbuilder.security.manager

BaseSecurityManager
-------------------

.. autoclass:: BaseSecurityManager
    :members:

BaseRegisterUser
----------------

.. automodule:: flask.ext.appbuilder.security.registerviews

    .. autoclass:: BaseRegisterUser
        :members:

flask.ext.appbuilder.filemanager
================================

.. automodule:: flask.ext.appbuilder.filemanager

    .. autofunction:: get_file_original_name

Aggr Functions for Group By Charts
==================================

.. automodule:: flask.ext.appbuilder.models.group

    .. autofunction:: aggregate_count
    .. autofunction:: aggregate_avg
    .. autofunction:: aggregate_sum

flask.ext.appbuilder.charts.views
=================================

.. automodule:: flask.ext.appbuilder.charts.views

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


flask.ext.appbuilder.models.mixins
==================================

.. automodule:: flask.ext.appbuilder.models.mixins

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

flask.ext.appbuilder.models.generic
===================================

.. automodule:: flask.ext.appbuilder.models.generic

    .. autoclass:: GenericColumn
        :members:

    .. autoclass:: GenericModel
        :members:

    .. autoclass:: GenericSession
        :members:
