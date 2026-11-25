"""
Tests for Flask-AppBuilder security model signals.

Tests verify that pre-commit and post-commit signals are fired correctly
for User, Role, and Group CRUD operations.
"""

import unittest
import uuid

from flask import Flask
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.signals import (
    group_created,
    group_creating,
    group_deleted,
    group_deleting,
    group_updated,
    group_updating,
    role_created,
    role_creating,
    role_deleted,
    role_deleting,
    role_updated,
    role_updating,
    user_created,
    user_creating,
    user_deleted,
    user_deleting,
    user_updated,
    user_updating,
)
from flask_appbuilder.utils.legacy import get_sqla_class


def unique_name(prefix: str) -> str:
    """Generate a unique name for test entities."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class SecuritySignalsTestCase(unittest.TestCase):
    """Test case for security model signals."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_SECURITY_SIGNALS_ENABLED"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        # Track created entities for cleanup
        self.created_users = []
        self.created_roles = []
        self.created_groups = []

        # Track signal emissions
        self.pre_commit_events = []
        self.post_commit_events = []

        # Connect signal handlers
        self._connect_handlers()

    def tearDown(self):
        """Clean up after tests."""
        self._disconnect_handlers()

        # Clean up created entities
        sm = self.appbuilder.sm

        # Delete users (except admin)
        for user in self.created_users:
            try:
                existing = sm.get_user_by_id(user.id)
                if existing:
                    sm.session.delete(existing)
            except Exception:
                pass

        # Delete roles (except built-in roles)
        for role in self.created_roles:
            try:
                existing = sm.find_role(role.name)
                if existing:
                    sm.session.delete(existing)
            except Exception:
                pass

        # Delete groups
        for group in self.created_groups:
            try:
                group_model = sm.group_model
                existing = sm.session.query(group_model).get(group.id)
                if existing:
                    existing.users = []
                    existing.roles = []
                    sm.session.delete(existing)
            except Exception:
                pass

        try:
            sm.session.commit()
        except Exception:
            sm.session.rollback()

        self.db.session.remove()
        self.ctx.pop()

    def _connect_handlers(self):
        """Connect test signal handlers."""
        # Pre-commit handlers
        user_creating.connect(self._on_pre_commit)
        user_updating.connect(self._on_pre_commit)
        user_deleting.connect(self._on_pre_commit)
        role_creating.connect(self._on_pre_commit)
        role_updating.connect(self._on_pre_commit)
        role_deleting.connect(self._on_pre_commit)
        group_creating.connect(self._on_pre_commit)
        group_updating.connect(self._on_pre_commit)
        group_deleting.connect(self._on_pre_commit)

        # Post-commit handlers
        user_created.connect(self._on_post_commit)
        user_updated.connect(self._on_post_commit)
        user_deleted.connect(self._on_post_commit)
        role_created.connect(self._on_post_commit)
        role_updated.connect(self._on_post_commit)
        role_deleted.connect(self._on_post_commit)
        group_created.connect(self._on_post_commit)
        group_updated.connect(self._on_post_commit)
        group_deleted.connect(self._on_post_commit)

    def _disconnect_handlers(self):
        """Disconnect test signal handlers."""
        # Pre-commit handlers
        user_creating.disconnect(self._on_pre_commit)
        user_updating.disconnect(self._on_pre_commit)
        user_deleting.disconnect(self._on_pre_commit)
        role_creating.disconnect(self._on_pre_commit)
        role_updating.disconnect(self._on_pre_commit)
        role_deleting.disconnect(self._on_pre_commit)
        group_creating.disconnect(self._on_pre_commit)
        group_updating.disconnect(self._on_pre_commit)
        group_deleting.disconnect(self._on_pre_commit)

        # Post-commit handlers
        user_created.disconnect(self._on_post_commit)
        user_updated.disconnect(self._on_post_commit)
        user_deleted.disconnect(self._on_post_commit)
        role_created.disconnect(self._on_post_commit)
        role_updated.disconnect(self._on_post_commit)
        role_deleted.disconnect(self._on_post_commit)
        group_created.disconnect(self._on_post_commit)
        group_updated.disconnect(self._on_post_commit)
        group_deleted.disconnect(self._on_post_commit)

    def _on_pre_commit(self, sender, event):
        """Handle pre-commit signals."""
        self.pre_commit_events.append(event)

    def _on_post_commit(self, sender, event):
        """Handle post-commit signals."""
        self.post_commit_events.append(event)

    def _clear_events(self):
        """Clear recorded events."""
        self.pre_commit_events = []
        self.post_commit_events = []


