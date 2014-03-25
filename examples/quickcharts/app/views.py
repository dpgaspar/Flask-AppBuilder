from flask.ext.appbuilder.baseapp import BaseApp
from flask.ext.appbuilder.models.datamodel import SQLAModel
from flask.ext.appbuilder.views import GeneralView
from flask_appbuilder.charts.views import DirectChartView
from flask.ext.babelpkg import lazy_gettext as _

from app import app, db
from models import CountryStats



class CountryStatsGeneralView(GeneralView):
    datamodel = SQLAModel(CountryStats, db.session)
    list_columns = ['stat_date','population','unenployed','college']

class CountryStatsDirectChart(DirectChartView):
    chart_title = 'Grouped contacts'
    chart_type = 'LineChart'
    direct_columns = {'General Stats': ('stat_date', 'population','unenployed','college')}
    datamodel = SQLAModel(CountryStats, db.session)
    base_order = ('stat_date', 'desc')

fixed_translations_import = [
    _("List Country Stats"),
    _("Show Country Chart")]


genapp = BaseApp(app, db)
genapp.add_view(CountryStatsGeneralView(), "List Country Stats", icon="fa-folder-open-o", category="Statistics")
genapp.add_separator("Statistics")
genapp.add_view(CountryStatsDirectChart(), "Show Country Chart", icon="fa-dashboard", category="Statistics")

