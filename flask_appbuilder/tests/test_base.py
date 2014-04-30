from nose.tools import eq_, ok_, raises

import logging

from . import setup

DEFAULT_INDEX_STRING = 'Welcome'

log = logging.getLogger(__name__)


def define_models():
    from sqlalchemy import Column, Integer, String, ForeignKey, Date
    from sqlalchemy.orm import relationship
    from flask.ext.appbuilder.models.mixins import BaseMixin
    from flask.ext.appbuilder import Base

    class Model1(BaseMixin, Base):
        id = Column(Integer, primary_key=True)
        field_string = Column(String(50), unique=True, nullable=False)
        field_integer = Column(Integer())
        field_date = Column(Date())

        def __repr__(self):
            return self.field_string

    class Model2(BaseMixin, Base):
        id = Column(Integer, primary_key=True)
        field_string = Column(String(50), unique=True, nullable=False)
        group_id = Column(Integer, ForeignKey('model1.id'), nullable=False)
        group = relationship("Model1")

        def __repr__(self):
            return self.field_string

    return Model1, Model2


def setup_simple_app1(app, db):
    from flask.ext.appbuilder.models.datamodel import SQLAModel
    from flask.ext.appbuilder.views import GeneralView
    from flask.ext.appbuilder.baseapp import BaseApp

    Model1, Model2 = define_models()
    genapp = BaseApp(app, db)

    class Model1View(GeneralView):
        datamodel = SQLAModel(Model1, db.session)

    class Model2View(GeneralView):
        datamodel = SQLAModel(Model2, db.session)
        related_views = [Model1View]

    genapp.add_view(Model1View(), "Model1")
    genapp.add_view(Model2View(), "Model2")
    return genapp, Model1, Model2


def test_base_init():
    from flask.ext.appbuilder.baseapp import BaseApp

    """
        Test F.A.B. initialization
    """
    db, app = setup()
    baseapp = BaseApp(app, db)
    ok_(len(baseapp.baseviews) > 9) # current minimal views are 11


def test_model_creation():
    from flask.ext.appbuilder.baseapp import BaseApp

    """
        Test F.A.B. Model creation
    """
    from sqlalchemy.engine.reflection import Inspector

    db, app = setup()
    define_models()
    genapp = BaseApp(app, db)
    engine = db.session.get_bind(mapper=None, clause=None)
    inspector = Inspector.from_engine(engine)
    # Check if tables exist
    ok_('model1' in inspector.get_table_names())
    ok_('model2' in inspector.get_table_names())


def test_base_views():
    """
        Test F.A.B. Basic views creation
    """

    db, app = setup()

    baseapp, Model1, Model2 = setup_simple_app1(app, db)
    client = app.test_client()
    
    # Check for Welcome Message    
    rv = client.get('/')
    data = rv.data.decode('utf-8')
    ok_(DEFAULT_INDEX_STRING in data)
    
    # Try List and Redirect to Login
    rv = client.get('/model1view/list/')
    eq_(rv.status_code, 302)
    rv = client.get('/model2view/list/')
    eq_(rv.status_code, 302)

    # Login with default admin
    client.post('/login/', data=dict(
        username='admin',
        password='general'
    ), follow_redirects=True)
    # Test access to authorized views
    rv = client.get('/model1view/list/')
    eq_(rv.status_code, 200)
    rv = client.get('/model2view/list/')
    eq_(rv.status_code, 200)

    rv = client.get('/model1view/add')
    eq_(rv.status_code, 200)

    # Add one record and test if it's on the db
    rv = client.post('/model1view/add?next=%2Fmodel1view%2Flist%2F',
                     data=dict(field_string='test1', field_integer='1'))
    eq_(rv.status_code, 200)

    model = db.session.query(Model1).first()
    eq_(model.field_string, u'test1')
    eq_(model.field_integer, 1)


