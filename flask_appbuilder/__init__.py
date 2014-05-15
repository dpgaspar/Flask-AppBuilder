__version__ = '0.8.6'
__author__ = 'Daniel Vaz Gaspar'
__email__ = 'danielvazgaspar@gmail.com'

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .base import AppBuilder
from .baseviews import expose
from .views import GeneralView, IndexView, FormWidget


