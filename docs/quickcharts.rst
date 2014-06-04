Chart Views (Quick How to)
==========================

To implement views with google charts, use all inherited classes from BaseChartView, these are:

 :DirectChartView: Display direct data charts with multiple series, no group by is applied.
 :GroupByChartView: Displays grouped data with multiple series.
 :ChartView: (Deprecated) Display simple group by method charts.
 :TimeChartView: (Deprecated) Displays simple group by month and year charts.

Direct Data Charts
------------------

These charts can display multiple series, based on columns from models or functions defined on the models.
You can display multiple charts on the same view.

Let's create a simple model first, the gold is to display a chart showing the unemployment evolution
versus the percentage of the population with higher education::

    class CountryStats(Model):
        id = Column(Integer, primary_key=True)
        stat_date = Column(Date, nullable=True)
        population = Column(Float)
        unemployed_perc = Column(Float)
        poor_perc = Column(Float)
        college = Column(Float)

Let's suppose that the college field will have the total number of college students on some date.
But the *unemployed_perc* field holds a percentage, we can't draw a chart with these two together,
we must create a function that calculated the *college_perc*::

        def college_perc(self):
            if self.population != 0:
                return (self.college*100)/self.population
            else
                return 0.0

Now we are ready to define our view::

    class CountryDirectChartView(DirectByChartView):
        datamodel = SQLAModel(CountryStats)
        chart_title = 'Direct Data Example'

        definitions = [
        {
            'label': 'Unemployment',
            'group': 'stat_date',
            'series': ['unemployed_perc',
                       'college_perc'
        }
    ]

This kind of chart inherits from **BaseChartView** that has some properties that you can configure
these are:

    :chart_title: The Title of the chart (can be used with babel of course).
    :group_by_label: The label that will be displayed before the buttons for choosing the chart.
    :chart_type: The chart type PieChart, ColumnChart or LineChart
    :chart_3d: = True or false label like: 'true'
    :width: The charts width
    :height: The charts height

Additionally you can configure **BaseModelView** properties because **BaseChartView** is a child.
The most interesting one is

    :base_filters: Defines the filters for data, this has precedence from all UI filters.


(Deprecated) Define your Chart Views (views.py)
-----------------------------------------------

::

    class ContactChartView(ChartView):
        search_columns = ['name','group']
        datamodel = SQLAModel(Contact)
        chart_title = 'Grouped contacts'
        label_columns = ContactModelView.label_columns
        group_by_columns = ['group']
    	
Notice that:

:label_columns: Are the labels that will be displayed instead of the model's columns name. In this case they are the same labels from ContactModelView.
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
        label_columns = ContactModelView.label_columns
        group_by_columns = ['birthday']
        datamodel = SQLAModel(Contact)

this will produce a column chart, with the number of contacts that were born on a particular month or year.
Notice that the label_columns are from and already defined *ContactModelView* take a look at the :doc:`quickhowto`

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

Take look at a more detailed example on `quickcharts <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickcharts>`_.

Register (views.py)
-------------------

Register everything, to present your charts and create the menu::

    appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-envelope", category="Contacts")
    appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Take a look at the :doc:`api`. For additional customization

.. note::
    You can use charts has related views also, just add them on your related_views properties.

Some images:

.. image:: ./images/chart.png
    :width: 100%

.. image:: ./images/chart_time1.png
    :width: 100%

.. image:: ./images/chart_time2.png
    :width: 100%
