    from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import ModelView
from flask_appbuilder.charts.views import DirectChartView, GroupByChartView
from models import CountryStats, Country, PoliticalType
from app import appbuilder, db
from flask_appbuilder.models.group import aggregate_count, aggregate_sum
import random


def fill_data():
    countries = ['Portugal', 'Germany', 'Spain', 'France', 'USA', 'China','Russia','Japan']
    politicals = ['Democratic', 'Authorative']
    try:
        for country in countries:
            c = Country(name=country)
            db.session.add(c)
            db.session.commit()
        for political in politicals:
            c = PoliticalType(name=political)
            db.session.add(c)
            db.session.commit()
        for x in range(1,100):
            cs = CountryStats()
            cs.population = random.randint(1, 1000000)
            cs.unemployed = random.randint(1, 100)
            cs.college = random.randint(1, 100)
            year = random.choice(range(1900, 2012))
            month = random.choice(range(1, 12))
            day = random.choice(range(1, 28))
            cs.statdate = datetime(year, month, day)
            cs.country_id = random.randint(1, len(countries))
            cs.political_type_id = random.randint(1, len(politicals))
            db.session.add(cs)
            db.session.commit()
    except Exception as e:
        log.error("Update ViewMenu error: {0}".format(str(e)))
        self.get_session.rollback()


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
fill_data()
appbuilder.add_view(CountryModelView, "List Countries", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(PoliticalTypeModelView, "List Political Types", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_view(CountryStatsModelView, "List Country Stats", icon="fa-folder-open-o", category="Statistics")
appbuilder.add_separator("Statistics")
appbuilder.add_view(CountryStatsDirectChart, "Show Country Chart", icon="fa-dashboard", category="Statistics")
appbuilder.add_view(CountryGroupByChartView, "Group Country Chart", icon="fa-dashboard", category="Statistics")

