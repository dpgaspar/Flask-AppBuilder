from flask.ext.appbuilder.widgets import RenderTemplateWidget

class ChartWidget(RenderTemplateWidget):

    template = 'appbuilder/general/widgets/chart.html'

    route_base = ''
    chart_title = ''
    value_columns = []
    chart_type = ''
    chart_3d = 'false'
    
    
    def __init__(self, route_base = '',
                chart_title = '',
                chart_type = '',
                chart_3d ='false',
                value_columns = []):
                
        self.route_base = route_base
        self.chart_title = chart_title
        self.chart_type = chart_type
        self.chart_3d = chart_3d
        self.value_columns = value_columns
        
    def __call__(self, **kwargs):
        kwargs['route_base'] = self.route_base
        kwargs['chart_title'] = self.chart_title
        kwargs['chart_type'] = self.chart_type
        kwargs['chart_3d'] = self.chart_3d 
        kwargs['value_columns'] = self.value_columns
        
        return super(ChartWidget, self).__call__(**kwargs)

