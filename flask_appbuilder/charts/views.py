from flask import render_template
from sqlalchemy.ext.serializer import loads, dumps

from sqlalchemy.ext.serializer import loads, dumps

from widgets import ChartWidget
from ..security.decorators import has_access
from ..views import BaseView, expose


class ChartView(BaseView):
    
    chart_template = 'appbuilder/general/charts/chart.html'
    chart_widget = ChartWidget
    chart_title = 'Chart'
    chart_type = 'PieChart'
    chart_3d = 'true'
    width = 400
    height = '400px'
    group_by = ''
    label_columns = []
    group_by_columns = []
    datamodel = None
    
    def _get_chart_widget(self, value_columns = [], widgets = {}):        
        widgets['chart'] = self.chart_widget(route_base = self.route_base,
                                             chart_title = self.chart_title, 
                                             chart_type = self.chart_type,
                                             chart_3d = self.chart_3d, 
                                                value_columns = value_columns)
        return widgets
    
    @expose('/chart/')
    @has_access
    def show(self):
        group_by = self._get_group_by_args()
        if group_by == '':
            group_by = self.group_by_columns[0]
        value_columns = self.datamodel.query_simple_group(group_by)
        widgets = self._get_chart_widget(value_columns = value_columns)
        return render_template(self.chart_template, route_base = self.route_base, 
                                                title = self.chart_title,
                                                label_columns = self.label_columns, 
                                                group_by_columns = self.group_by_columns,
                                                height = self.height,
                                                widgets = widgets, 
                                                baseapp = self.baseapp)
    
    
