from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import ModelView
from flask_appbuilder.charts.views import DirectChartView, GroupByChartView
from models import CountryStats, Country, PoliticalType
from app import appbuilder, db
from flask_appbuilder.models.group import aggregate_count, aggregate_sum

class CountryStatsModelView(ModelView):
    datamodel = SQLAModel(CountryStats)
    list_columns = ['country', 'stat_date', 'population', 'unemployed', 'college']

class CountryModelView(ModelView):
    datamodel = SQLAModel(Country)


class PoliticalTypeModelView(ModelView):
    datamodel = SQLAModel(PoliticalType)


class CountryStatsDirectChart(DirectChartView):
    datamodel = SQLAModel(CountryStats)
    chart_title = 'Statistics'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population', 'unemployed', 'college')}
    base_order = ('stat_date', 'asc')


class CountryGroupByChartView(GroupByChartView):
    datamodel = SQLAModel(CountryStats)
    chart_title = 'Statistics'
    chart_type = 'ColumnChart'
    group_by_columns = ['country.name', 'political_type.name']
    # [{'column':'<COL NAME>','group_class':<CLASS>]
    aggregate_by_column = [(aggregate_count, ''), (aggregate_sum, 'population')]
    # [{'aggr_func':<FUNC>,'column':'<COL NAME>'}]


db.create_all()
appbuilder.add_view(CountryModelView, "List Countries", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(PoliticalTypeModelView, "List Political Types", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(CountryStatsModelView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_separator("Statistics")
appbuilder.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")
appbuilder.add_view(CountryGroupByChartView, "Group Country Chart", icon="fa-dashboard", category="Statistics")