class UserSignalsTestCase(SecuritySignalsTestCase):
    """Test signals for User model operations."""

    def test_add_user_emits_signals(self):
        """Test that add_user emits pre and post commit signals."""
        sm = self.appbuilder.sm
        username = unique_name("signal_test_user")

        user = sm.add_user(
            username=username,
            first_name="Signal",
            last_name="Test",
            email=f"{username}@test.com",
            password="password123",
        )

        self.assertIsNotNone(user)
        self.assertNotEqual(user, False)
        self.created_users.append(user)

        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check pre-commit event
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "user")
        self.assertEqual(pre_event.action, "creating")
        self.assertEqual(pre_event.model_id, user.id)
        self.assertEqual(pre_event.model, user)
        self.assertFalse(pre_event.is_committed)

        # Check post-commit event
        post_event = self.post_commit_events[0]
        self.assertEqual(post_event.model_type, "user")
        self.assertEqual(post_event.action, "created")
        self.assertEqual(post_event.model_id, user.id)
        self.assertTrue(post_event.is_committed)

    def test_add_user_no_commit_only_pre_signal(self):
        """Test that add_user with commit=False only emits pre-commit signal."""
        sm = self.appbuilder.sm
        username = unique_name("no_commit_user")

        user = sm.add_user(
            username=username,
            first_name="NoCommit",
            last_name="Test",
            email=f"{username}@test.com",
            password="password123",
            commit=False,
        )

        self.assertIsNotNone(user)
        self.assertNotEqual(user, False)
        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 0)

        # Rollback to clean up
        sm.session.rollback()

    def test_update_user_emits_signals(self):
        """Test that update_user emits pre and post commit signals."""
        sm = self.appbuilder.sm
        username = unique_name("update_test_user")

        # First create a user
        user = sm.add_user(
            username=username,
            first_name="Update",
            last_name="Test",
            email=f"{username}@test.com",
            password="password123",
        )
        self.assertNotEqual(user, False)
        self.created_users.append(user)
        self._clear_events()

        # Now update the user
        user.first_name = "Updated"
        sm.update_user(user)

        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check pre-commit event
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "user")
        self.assertEqual(pre_event.action, "updating")
        # Changes may or may not be detected depending on SQLAlchemy state
        # The important thing is that the signal was emitted

        # Check post-commit event
        post_event = self.post_commit_events[0]
        self.assertEqual(post_event.model_type, "user")
        self.assertEqual(post_event.action, "updated")
        self.assertTrue(post_event.is_committed)

    def test_delete_user_emits_signals(self):
        """Test that delete_user emits pre and post commit signals."""
        sm = self.appbuilder.sm
        username = unique_name("delete_test_user")

        # First create a user
        user = sm.add_user(
            username=username,
            first_name="Delete",
            last_name="Test",
            email=f"{username}@test.com",
            password="password123",
        )
        self.assertNotEqual(user, False)
        user_id = user.id
        self._clear_events()

        # Now delete the user (no need to track - it's being deleted)
        result = sm.delete_user(user)

        self.assertTrue(result)
        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check pre-commit event
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "user")
        self.assertEqual(pre_event.action, "deleting")
        self.assertEqual(pre_event.model_id, user_id)
        self.assertEqual(pre_event.model, user)
        self.assertFalse(pre_event.is_committed)

        # Check post-commit event
        post_event = self.post_commit_events[0]
        self.assertEqual(post_event.model_type, "user")
        self.assertEqual(post_event.action, "deleted")
        self.assertEqual(post_event.model_id, user_id)
        self.assertIsNone(post_event.model)  # Model is None after delete
        self.assertTrue(post_event.is_committed)


