import datetime
import logging

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import sqlalchemy.types as types
from sqlalchemy.ext.declarative import declared_attr

from flask import g


log = logging.getLogger(__name__)


class FileColumn(types.TypeDecorator):
    """
        Extends SQLAlchemy to support and mostly identify a File Column
    """
    impl = types.Text


class ImageColumn(types.TypeDecorator):
    """
        Extends SQLAlchemy to support and mostly identify a Image Column
    """
    impl = types.Text


class AuditMixin(object):
    """
        AuditMixin
        Mixin for models, adds 4 columns to stamp, time and user on creation and modification
        will create the following columns:
        
        :created on:
        :changed on:
        :created by:
        :changed by:
    """
    created_on = Column(DateTime, default=datetime.datetime.now, nullable=False)
    changed_on = Column(DateTime, default=datetime.datetime.now,
                        onupdate=datetime.datetime.now, nullable=False)

    @declared_attr
    def created_by_fk(cls):
        return Column(Integer, ForeignKey('ab_user.id'),
                      default=cls.get_user_id, nullable=False)

    @declared_attr
    def created_by(cls):
        return relationship("User", primaryjoin='%s.created_by_fk == User.id' % cls.__name__)

    @declared_attr
    def changed_by_fk(cls):
        return Column(Integer, ForeignKey('ab_user.id'),
                      default=cls.get_user_id, onupdate=cls.get_user_id, nullable=False)

    @declared_attr
    def changed_by(cls):
        return relationship("User", primaryjoin='%s.changed_by_fk == User.id' % cls.__name__)


    @classmethod
    def get_user_id(cls):
        try:
            log.debug("GET USER ID: {0}".format(g.user.id))
            return g.user.id
        except Exception as e:
            #log.warning("AuditMixin Get User ID {0}".format(str(e)))
            return None


"""
    This is for retro compatibility
"""
class BaseMixin(object):
    pass

