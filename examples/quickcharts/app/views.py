import random
import logging
import datetime
import calendar
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder.views import ModelView
from flask_appbuilder.charts.views import DirectChartView, DirectByChartView, GroupByChartView
from models import CountryStats, Country, PoliticalType
from app import appbuilder, db
from flask_appbuilder.models.group import aggregate_count, aggregate_sum, aggregate_avg

log = logging.getLogger(__name__)



class CountryStatsModelView(ModelView):
    datamodel = SQLAInterface(CountryStats)
    list_columns = ['country', 'stat_date', 'population', 'unemployed', 'college']


class CountryModelView(ModelView):
    datamodel = SQLAInterface(Country)


class PoliticalTypeModelView(ModelView):
    datamodel = SQLAInterface(PoliticalType)


class CountryStatsDirectChart(DirectChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = 'Statistics'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population', 'unemployed', 'college')}
    base_order = ('stat_date', 'asc')


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


class CountryDirectChartView(DirectByChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = 'Direct Data'

    definitions = [
        {
            #'label': 'Monthly',
            'group': 'stat_date',
            'series': ['unemployed',
                       'college']
        }
    ]


class CountryGroupByChartView(GroupByChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = 'Statistics'

    definitions = [
        {
            'label': 'Country Stat',
            'group': 'country',
            'series': [(aggregate_avg, 'unemployed'),
                       (aggregate_avg, 'population'),
                       (aggregate_avg, 'college')
            ]
        },
        {
            #'label': 'Monthly',
            'group': 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_sum, 'unemployed'),
                       (aggregate_avg, 'population'),
                       (aggregate_avg, 'college')
            ]
        }
    ]


appbuilder.add_view(CountryModelView, "List Countries", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(PoliticalTypeModelView, "List Political Types", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(CountryStatsModelView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_separator("Statistics")
appbuilder.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")
appbuilder.add_view(CountryGroupByChartView, "Group Country Chart", icon="fa-dashboard", category="Statistics")
appbuilder.add_view(CountryDirectChartView, "Show Country Chart", icon="fa-dashboard", category="Statistics")

