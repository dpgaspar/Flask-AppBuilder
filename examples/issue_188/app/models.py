from flask.ext.appbuilder import Model
from flask.ext.appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey 
from sqlalchemy.orm import relationship
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
        
class Job(Model, AuditMixin):
    id = Column(Integer, primary_key=True)
    jid = Column(Integer,  nullable=True)
    name =  Column(String(564), nullable=False)
    module_type = Column(String(150))
    start_time  = Column(String(150))
    SSL = Column(Boolean)
    SSLVersion = Column(String(20), default='Empty')
    SRVHOST = Column(String(564), default='Empty')
    SRVPORT = Column(BigInteger)
    PAYLOAD = Column(String(564), default='Empty')
    LHOST = Column(String(564), default='Empty')
    LPORT = Column(BigInteger)

    def __repr__(self):
        return self.name

