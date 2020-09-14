from flask import abort, redirect, session
from flask_babel import refresh

from ..baseviews import BaseView, expose


class LocaleView(BaseView):
    route_base = "/lang"

    default_view = "index"

    @expose("/<string:locale>")
    def index(self, locale):
        if locale not in self.appbuilder.bm.languages:
            abort(404, description="Locale not supported.")
        session["locale"] = locale
        refresh()
        self.update_redirect()
        return redirect(self.get_redirect())
