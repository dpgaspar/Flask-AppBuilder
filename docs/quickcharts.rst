Quick Charts
============

To implement views with google charts derive from ChartsViews like this::

Define your Chart Views (views.py)
----------------------------------

::

    class PersonChartView(ChartView):
        route_base = '/persons'
        chart_title = 'Grouped Persons'
        label_columns = PersonGeneralView.label_columns
        group_by_columns = ['group']
        datamodel = SQLAModel(Person, db.session)
        
Register (views.py)
-------------------

Register everything, to present your charts and create the menu::

    genapp.add_view(ContactChartView, "Contacts Chart","/contacts/chart","earphone","Contacts")

This will present a view with the count of Persons grouped by groups. You can can add any columns
to "group_by_columns" as long as it makes sence to you.
You have two options with this chart, pie and columns you can set overriding::

	chart_type = 'PieChart' # default
	chart_type = 'ColumnsChart'

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Some images:

.. image:: ./images/chart.png
    :width: 100%
