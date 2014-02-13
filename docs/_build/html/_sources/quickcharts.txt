Quick Charts
============

To implement views with google charts inherit from ChartsViews like this

Define your Chart Views (views.py)
----------------------------------

::

    class ContactChartView(ChartView):
        search_columns = ['name','group']
        datamodel = SQLAModel(Contact, db.session)
        chart_title = 'Grouped contacts'
        label_columns = ContactGeneralView.label_columns
        group_by_columns = ['group']
    	
Notice that:

:label_columns: The same label's from ContactGeneralView.
:group_by_columns: Is a list of columns that you want to group.

this will produce a Pie chart, with the percentage of contacts by group.
If you want a column chart just override this::

	chart_type = 'PieChart' # default
	chart_type = 'ColumnsChart'


How about a chart grouped by a time frame? This is new on 0.2.0::

    class ContactTimeChartView(TimeChartView):
        search_columns = ['name','group']
        chart_title = 'Grouped Birth contacts'
        label_columns = ContactGeneralView.label_columns
        group_by_columns = ['birthday']
        datamodel = SQLAModel(Contact, db.session)

this will produce a column chart, with the number of contacts that were born on a particular month or year.

Register (views.py)
-------------------

Register everything, to present your charts and create the menu::

    genapp.add_view(ContactChartView(), "Contacts Chart","/contactchartview/chart","signal","Contacts")
    genapp.add_view(ContactTimeChartView(), "Contacts Birth Chart","/contacttimechartview/chart/month","signal","Contacts")

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Take a look at the :doc:`api`. For additional customization


Some images:

.. image:: ./images/chart.png
    :width: 100%

.. image:: ./images/chart_time1.png
    :width: 100%

.. image:: ./images/chart_time2.png
    :width: 100%
