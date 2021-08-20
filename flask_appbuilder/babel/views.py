from flask import abort, redirect, session, request
from flask_babel import refresh

from ..baseviews import BaseView, expose
from ..urltools import Stack


class LocaleView(BaseView):
    route_base = "/lang"

    default_view = "index"

    @expose("/<string:locale>")
    def index(self, locale):
        if locale not in self.appbuilder.bm.languages:
            abort(404, description="Locale not supported.")

        if request.referrer is not None:
            page_history = Stack(session.get("page_history", []))
            page_history.push(request.referrer)
            session["page_history"] = page_history.to_json()

        session["locale"] = locale
        refresh()
        self.update_redirect()
        return redirect(self.get_redirect())
