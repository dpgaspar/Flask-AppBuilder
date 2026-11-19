import unittest

from flask import render_template
from jinja2 import ChoiceLoader, DictLoader
from tests.base import BaseMVCTestCase
from tests.const import PASSWORD_READONLY, USERNAME_READONLY

# A filter call whose arguments are all literals: Jinja constant-folds it at
# compile time unless the filter is marked as context dependent.
PERMISSION_TEMPLATE = (
    '{% if "can_list"|is_item_visible("MyView") %}VISIBLE{% else %}HIDDEN{% endif %}'
)
# The same check, with the view name passed as a variable (the way FAB's own
# templates call the filter).
PERMISSION_TEMPLATE_VARIABLE = (
    '{% set view = "MyView" %}'
    '{% if "can_list"|is_item_visible(view) %}VISIBLE{% else %}HIDDEN{% endif %}'
)
# A request dependent filter called with a literal argument.
REQUEST_TEMPLATE = "{{ ''|get_link_next }}"

PUBLIC_USERNAME = "public_user"
PUBLIC_PASSWORD = "public"


class TemplateFilterFoldingTestCase(BaseMVCTestCase):
    """
    Jinja constant-folds calls to unmarked filters when every argument is a
    literal, baking the first render's result into the compiled template for
    the lifetime of the process. Filters whose result depends on the request
    or on the current user must therefore be registered with
    ``jinja2.pass_context``.

    See https://github.com/dpgaspar/Flask-AppBuilder/issues/2487
    """

    def setUp(self):
        super().setUp()
        self.db.create_all()

        self.app.jinja_env.loader = ChoiceLoader(
            [
                DictLoader(
                    {
                        "fold_permission.html": PERMISSION_TEMPLATE,
                        "fold_permission_reverse.html": PERMISSION_TEMPLATE,
                        "fold_permission_variable.html": PERMISSION_TEMPLATE_VARIABLE,
                        "fold_request.html": REQUEST_TEMPLATE,
                    }
                ),
                self.app.jinja_env.loader,
            ]
        )

        from flask_appbuilder.models.sqla.interface import SQLAInterface
        from flask_appbuilder.views import ModelView
        from tests.sqla.models import Model1

        class MyView(ModelView):
            datamodel = SQLAInterface(Model1)

        self.appbuilder.add_view(MyView, "MyView")
        self._delete_public_user()
        self.appbuilder.sm.add_user(
            PUBLIC_USERNAME,
            "public",
            "user",
            "public@fab.org",
            role=[self.appbuilder.sm.find_role("Public")],
            password=PUBLIC_PASSWORD,
        )

        @self.app.route("/fold/<template_name>")
        def fold(template_name):
            return render_template(template_name)

    def tearDown(self):
        # The database is shared with the other test modules, so the extra
        # user must not outlive this test case.
        self._delete_public_user()
        super().tearDown()

    def _delete_public_user(self):
        user = self.appbuilder.sm.find_user(username=PUBLIC_USERNAME)
        if user is not None:
            self.appbuilder.session.delete(user)
            self.appbuilder.session.commit()

    def _render(self, username, password, template_name, query_string=None):
        client = self.app.test_client()
        client.get("/logout/")
        client.post(
            "/login/",
            data=dict(username=username, password=password),
            follow_redirects=True,
        )
        response = client.get("/fold/" + template_name, query_string=query_string or {})
        return response.data.decode()

    def test_permission_filter_not_constant_folded(self):
        # The user without permissions compiles the template first: the
        # permission check must still answer for the second user.
        first = self._render(PUBLIC_USERNAME, PUBLIC_PASSWORD, "fold_permission.html")
        second = self._render(
            USERNAME_READONLY, PASSWORD_READONLY, "fold_permission.html"
        )
        self.assertEqual("HIDDEN", first)
        self.assertEqual("VISIBLE", second)

    def test_permission_filter_not_constant_folded_reverse(self):
        # The other way around: the user with permissions compiles the
        # template first.
        first = self._render(
            USERNAME_READONLY, PASSWORD_READONLY, "fold_permission_reverse.html"
        )
        second = self._render(
            PUBLIC_USERNAME, PUBLIC_PASSWORD, "fold_permission_reverse.html"
        )
        self.assertEqual("VISIBLE", first)
        self.assertEqual("HIDDEN", second)

    def test_permission_filter_with_variable_arguments(self):
        # FAB's own templates pass the view name as a variable, which Jinja
        # never folds: the filter must keep answering per user.
        self.assertEqual(
            "VISIBLE",
            self._render(
                USERNAME_READONLY, PASSWORD_READONLY, "fold_permission_variable.html"
            ),
        )
        self.assertEqual(
            "HIDDEN",
            self._render(
                PUBLIC_USERNAME, PUBLIC_PASSWORD, "fold_permission_variable.html"
            ),
        )

    def test_request_dependent_filter_not_constant_folded(self):
        # A request dependent filter called with a literal argument must not
        # bake the first request's query string either.
        first = self._render(
            USERNAME_READONLY,
            PASSWORD_READONLY,
            "fold_request.html",
            {"next": "/first-page"},
        )
        second = self._render(
            USERNAME_READONLY,
            PASSWORD_READONLY,
            "fold_request.html",
            {"next": "/second-page"},
        )
        self.assertEqual("/first-page", first)
        self.assertEqual("/second-page", second)


if __name__ == "__main__":
    unittest.main()
