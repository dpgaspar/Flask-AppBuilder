from flask import session, request
from flask_appbuilder.api import BaseApi, expose

from . import appbuilder


class CasApi(BaseApi):
    @expose('/cas/callback', methods=['POST'])
    def callback(self):
        """
        Read PGT and PGTIOU sent by CAS(Single-Logout callback)
        """
        if 'logoutRequest' in request.args:
            pass


appbuilder.add_api(CasApi)
