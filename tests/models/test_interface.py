from contextlib import contextmanager

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.models.sqla.filters import (
    FilterEqual,
    FilterRelationManyToManyEqual,
)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import (
    PermissionView,
    Role,
    User,
)
from flask_appbuilder.utils.legacy import get_sqla_class
from sqlalchemy import event
from sqlalchemy.engine import Engine
from tests.base import FABTestCase
from tests.const import USERNAME_ADMIN, USERNAME_READONLY


@contextmanager
def assert_no_queries(engine: Engine):
    queries = []

    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        queries.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        if queries:
            raise AssertionError(f"Unexpected queries executed:\n{queries}")


class SQLAInterfaceTestCase(FABTestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)

    def tearDown(self):
        pass

    def test_query_with_filter(self):
        interface = SQLAInterface(User)
        filters = interface.get_filters()
        filters.add_filter(
            "username",
            FilterEqual,
            USERNAME_ADMIN,
        )
        count, admin_user = interface.query(
            filters=filters,
            page=0,
            page_size=10,
            order_column="id",
            order_direction="asc",
        )
        self.assertEqual(count, 1)
        self.assertEqual(admin_user[0].username, USERNAME_ADMIN)

    def test_query_join_m_m(self):
        interface = SQLAInterface(User)
        filters = interface.get_filters(["id", "username"], {})
        count, users = interface.query(
            filters=filters,
            page=0,
            page_size=10,
            order_column="username",
            order_direction="asc",
            select_columns=["username", "roles.name"],
        )
        if count != 2:
            raise AssertionError(
                f"2 users, got {count}. Users: {[user.username for user in users]}"
            )
        self.assertEqual(count, 2)
        with assert_no_queries(self.appbuilder.session.get_bind()):
            self.assertEqual(users[0].roles[0].name, "ReadOnly")

    def test_query_join_o_m_order_by(self):
        interface = SQLAInterface(PermissionView)
        filters = interface.get_filters([], {})
        filters.add_filter(
            "permission.name",
            FilterEqual,
            "can_add",
        ).add_filter(
            "view_menu.name",
            FilterEqual,
            "UserDBModelView",
        )

        count, permissions = interface.query(
            filters=filters,
            page=0,
            page_size=10,
            order_column="permission.name",
            order_direction="asc",
            select_columns=["permission.name", "view_menu.name"],
        )
        self.assertEqual(count, 1)
        with assert_no_queries(self.appbuilder.session.get_bind()):
            self.assertEqual(permissions[0].permission.name, "can_add")

    def test_query_join_m_m_order_by_m_o(self):
        interface = SQLAInterface(User)
        filters = interface.get_filters()
        count, users = interface.query(
            filters=filters,
            page=0,
            page_size=10,
            order_column="changed_by.username",
            order_direction="asc",
            select_columns=[
                "username",
                "roles.name",
                "created_by.username",
                "changed_by.username",
            ],
        )
        self.assertEqual(count, 2)
        with assert_no_queries(self.appbuilder.session.get_bind()):
            # access attr makes sure no extra lazy queries are triggered
            users[0].roles[0].name
        usernames = sorted([user.username for user in users])
        expected_username = sorted(
            [
                USERNAME_ADMIN,
                USERNAME_READONLY,
            ]
        )
        self.assertEqual(usernames, expected_username)

    def test_query_join_m_m_filter_m_m(self):
        interface = SQLAInterface(User)
        filters = interface.get_filters()
        readonly_role = (
            self.appbuilder.session.query(Role)
            .filter(Role.name == "ReadOnly")
            .one_or_none()
        )
        filters.add_filter(
            "roles",
            FilterRelationManyToManyEqual,
            readonly_role.id,
        )
        count, users = interface.query(
            filters=filters,
            page=0,
            page_size=10,
            select_columns=[
                "username",
                "roles.name",
                "created_by.username",
                "changed_by.username",
            ],
        )
        self.assertEqual(count, 1)
        with assert_no_queries(self.appbuilder.session.get_bind()):
            # access attr makes sure no extra lazy queries are triggered
            assert users[0].roles[0].name == "ReadOnly"

    def test_query_join_m_m_order_by_m_m(self):
        interface = SQLAInterface(User)
        filters = interface.get_filters()
        count, users = interface.query(
            filters=filters,
            order_column="roles.name",
            order_direction="asc",
            page=0,
            page_size=10,
            select_columns=[
                "username",
                "roles.name",
                "created_by.username",
                "changed_by.username",
            ],
        )
        self.assertEqual(count, 2)
