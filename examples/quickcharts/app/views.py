from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import ModelView
from flask_appbuilder.charts.views import DirectChartView

from models import CountryStats
from app import appbuilder, db


class CountryStatsModelView(ModelView):
    datamodel = SQLAModel(CountryStats)
    list_columns = ['stat_date', 'population', 'unemployed', 'college']


class CountryStatsDirectChart(DirectChartView):
    chart_title = 'Statistics'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population', 'unemployed', 'college')}
    datamodel = SQLAModel(CountryStats)
    base_order = ('stat_date', 'asc')


db.create_all()
appbuilder.add_view(CountryStatsModelView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_separator("Statistics")
appbuilder.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")

