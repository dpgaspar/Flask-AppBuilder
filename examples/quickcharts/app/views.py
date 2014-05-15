from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from flask_appbuilder.charts.views import DirectChartView

from app import appbuilder
from models import CountryStats


class CountryStatsGeneralView(GeneralView):
    datamodel = SQLAModel(CountryStats)
    list_columns = ['stat_date', 'population', 'unemployed', 'college']


class CountryStatsDirectChart(DirectChartView):
    chart_title = 'Statistics'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population', 'unemployed', 'college')}
    datamodel = SQLAModel(CountryStats)
    base_order = ('stat_date', 'asc')


appbuilder.add_view(CountryStatsGeneralView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_separator("Statistics")
appbuilder.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")

