"""
Tests for detached user resilience in FAB security views and manager.

Verifies that:
1. _get_safe_user re-fetches a detached user from DB
2. _get_authenticated_user handles detached/missing g.user gracefully
3. has_access handles detached g.user gracefully
4. update_user_auth_stat calls hooks AFTER update_user
"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask, g
from flask_appbuilder import AppBuilder
from flask_appbuilder.utils.legacy import get_sqla_class


class SafeUserTestCase(unittest.TestCase):
    """Test _get_safe_user and _is_user_detached helpers."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_get_safe_user_returns_none_for_none(self):
        sm = self.appbuilder.sm
        self.assertIsNone(sm._get_safe_user(None))

    def test_get_safe_user_returns_attached_user_as_is(self):
        sm = self.appbuilder.sm
        user = sm.add_user(
            username="test_safe_attached",
            first_name="Safe",
            last_name="Attached",
            email="safe_attached@test.com",
            password="password123",
        )
        try:
            result = sm._get_safe_user(user)
            self.assertEqual(result.id, user.id)
        finally:
            sm.delete_user(user)

    def test_get_safe_user_refetches_detached_user(self):
        sm = self.appbuilder.sm
        user = sm.add_user(
            username="test_safe_detached",
            first_name="Safe",
            last_name="Detached",
            email="safe_detached@test.com",
            password="password123",
        )
        user_id = user.id
        try:
            # Detach the user by expunging from session
            self.db.session.expunge(user)
            self.assertTrue(sm._is_user_detached(user))

            result = sm._get_safe_user(user)
            self.assertIsNotNone(result)
            self.assertEqual(result.id, user_id)
            self.assertFalse(sm._is_user_detached(result))
        finally:
            # Re-fetch for cleanup
            fresh = sm.get_user_by_id(user_id)
            if fresh:
                sm.delete_user(fresh)

    def test_is_user_detached_false_for_non_orm_object(self):
        """Non-ORM objects (e.g. AnonymousUser) should not be flagged."""
        from flask_login import AnonymousUserMixin

        sm = self.appbuilder.sm
        anon = AnonymousUserMixin()
        self.assertFalse(sm._is_user_detached(anon))


class DetachedUserViewTestCase(unittest.TestCase):
    """Test _get_authenticated_user resilience to detached users."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_get_authenticated_user_no_g_user_returns_none(self):
        """When g.user is not set, should return None."""
        auth_view = self.appbuilder.sm.auth_view

        with self.app.test_request_context("/"):
            result = auth_view._get_authenticated_user()
            self.assertIsNone(result)

    def test_get_authenticated_user_detached_refetches(self):
        """When g.user is detached, should re-fetch and return the user."""
        auth_view = self.appbuilder.sm.auth_view
        sm = self.appbuilder.sm

        user = sm.add_user(
            username="test_detach_view",
            first_name="Test",
            last_name="Detach",
            email="test_detach_view@test.com",
            password="password123",
        )
        user_id = user.id

        try:
            with self.app.test_request_context("/"):
                # Detach the user
                self.db.session.expunge(user)
                g.user = user

                result = auth_view._get_authenticated_user()
                self.assertIsNotNone(result)
                self.assertEqual(result.id, user_id)
        finally:
            fresh = sm.get_user_by_id(user_id)
            if fresh:
                sm.delete_user(fresh)

    def test_get_authenticated_user_normal_user_works(self):
        """Normal (non-detached) user should be resolved correctly."""
        auth_view = self.appbuilder.sm.auth_view
        sm = self.appbuilder.sm

        user = sm.add_user(
            username="test_detach_user",
            first_name="Test",
            last_name="Detach",
            email="test_detach@test.com",
            password="password123",
        )

        try:
            with self.app.test_request_context("/"):
                g.user = user
                result = auth_view._get_authenticated_user()
                self.assertIsNotNone(result)
                self.assertEqual(result.username, "test_detach_user")
        finally:
            sm.delete_user(user)


class DetachedUserHasAccessTestCase(unittest.TestCase):
    """Test has_access resilience to detached users."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_has_access_unauthenticated_falls_through_to_public(self):
        """Unauthenticated user should check public permissions."""
        sm = self.appbuilder.sm

        with self.app.test_request_context("/"):
            mock_user = MagicMock()
            mock_user.is_authenticated = False

            with patch("flask_appbuilder.security.manager.current_user", mock_user):
                result = sm.has_access("can_list", "SomeView")
                # Falls through to is_item_public which returns False
                self.assertFalse(result)

    def test_has_access_detached_g_user_returns_false(self):
        """When g.user is detached and can't be re-fetched, return False."""
        sm = self.appbuilder.sm

        with self.app.test_request_context("/"):
            mock_current = MagicMock()
            mock_current.is_authenticated = True

            # _get_safe_user returns None for detached user with no valid id
            mock_user = MagicMock()
            mock_user.id = None

            g.user = mock_user

            with (
                patch("flask_appbuilder.security.manager.current_user", mock_current),
                patch.object(sm, "_get_safe_user", return_value=None),
            ):
                result = sm.has_access("can_list", "SomeView")
                self.assertFalse(result)


class UpdateUserAuthStatHookOrderTestCase(unittest.TestCase):
    """Test that update_user_auth_stat calls hooks AFTER update_user."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.db.session.remove()
        self.ctx.pop()

    def test_on_user_login_called_after_update_user_on_success(self):
        """on_user_login should be called AFTER update_user on success."""
        sm = self.appbuilder.sm
        call_order = []

        original_update_user = sm.update_user
        original_on_user_login = sm.on_user_login

        def mock_update_user(user):
            call_order.append("update_user")
            return original_update_user(user)

        def mock_on_user_login(user):
            call_order.append("on_user_login")
            return original_on_user_login(user)

        user = sm.add_user(
            username="test_hook_order",
            first_name="Hook",
            last_name="Order",
            email="hookorder@test.com",
            password="password123",
        )

        try:
            sm.update_user = mock_update_user
            sm.on_user_login = mock_on_user_login

            sm.update_user_auth_stat(user, success=True)

            self.assertEqual(call_order, ["update_user", "on_user_login"])
        finally:
            sm.update_user = original_update_user
            sm.on_user_login = original_on_user_login
            sm.delete_user(user)

    def test_on_user_login_failed_called_after_update_user_on_failure(self):
        """on_user_login_failed should be called AFTER update_user on failure."""
        sm = self.appbuilder.sm
        call_order = []

        original_update_user = sm.update_user
        original_on_user_login_failed = sm.on_user_login_failed

        def mock_update_user(user):
            call_order.append("update_user")
            return original_update_user(user)

        def mock_on_user_login_failed(user):
            call_order.append("on_user_login_failed")
            return original_on_user_login_failed(user)

        user = sm.add_user(
            username="test_hook_order_fail",
            first_name="Hook",
            last_name="OrderFail",
            email="hookorderfail@test.com",
            password="password123",
        )

        try:
            sm.update_user = mock_update_user
            sm.on_user_login_failed = mock_on_user_login_failed

            sm.update_user_auth_stat(user, success=False)

            self.assertEqual(call_order, ["update_user", "on_user_login_failed"])
        finally:
            sm.update_user = original_update_user
            sm.on_user_login_failed = original_on_user_login_failed
            sm.delete_user(user)


if __name__ == "__main__":
    unittest.main()