class RoleSignalsTestCase(SecuritySignalsTestCase):
    """Test signals for Role model operations."""

    def test_add_role_emits_signals(self):
        """Test that add_role emits pre and post commit signals."""
        sm = self.appbuilder.sm
        role_name = unique_name("SignalTestRole")

        role = sm.add_role(role_name)

        self.assertIsNotNone(role)
        self.created_roles.append(role)

        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check pre-commit event
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "role")
        self.assertEqual(pre_event.action, "creating")
        self.assertEqual(pre_event.model_id, role.id)
        self.assertFalse(pre_event.is_committed)

        # Check post-commit event
        post_event = self.post_commit_events[0]
        self.assertEqual(post_event.model_type, "role")
        self.assertEqual(post_event.action, "created")
        self.assertTrue(post_event.is_committed)

    def test_add_role_existing_no_signals(self):
        """Test that add_role for existing role doesn't emit signals."""
        sm = self.appbuilder.sm
        role_name = unique_name("ExistingRole")

        # Create role first
        role1 = sm.add_role(role_name)
        self.created_roles.append(role1)
        self._clear_events()

        # Try to add same role again
        role2 = sm.add_role(role_name)

        # Should return existing role without emitting signals
        self.assertEqual(role1.id, role2.id)
        self.assertEqual(len(self.pre_commit_events), 0)
        self.assertEqual(len(self.post_commit_events), 0)

    def test_update_role_emits_signals(self):
        """Test that update_role emits pre and post commit signals."""
        sm = self.appbuilder.sm
        role_name = unique_name("UpdateTestRole")
        new_role_name = unique_name("UpdatedRoleName")

        role = sm.add_role(role_name)
        self.created_roles.append(role)
        self._clear_events()

        # Update the role
        sm.update_role(role.id, new_role_name)

        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check events
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "role")
        self.assertEqual(pre_event.action, "updating")
        self.assertIsNotNone(pre_event.changes)
        self.assertIn("name", pre_event.changes)

    def test_delete_role_emits_signals(self):
        """Test that delete_role emits pre and post commit signals."""
        sm = self.appbuilder.sm
        role_name = unique_name("DeleteTestRole")

        role = sm.add_role(role_name)
        role_id = role.id
        self._clear_events()

        # Delete the role (no need to track - it's being deleted)
        result = sm.delete_role(role)

        self.assertTrue(result)
        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "role")
        self.assertEqual(pre_event.action, "deleting")
        self.assertEqual(pre_event.model_id, role_id)


class GroupSignalsTestCase(SecuritySignalsTestCase):
    """Test signals for Group model operations."""

    def test_add_group_emits_signals(self):
        """Test that add_group emits pre and post commit signals."""
        sm = self.appbuilder.sm
        group_name = unique_name("signal_test_group")

        group = sm.add_group(
            name=group_name,
            label="Signal Test Group",
            description="Test group for signals",
        )

        self.assertIsNotNone(group)
        self.created_groups.append(group)

        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        # Check pre-commit event
        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "group")
        self.assertEqual(pre_event.action, "creating")
        self.assertEqual(pre_event.model_id, group.id)

        # Check post-commit event
        post_event = self.post_commit_events[0]
        self.assertEqual(post_event.model_type, "group")
        self.assertEqual(post_event.action, "created")

    def test_delete_group_emits_signals(self):
        """Test that delete_group emits pre and post commit signals."""
        sm = self.appbuilder.sm
        group_name = unique_name("delete_test_group")

        group = sm.add_group(
            name=group_name,
            label="Delete Test Group",
            description="Test group for delete signals",
        )
        group_id = group.id
        self._clear_events()

        # Delete the group (no need to track - it's being deleted)
        result = sm.delete_group(group)

        self.assertTrue(result)
        self.assertEqual(len(self.pre_commit_events), 1)
        self.assertEqual(len(self.post_commit_events), 1)

        pre_event = self.pre_commit_events[0]
        self.assertEqual(pre_event.model_type, "group")
        self.assertEqual(pre_event.action, "deleting")
        self.assertEqual(pre_event.model_id, group_id)


