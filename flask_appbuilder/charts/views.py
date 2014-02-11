import logging
from flask import render_template
from widgets import ChartWidget, MultipleChartWidget
from ..widgets import SearchWidget
from ..security.decorators import has_access
from ..baseviews import BaseModelView, expose
from ..urltools import *

log = logging.getLogger(__name__)


class BaseChartView(BaseModelView):
    """
        This is the base class for all chart views. 
        Use ChartView or TimeChartView, override their properties and these
        to customise your charts
    """

    chart_template = 'appbuilder/general/charts/chart.html'
    """ The chart template, override to implement your own """
    chart_widget = ChartWidget
    """ Chart widget override to implement your own """
    search_widget = SearchWidget
    """ Search widget override to implement your own """

    chart_title = 'Chart'
    """ A title to be displayed on the chart """
    default_view = 'chart'

    chart_type = 'PieChart'
    """ The chart type PieChart or ColumnChart """
    chart_3d = 'true'
    """ Will display in 3D? """
    width = 400
    """ The width """
    height = '400px'

    group_by_columns = []
    """ A list of columns to be possibly grouped by """

    group_bys = {}
    """ New for 0.6.4, on test """


    def __init__(self, **kwargs):
        super(BaseChartView, self).__init__(**kwargs)


    def _get_chart_widget(self, value_columns=[], widgets={}):
        widgets['chart'] = self.chart_widget(route_base=self.route_base,
                                             chart_title=self.chart_title,
                                             chart_type=self.chart_type,
                                             chart_3d=self.chart_3d,
                                             value_columns=value_columns)
        return widgets


class ChartView(BaseChartView):
    """
        Provides a simple (and hopefully nice) way to draw charts on your application.

        This will show Google Charts based on group by of your tables.                
    """

    @expose('/chart/')
    @has_access
    def chart(self):
        form = self.search_form.refresh()
        get_filter_args(self._filters)

        group_by = get_group_by_args()
        if group_by == '':
            group_by = self.group_by_columns[0]
        value_columns = self.datamodel.query_simple_group(group_by, filters=self._filters)

        widgets = self._get_chart_widget(value_columns=value_columns)
        widgets = self._get_search_widget(form=form, widgets=widgets)
        return render_template(self.chart_template, route_base=self.route_base,
                               title=self.chart_title,
                               label_columns=self.label_columns,
                               group_by_columns=self.group_by_columns,
                               height=self.height,
                               widgets=widgets,
                               baseapp=self.baseapp)


class TimeChartView(BaseChartView):
    """
        Provides a simple way to draw some time charts on your application.

        This will show Google Charts based on count and group by month and year for your tables.
    """

    chart_template = 'appbuilder/general/charts/chart_time.html'
    chart_type = 'ColumnChart'


    @expose('/chart/')
    @has_access
    def chart(self):
        form = self.search_form.refresh()
        get_filter_args(self._filters)
        group_by = get_group_by_args()
        group_by = group_by or self.group_by_columns[0]
        period = request.args.get('period')

        if group_by == '':
            group_by = self.group_by_columns[0]

        if period == 'month' or not period:
            log.debug("GROUO %s" % group_by)
            value_columns = self.datamodel.query_month_group(group_by, filters=self._filters)
        elif period == 'year':
            value_columns = self.datamodel.query_year_group(group_by, filters=self._filters)
        widgets = self._get_chart_widget(value_columns=value_columns)
        widgets = self._get_search_widget(form=form, widgets=widgets)
        return render_template(self.chart_template, route_base=self.route_base,
                               title=self.chart_title,
                               label_columns=self.label_columns,
                               group_by_columns=self.group_by_columns,
                               height=self.height,
                               widgets=widgets,
                               baseapp=self.baseapp)


class MultipleChartView(BaseChartView):
    chart_template = 'appbuilder/general/charts/chart.html'
    chart_type = 'ColumnChart'

    chart_widget = MultipleChartWidget


    @expose('/chart/')
    @has_access
    def chart(self):
        form = self.search_form.refresh()
        get_filter_args(self._filters)

        value_columns = self.datamodel.query_group(self.group_bys[0], filters=self._filters)

        widgets = self._get_chart_widget(value_columns=value_columns)
        widgets = self._get_search_widget(form=form, widgets=widgets)
        return render_template(self.chart_template, route_base=self.route_base,
                               title=self.chart_title,
                               label_columns=self.label_columns,
                               group_by_columns=self.group_by_columns,
                               height=self.height,
                               widgets=widgets,
                               baseapp=self.baseapp)
