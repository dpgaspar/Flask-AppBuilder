from nose.tools import eq_, ok_, raises

import os
import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.appbuilder.baseapp import BaseApp


DEFAULT_INDEX_STRING = 'Welcome'

def setup():

    basedir = os.path.abspath(os.path.dirname(__file__))
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = 'thisismyscretkey'
    db = SQLAlchemy(app)
    return db, app


def create_models(db):
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

    Model1, Model2 = create_models(db)
    genapp = BaseApp(app, db)

    class Model1View(GeneralView):
        datamodel = SQLAModel(Model1, db.session)

    class Model2View(GeneralView):
        datamodel = SQLAModel(Model2, db.session)
        related_views = [Model1View]

    genapp.add_view(Model1View(), "Model1")
    genapp.add_view(Model2View(), "Model2")
    return genapp


def test_base_init():
    """
        Test F.A.B. initialization
    """
    db, app = setup()
    genapp = BaseApp(app, db)
    ok_(len(genapp.baseviews) > 9) # current minimal views are 11


def test_base_models():
    """
        Test F.A.B. Model creation
    """
    from sqlalchemy.engine.reflection import Inspector

    db, app = setup()
    create_models(db)
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

    setup_simple_app1(app, db)
    t = app.test_client()
    resp = t.get('/')
    data = resp.data.decode('utf-8')
    ok_(DEFAULT_INDEX_STRING in resp.data)
    