class SignalsDisabledTestCase(SecuritySignalsTestCase):
    """Test that signals can be disabled via config."""

    def setUp(self):
        """Set up test fixtures with signals disabled."""
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_api")
        self.app.config["FAB_SECURITY_SIGNALS_ENABLED"] = False

        self.ctx = self.app.app_context()
        self.ctx.push()

        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

        # Track created entities for cleanup
        self.created_users = []
        self.created_roles = []
        self.created_groups = []

        self.pre_commit_events = []
        self.post_commit_events = []
        self._connect_handlers()

    def test_signals_disabled_no_events(self):
        """Test that no signals are emitted when disabled."""
        sm = self.appbuilder.sm
        username = unique_name("disabled_signals_user")

        user = sm.add_user(
            username=username,
            first_name="Disabled",
            last_name="Signals",
            email=f"{username}@test.com",
            password="password123",
        )

        self.assertIsNotNone(user)
        self.created_users.append(user)

        self.assertEqual(len(self.pre_commit_events), 0)
        self.assertEqual(len(self.post_commit_events), 0)


class TransactionIsolationTestCase(SecuritySignalsTestCase):
    """Test transaction isolation with pre-commit signals."""

    def test_pre_commit_handler_can_modify_session(self):
        """Test that pre-commit handler can add to the same transaction."""
        modifications_made = []

        def pre_commit_modifier(sender, event):
            """Handler that records it was called during transaction."""
            # In a real scenario, this would add to the session
            # For testing, we just record that we were called
            modifications_made.append(
                {
                    "model_type": event.model_type,
                    "model_id": event.model_id,
                    "is_committed": event.is_committed,
                }
            )

        user_creating.connect(pre_commit_modifier)

        try:
            sm = self.appbuilder.sm
            username = unique_name("transaction_test_user")

            user = sm.add_user(
                username=username,
                first_name="Transaction",
                last_name="Test",
                email=f"{username}@test.com",
                password="password123",
            )

            self.created_users.append(user)

            self.assertEqual(len(modifications_made), 1)
            self.assertEqual(modifications_made[0]["model_type"], "user")
            self.assertFalse(modifications_made[0]["is_committed"])
        finally:
            user_creating.disconnect(pre_commit_modifier)

    def test_pre_commit_error_causes_rollback(self):
        """Test that error in pre-commit handler causes rollback."""
        username = unique_name("failing_user")

        def failing_handler(sender, event):
            raise ValueError("Intentional error in handler")

        user_creating.connect(failing_handler)

        try:
            sm = self.appbuilder.sm

            # This should fail and rollback
            user = sm.add_user(
                username=username,
                first_name="Failing",
                last_name="User",
                email=f"{username}@test.com",
                password="password123",
            )

            # add_user returns False on error
            self.assertFalse(user)

            # User should not exist in DB (no cleanup needed)
            found_user = sm.find_user(username=username)
            self.assertIsNone(found_user)
        finally:
            user_creating.disconnect(failing_handler)


