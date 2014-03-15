Quick Charts
============

To implement views with google charts, use all derived class from BaseChartView, these are:

 :ChartView: Display simple group by method charts.
 :TimeChartView: Displays simple group by month and year charts.
 :DirectChartView: Display direct data charts, no group by is applied.

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

:label_columns: Are the labels that will be displayed instead of the model's columns name. In this case they are the same labels from ContactGeneralView.
:group_by_columns: Is a list of columns that you want to group.

this will produce a Pie chart, with the percentage of contacts by group.
If you want a column chart just define::

	chart_type = 'ColumnChart'

You can use 'BarChart', 'LineChart', 'AreaChart' the default is 'PieChart', take a look at the google charts documentation, the *chart_type* is the function on 'google.visualization' object

Let's define a chart grouped by a time frame?

::

    class ContactTimeChartView(TimeChartView):
        search_columns = ['name','group']
        chart_title = 'Grouped Birth contacts'
        label_columns = ContactGeneralView.label_columns
        group_by_columns = ['birthday']
        datamodel = SQLAModel(Contact, db.session)

this will produce a column chart, with the number of contacts that were born on a particular month or year.
Notice that the label_columns are from and already defined *ContactGeneralView* take a look at the :doc:`quickhowto`

Finally we will define a direct data chart

::

    class StatsChartView(DirectChartView):
        datamodel = SQLAModel(Stats)
        chart_title = lazy_gettext('Statistics')
        direct_columns = {'Some Stats': ('stat1', 'col1', 'col2'),
                        'Other Stats': ('stat2', 'col3')}

direct_columns is a dictionary you define to identify a label for your X column, and the Y columns (series) you want to include on the chart

This dictionary is composed by key and a tuple: {'KEY LABEL FOR X COL':('X COL','Y COL','Y2 COL',...),...}

Remember 'X COL', 'Ys COL' are identifying columns from the data model.

Register (views.py)
-------------------

Register everything, to present your charts and create the menu::

    baseapp.add_view(PersonGeneralView(), "List Contacts", icon="fa-envelope", category="Contacts")
    baseapp.add_view(PersonChartView(), "Contacts Chart", icon="fa-dashboard", category="Contacts")

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Take a look at the :doc:`api`. For additional customization


Some images:

.. image:: ./images/chart.png
    :width: 100%

.. image:: ./images/chart_time1.png
    :width: 100%

.. image:: ./images/chart_time2.png
    :width: 100%
