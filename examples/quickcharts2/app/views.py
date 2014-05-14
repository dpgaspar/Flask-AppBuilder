from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from flask_appbuilder.charts.views import DirectChartView

from app import app, db
from models import CountryStats, Country


class CountryStatsGeneralView(GeneralView):
    datamodel = SQLAModel(CountryStats)
    list_columns = ['country', 'stat_date', 'population', 'unemployed', 'college']

class CountryGeneralView(GeneralView):
    datamodel = SQLAModel(Country)


class CountryStatsDirectChart(DirectChartView):
    datamodel = SQLAModel(CountryStats)
    chart_title = 'Statistics'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population', 'unemployed', 'college')}
    base_order = ('stat_date', 'asc')


genapp = BaseApp(app, db)
genapp.add_view(CountryGeneralView, "List Countries", icon="fa-folder-open-o", category="Statistics")
genapp.add_view(CountryStatsGeneralView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
genapp.add_separator("Statistics")
genapp.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")