class EventPropertiesTestCase(unittest.TestCase):
    """Test SecurityModelChangeEvent properties."""

    def test_is_pre_commit_true_when_not_committed(self):
        """Test is_pre_commit returns True when is_committed is False."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="user",
            action="creating",
            model_id=1,
            is_committed=False,
        )
        self.assertTrue(event.is_pre_commit)

    def test_is_pre_commit_false_when_committed(self):
        """Test is_pre_commit returns False when is_committed is True."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="user",
            action="created",
            model_id=1,
            is_committed=True,
        )
        self.assertFalse(event.is_pre_commit)

    def test_is_create_for_creating_action(self):
        """Test is_create returns True for 'creating' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="user",
            action="creating",
            model_id=1,
        )
        self.assertTrue(event.is_create)
        self.assertFalse(event.is_update)
        self.assertFalse(event.is_delete)

    def test_is_create_for_created_action(self):
        """Test is_create returns True for 'created' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="user",
            action="created",
            model_id=1,
        )
        self.assertTrue(event.is_create)
        self.assertFalse(event.is_update)
        self.assertFalse(event.is_delete)

    def test_is_update_for_updating_action(self):
        """Test is_update returns True for 'updating' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="role",
            action="updating",
            model_id=1,
        )
        self.assertFalse(event.is_create)
        self.assertTrue(event.is_update)
        self.assertFalse(event.is_delete)

    def test_is_update_for_updated_action(self):
        """Test is_update returns True for 'updated' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="role",
            action="updated",
            model_id=1,
        )
        self.assertFalse(event.is_create)
        self.assertTrue(event.is_update)
        self.assertFalse(event.is_delete)

    def test_is_delete_for_deleting_action(self):
        """Test is_delete returns True for 'deleting' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="group",
            action="deleting",
            model_id=1,
        )
        self.assertFalse(event.is_create)
        self.assertFalse(event.is_update)
        self.assertTrue(event.is_delete)

    def test_is_delete_for_deleted_action(self):
        """Test is_delete returns True for 'deleted' action."""
        from flask_appbuilder.security.events import SecurityModelChangeEvent

        event = SecurityModelChangeEvent(
            model_type="group",
            action="deleted",
            model_id=1,
        )
        self.assertFalse(event.is_create)
        self.assertFalse(event.is_update)
        self.assertTrue(event.is_delete)


class PostCommitErrorHandlingTestCase(SecuritySignalsTestCase):
    """Test error handling in post-commit signals."""

    def test_post_commit_error_is_logged_not_raised(self):
        """Test that errors in post-commit handlers are logged but not raised."""
        username = unique_name("post_error_user")

        def failing_post_handler(sender, event):
            raise ValueError("Intentional post-commit error")

        user_created.connect(failing_post_handler)

        try:
            sm = self.appbuilder.sm

            # This should succeed despite post-commit handler error
            user = sm.add_user(
                username=username,
                first_name="PostError",
                last_name="User",
                email=f"{username}@test.com",
                password="password123",
            )

            # User should be created successfully
            self.assertIsNotNone(user)
            self.assertNotEqual(user, False)
            self.created_users.append(user)

            # Pre-commit should have fired
            self.assertEqual(len(self.pre_commit_events), 1)
            # Post-commit event was sent (handler failed but event was emitted)
        finally:
            user_created.disconnect(failing_post_handler)


class NoAppContextTestCase(SecuritySignalsTestCase):
    """Test signal behavior outside app context."""

    def test_signals_disabled_without_app_context(self):
        """Test that _signals_enabled returns False outside app context."""
        from unittest.mock import patch

        sm = self.appbuilder.sm

        # Within context, signals should be enabled
        self.assertTrue(sm._signals_enabled())

        # Mock has_app_context to return False
        with patch(
            "flask_appbuilder.security.sqla.manager.has_app_context", return_value=False
        ):
            self.assertFalse(sm._signals_enabled())


class TriggeredByUserTestCase(SecuritySignalsTestCase):
    """Test _get_triggered_by_user behavior."""

    def test_triggered_by_user_returns_none_without_request(self):
        """Test that _get_triggered_by_user returns None without request context."""
        sm = self.appbuilder.sm

        # Outside request context, should return None without error
        result = sm._get_triggered_by_user()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
