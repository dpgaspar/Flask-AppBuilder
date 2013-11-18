Quick Charts
============

To implement views with google charts derive from ChartsViews like this::

    class PersonChartView(ChartView):
        route_base = '/persons'
        chart_title = 'Grouped Persons'
        label_columns = PersonGeneralView.label_columns
        group_by_columns = ['group']
        datamodel = SQLAModel(Person, db.session)

You can find this example at: https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples/quickhowto

Some images:

.. image:: ./images/chart.png
    :width: 100%
