from flask_appbuilder import SQLA
from flask_appbuilder.tests.base import FABTestCase
from flask_login import AnonymousUserMixin


class SecurityPermissionsTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("flask_appbuilder.tests.config_security")
        self.app.config["FAB_ADD_SECURITY_VIEWS"] = False

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        self._db_role_1 = self.appbuilder.sm.add_role("DB_ROLE1")
        self._pvm1 = self.appbuilder.sm.add_permission_view_menu(
            "can_show", "ModelDBView"
        )
        self._pvm2 = self.appbuilder.sm.add_permission_view_menu(
            "can_delete", "ModelDBView"
        )
        self.appbuilder.sm.add_permission_role(self._db_role_1, self._pvm1)
        self.appbuilder.sm.add_permission_role(self._db_role_1, self._pvm2)

        # Insert test data
        self._user01 = self.create_user(
            self.appbuilder,
            "user1",
            "password1",
            "",
            first_name="user01",
            last_name="user",
            email="user01@fab.org",
            role_names=["FAB_ROLE1", "DB_ROLE1"],
        )

        self._user02 = self.create_user(
            self.appbuilder,
            "user2",
            "password1",
            "",
            first_name="user02",
            last_name="user",
            email="user02@fab.org",
            role_names=["DB_ROLE1"],
        )

        self._user03 = self.create_user(
            self.appbuilder,
            "user3",
            "password1",
            "",
            first_name="user03",
            last_name="user",
            email="user03@fab.org",
            role_names=["FAB_ROLE2"],
        )

        self._user04 = self.create_user(
            self.appbuilder,
            "user4",
            "password1",
            "",
            first_name="user04",
            last_name="user",
            email="user04@fab.org",
            role_names=["FAB_ROLE1", "FAB_ROLE2"],
        )

    def tearDown(self):
        self.appbuilder.get_session.delete(self._user01)
        self.appbuilder.get_session.delete(self._user02)
        self.appbuilder.get_session.delete(self._user03)
        self.appbuilder.get_session.delete(self._user04)
        self.appbuilder.get_session.delete(self._pvm1)
        self.appbuilder.get_session.delete(self._pvm2)
        self.appbuilder.get_session.delete(self._db_role_1)
        self.appbuilder.get_session.commit()

    def test_get_user_permissions_mixed(self):
        """
        Security Permissions: Get user permissions mixes role types
        """
        assert {
            ("can_list", "Model1View"),
            ("can_list", "Model2View"),
            ("can_show", "ModelDBView"),
            ("can_delete", "ModelDBView"),
        } == self.appbuilder.sm.get_user_permissions(self._user01)

    def test_get_user_permissions_db(self):
        """
        Security Permissions: Get user permissions DB role type
        """
        assert {
            ("can_delete", "ModelDBView"),
            ("can_show", "ModelDBView"),
        } == self.appbuilder.sm.get_user_permissions(self._user02)

    def test_get_user_permissions_builtin(self):
        """
        Security Permissions: Get user permissions builtin role type
        """
        assert {
            ("can_list", "Model3View"),
            ("can_list", "Model4View"),
        } == self.appbuilder.sm.get_user_permissions(self._user03)

    def test_get_user_permissions_builtin_multiple(self):
        """
        Security Permissions: Get user permissions multiple builtin role type
        """
        assert {
            ("can_list", "Model2View"),
            ("can_list", "Model1View"),
            ("can_list", "Model3View"),
            ("can_list", "Model4View"),
        } == self.appbuilder.sm.get_user_permissions(self._user04)

    def test_get_anonymous_permissions(self):
        """
        Security Permissions: Get anonymous user permissions
        """
        assert set() == self.appbuilder.sm.get_user_permissions(AnonymousUserMixin())

    def test_get_role_permissions_builtin(self):
        """
        Security Permissions: Get role permissions builtin
        """
        role = self.appbuilder.sm.find_role("FAB_ROLE1")
        assert {
            ("can_list", "Model2View"),
            ("can_list", "Model1View"),
        } == self.appbuilder.sm.get_role_permissions(role)

    def test_get_role_permissions_db(self):
        """
        Security Permissions: Get role permissions db
        """
        role = self.appbuilder.sm.find_role("DB_ROLE1")
        assert {
            ("can_show", "ModelDBView"),
            ("can_delete", "ModelDBView"),
        } == self.appbuilder.sm.get_role_permissions(role)
