Quick Charts
============

To implement views with google charts derive from ChartsViews like this::

Define your Chart Views (views.py)
----------------------------------

::

    class ContactChartView(ChartView):
    	
        datamodel = SQLAModel(Contact, db.session)
        chart_title = 'Grouped contacts'
        label_columns = ContactGeneralView.label_columns
        group_by_columns = ['group']
    	
Notice that:

:label_columns: were the ones used on ContactGeneralView
:group_by_columns: is a list of columns that you want to group

this will produce a Pie chart, with the percentage of contacts by group.
If you want a column chart just override this::

	chart_type = 'PieChart' # default
	chart_type = 'ColumnsChart'


How about a chart grouped by a time frame? This is new on 0.2.0::

    class ContactTimeChartView(TimeChartView):
    
        chart_title = 'Grouped Birth contacts'
        label_columns = ContactGeneralView.label_columns
        group_by_columns = ['birthday']
        datamodel = SQLAModel(Contact, db.session)

this will produce a column chart, with the number of contacts that have borned on a particular month or year.

Register (views.py)
-------------------

Register everything, to present your charts and create the menu::

    genapp.add_view(ContactChartView(), "Contacts Chart","/contactchartview/chart","signal","Contacts")
    genapp.add_view(ContactTimeChartView(), "Contacts Birth Chart","/contacttimechartview/chart/month","signal","Contacts")

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Some images:

.. image:: ./images/chart.png
    :width: 100%

.. image:: ./images/chart_time1.png
    :width: 100%

.. image:: ./images/chart_time2.png
    :width: 100%
