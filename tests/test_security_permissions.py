from flask import g
from flask_appbuilder import SQLA
from flask_login import AnonymousUserMixin, login_user
from tests.base import FABTestCase


class SecurityPermissionsTestCase(FABTestCase):
    def setUp(self):
        from flask import Flask
        from flask_appbuilder import AppBuilder

        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_security")
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

        self._builtin_role = self.appbuilder.sm.find_role("FAB_ROLE1")
        self._group_db_role = self.appbuilder.sm.add_group(
            "group_db_role",
            "group_db_role",
            description="",
            roles=[self._db_role_1],
        )
        self._group_builtin_role = self.appbuilder.sm.add_group(
            "group_builtin_role",
            "group_builtin_role",
            description="",
            roles=[self._builtin_role],
        )
        self._group_mix_roles = self.appbuilder.sm.add_group(
            "group_mix_roles",
            "_group_mix_roles",
            description="",
            roles=[self._db_role_1, self._builtin_role],
        )

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

        self._user_group_mix_roles = self.create_user(
            self.appbuilder,
            "user_group_mix_roles",
            "password1",
            "",
            first_name="user_group_mix_roles",
            last_name="user",
            email="user_group_mix_roles@fab.org",
            role_names=[],
            group_names=["group_mix_roles"],
        )

        self._user_group_db_role = self.create_user(
            self.appbuilder,
            "user_group_db_role",
            "password1",
            "",
            first_name="user_group_db_role",
            last_name="user",
            email="user_group_db_role@fab.org",
            role_names=[],
            group_names=["group_db_role"],
        )

        self._user_group_builtin_role = self.create_user(
            self.appbuilder,
            "user_group_builtin_role",
            "password1",
            "",
            first_name="user_group_builtin_role",
            last_name="user",
            email="user_group_builtin_role@fab.org",
            role_names=[],
            group_names=["group_builtin_role"],
        )

        self._user_multiple_groups = self.create_user(
            self.appbuilder,
            "user_group_multiple_groups",
            "password1",
            "",
            first_name="user_group_multiple_groups",
            last_name="user",
            email="user_group_multiple_groups@fab.org",
            role_names=[],
            group_names=["group_builtin_role", "group_db_role"],
        )

    def tearDown(self):
        self._group_db_role = self.appbuilder.sm.find_group("group_db_role")
        self._group_mix_roles = self.appbuilder.sm.find_group("group_mix_roles")
        self._group_builtin_role = self.appbuilder.sm.find_group("group_builtin_role")
        self._user_group_db_role = self.appbuilder.sm.find_user(
            username="user_group_db_role"
        )
        self._user_group_builtin_role = self.appbuilder.sm.find_user(
            username="user_group_builtin_role"
        )
        self._user_multiple_groups = self.appbuilder.sm.find_user(
            username="user_group_multiple_groups"
        )
        self._db_role_1 = self.appbuilder.sm.find_role("DB_ROLE1")
        self.appbuilder.session.delete(self._user01)
        self.appbuilder.session.delete(self._user02)
        self.appbuilder.session.delete(self._user03)
        self.appbuilder.session.delete(self._user04)
        self.appbuilder.session.delete(self._user_group_db_role)
        self.appbuilder.session.delete(self._user_group_builtin_role)
        self.appbuilder.session.delete(self._user_group_mix_roles)
        self.appbuilder.session.delete(self._user_multiple_groups)
        self.appbuilder.session.delete(self._pvm1)
        self.appbuilder.session.delete(self._pvm2)
        self.appbuilder.session.delete(self._group_db_role)
        self.appbuilder.session.delete(self._group_builtin_role)
        self.appbuilder.session.delete(self._group_mix_roles)
        self.appbuilder.session.delete(self._db_role_1)
        self.appbuilder.get_session.commit()

    def login_user(self, user):
        user = self.appbuilder.sm.find_user(username=user.username)
        g.user = user
        login_user(user)

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

    def test_get_user_permissions_with_group_mix_roles(self):
        """
        Security Permissions: Get user permissions group with mixed roles
        """
        assert {
            ("can_list", "Model1View"),
            ("can_list", "Model2View"),
            ("can_show", "ModelDBView"),
            ("can_delete", "ModelDBView"),
        } == self.appbuilder.sm.get_user_permissions(self._user_group_mix_roles)

    def test_get_user_permissions_with_group_db_role(self):
        """
        Security Permissions: Get user permissions group with db role
        """
        assert {
            ("can_show", "ModelDBView"),
            ("can_delete", "ModelDBView"),
        } == self.appbuilder.sm.get_user_permissions(self._user_group_db_role)

    def test_get_user_permissions_with_group_builtin_role(self):
        """
        Security Permissions: Get user permissions group with builtin role
        """
        assert {
            ("can_list", "Model1View"),
            ("can_list", "Model2View"),
        } == self.appbuilder.sm.get_user_permissions(self._user_group_builtin_role)

    def test_has_access_user_builtin_role(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user_group_builtin_role)
            assert self.appbuilder.sm.has_access("can_list", "Model1View")
            assert self.appbuilder.sm.has_access("can_list", "Model2View")
            assert not self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert not self.appbuilder.sm.has_access("can_delete", "ModelDBView")

    def test_has_access_user_db_role(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user_group_db_role)
            assert not self.appbuilder.sm.has_access("can_list", "Model1View")
            assert not self.appbuilder.sm.has_access("can_list", "Model2View")
            assert self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert self.appbuilder.sm.has_access("can_delete", "ModelDBView")

    def test_has_access_user_mix_role(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user_group_mix_roles)
            assert self.appbuilder.sm.has_access("can_list", "Model1View")
            assert self.appbuilder.sm.has_access("can_list", "Model2View")
            assert self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert self.appbuilder.sm.has_access("can_delete", "ModelDBView")

    def test_has_access_user_multiple_groups(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user_multiple_groups)
            assert self.appbuilder.sm.has_access("can_list", "Model1View")
            assert self.appbuilder.sm.has_access("can_list", "Model2View")
            assert self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert self.appbuilder.sm.has_access("can_delete", "ModelDBView")

    def test_has_access_user_multiple_roles(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user01)
            assert self.appbuilder.sm.has_access("can_list", "Model1View")
            assert self.appbuilder.sm.has_access("can_list", "Model2View")
            assert self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert self.appbuilder.sm.has_access("can_delete", "ModelDBView")

    def test_has_access_user_db_roles(self):
        with self.app.test_request_context("/"):
            self.login_user(self._user02)
            assert not self.appbuilder.sm.has_access("can_list", "Model1View")
            assert not self.appbuilder.sm.has_access("can_list", "Model2View")
            assert self.appbuilder.sm.has_access("can_show", "ModelDBView")
            assert self.appbuilder.sm.has_access("can_delete", "ModelDBView")

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

    def test_get_user_roles_permissions_one_db_role(self):
        assert {
            "DB_ROLE1": [("can_show", "ModelDBView"), ("can_delete", "ModelDBView")]
        } == self.appbuilder.sm.get_user_roles_permissions(self._user02)

    def test_get_user_roles_permissions_mixed_roles(self):
        assert {
            "FAB_ROLE1": [("can_list", "Model1View"), ("can_list", "Model2View")],
            "DB_ROLE1": [("can_show", "ModelDBView"), ("can_delete", "ModelDBView")],
        } == self.appbuilder.sm.get_user_roles_permissions(self._user01)

    def test_get_user_roles_permissions_one_builtin_roles(self):
        assert {
            "FAB_ROLE2": [("can_list", "Model3View"), ("can_list", "Model4View")]
        } == self.appbuilder.sm.get_user_roles_permissions(self._user03)

    def test_get_user_roles_permissions_mul_builtin_roles(self):
        assert {
            "FAB_ROLE1": [("can_list", "Model1View"), ("can_list", "Model2View")],
            "FAB_ROLE2": [("can_list", "Model3View"), ("can_list", "Model4View")],
        } == self.appbuilder.sm.get_user_roles_permissions(self._user04)
