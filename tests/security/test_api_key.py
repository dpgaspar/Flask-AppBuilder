import datetime
import json
import logging
import os
import unittest
from unittest.mock import MagicMock, patch

from flask import Flask, g
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.sqla.models import ApiKey
from flask_appbuilder.utils.legacy import get_sqla_class
from tests.base import FABTestCase
from tests.const import PASSWORD_ADMIN, USERNAME_ADMIN
from werkzeug.security import check_password_hash, generate_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))


class ApiKeyModelTestCase(unittest.TestCase):
    """Test the ApiKey model's is_active property."""

    def _make_key(self, **kwargs):
        key = ApiKey()
        key.name = kwargs.get("name", "test-key")
        key.key_hash = kwargs.get("key_hash", "fakehash")
        key.key_prefix = kwargs.get("key_prefix", "sst_")
        key.active = kwargs.get("active", True)
        key.revoked_on = kwargs.get("revoked_on", None)
        key.expires_on = kwargs.get("expires_on", None)
        return key

    def test_is_active_basic(self):
        key = self._make_key()
        self.assertTrue(key.is_active)

    def test_is_active_inactive(self):
        key = self._make_key(active=False)
        self.assertFalse(key.is_active)

    def test_is_active_revoked(self):
        key = self._make_key(revoked_on=datetime.datetime(2024, 1, 1))
        self.assertFalse(key.is_active)

    def test_is_active_expired(self):
        key = self._make_key(
            expires_on=datetime.datetime(2020, 1, 1)  # past date
        )
        self.assertFalse(key.is_active)

    def test_is_active_not_yet_expired(self):
        key = self._make_key(
            expires_on=datetime.datetime(2099, 1, 1)  # future date
        )
        self.assertTrue(key.is_active)


class ApiKeySecurityManagerTestCase(FABTestCase):
    """Test API key methods on the SecurityManager using a real Flask app."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_security_api")
        self.app.config["FAB_API_KEY_ENABLED"] = True
        self.app.config["FAB_API_KEY_PREFIXES"] = ["sst_"]
        logging.basicConfig(level=logging.ERROR)

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)

    def tearDown(self):
        self.appbuilder.session.query(ApiKey).delete()
        self.appbuilder.session.commit()
        self.ctx.pop()
        self.appbuilder = None
        self.app = None

    def test_create_api_key(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="test-key")

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "test-key")
        self.assertTrue(result["key"].startswith("sst_"))
        self.assertIn("uuid", result)

    def test_validate_api_key_valid(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="test-key")
        raw_key = result["key"]

        validated_user = self.appbuilder.sm.validate_api_key(raw_key)
        self.assertIsNotNone(validated_user)
        self.assertEqual(validated_user.username, USERNAME_ADMIN)

    def test_validate_api_key_invalid(self):
        validated_user = self.appbuilder.sm.validate_api_key("sst_invalid_key_12345")
        self.assertIsNone(validated_user)

    def test_validate_api_key_revoked(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="revoke-test")
        raw_key = result["key"]

        # Revoke the key
        self.appbuilder.sm.revoke_api_key(result["uuid"])

        validated_user = self.appbuilder.sm.validate_api_key(raw_key)
        self.assertIsNone(validated_user)

    def test_validate_api_key_expired(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(
            user=user,
            name="expire-test",
            expires_on=datetime.datetime(2020, 1, 1),
        )
        raw_key = result["key"]

        validated_user = self.appbuilder.sm.validate_api_key(raw_key)
        self.assertIsNone(validated_user)

    def test_revoke_api_key(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="revoke-me")

        success = self.appbuilder.sm.revoke_api_key(result["uuid"])
        self.assertTrue(success)

        api_key = self.appbuilder.sm.get_api_key_by_uuid(result["uuid"])
        self.assertIsNotNone(api_key.revoked_on)

    def test_revoke_nonexistent_key(self):
        success = self.appbuilder.sm.revoke_api_key("nonexistent-uuid")
        self.assertFalse(success)

    def test_find_api_keys_for_user(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        self.appbuilder.sm.create_api_key(user=user, name="key-1")
        self.appbuilder.sm.create_api_key(user=user, name="key-2")

        keys = self.appbuilder.sm.find_api_keys_for_user(user.id)
        self.assertEqual(len(keys), 2)
        names = {k.name for k in keys}
        self.assertIn("key-1", names)
        self.assertIn("key-2", names)

    def test_get_api_key_by_uuid(self):
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="uuid-test")

        api_key = self.appbuilder.sm.get_api_key_by_uuid(result["uuid"])
        self.assertIsNotNone(api_key)
        self.assertEqual(api_key.name, "uuid-test")

    def test_get_api_key_by_uuid_not_found(self):
        api_key = self.appbuilder.sm.get_api_key_by_uuid("nonexistent")
        self.assertIsNone(api_key)


class ApiKeyEndpointTestCase(FABTestCase):
    """Test the API key CRUD endpoints."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_security_api")
        self.app.config["FAB_API_KEY_ENABLED"] = True
        self.app.config["FAB_API_KEY_PREFIXES"] = ["sst_"]
        logging.basicConfig(level=logging.ERROR)

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)
        self.client = self.app.test_client()
        self.token = self.login(self.client, USERNAME_ADMIN, PASSWORD_ADMIN)

    def tearDown(self):
        self.appbuilder.session.query(ApiKey).delete()
        self.appbuilder.session.commit()
        self.ctx.pop()
        self.appbuilder = None
        self.app = None

    def test_create_api_key_endpoint(self):
        rv = self.auth_client_post(
            self.client,
            self.token,
            "api/v1/security/api_keys/",
            json={"name": "test-endpoint-key"},
        )
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.data)
        self.assertIn("result", data)
        self.assertIn("key", data["result"])
        self.assertTrue(data["result"]["key"].startswith("sst_"))

    def test_list_api_keys_endpoint(self):
        # Create a key first
        self.auth_client_post(
            self.client,
            self.token,
            "api/v1/security/api_keys/",
            json={"name": "list-test-key"},
        )

        rv = self.auth_client_get(
            self.client, self.token, "api/v1/security/api_keys/"
        )
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertIn("result", data)
        self.assertGreaterEqual(len(data["result"]), 1)

    def test_get_api_key_endpoint(self):
        rv = self.auth_client_post(
            self.client,
            self.token,
            "api/v1/security/api_keys/",
            json={"name": "get-test-key"},
        )
        key_uuid = json.loads(rv.data)["result"]["uuid"]

        rv = self.auth_client_get(
            self.client, self.token, f"api/v1/security/api_keys/{key_uuid}"
        )
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertEqual(data["result"]["name"], "get-test-key")
        # Plaintext key should NOT be returned on get
        self.assertNotIn("key", data["result"])

    def test_revoke_api_key_endpoint(self):
        rv = self.auth_client_post(
            self.client,
            self.token,
            "api/v1/security/api_keys/",
            json={"name": "revoke-test-key"},
        )
        key_uuid = json.loads(rv.data)["result"]["uuid"]

        rv = self.auth_client_delete(
            self.client, self.token, f"api/v1/security/api_keys/{key_uuid}"
        )
        self.assertEqual(rv.status_code, 200)

    def test_revoke_nonexistent_key_endpoint(self):
        rv = self.auth_client_delete(
            self.client, self.token, "api/v1/security/api_keys/nonexistent-uuid"
        )
        self.assertEqual(rv.status_code, 404)

    def test_create_api_key_no_name(self):
        rv = self.auth_client_post(
            self.client,
            self.token,
            "api/v1/security/api_keys/",
            json={},
        )
        self.assertEqual(rv.status_code, 400)


class ApiKeyProtectDecoratorTestCase(FABTestCase):
    """Test that @protect() accepts API key auth."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object("tests.config_security_api")
        self.app.config["FAB_API_KEY_ENABLED"] = True
        self.app.config["FAB_API_KEY_PREFIXES"] = ["sst_"]
        logging.basicConfig(level=logging.ERROR)

        self.ctx = self.app.app_context()
        self.ctx.push()
        SQLA = get_sqla_class()
        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)
        self.create_default_users(self.appbuilder)
        self.client = self.app.test_client()

    def tearDown(self):
        self.appbuilder.session.query(ApiKey).delete()
        self.appbuilder.session.commit()
        self.ctx.pop()
        self.appbuilder = None
        self.app = None

    def test_api_key_auth_on_protected_endpoint(self):
        """Test that an API key works on a @protect() endpoint."""
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="protect-test")
        api_key = result["key"]

        # Use the API key to list roles (a protected endpoint)
        rv = self.client.get(
            "api/v1/security/roles/",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        self.assertEqual(rv.status_code, 200)

    def test_invalid_api_key_on_protected_endpoint(self):
        """Test that an invalid API key returns 403."""
        rv = self.client.get(
            "api/v1/security/roles/",
            headers={"Authorization": "Bearer sst_invalidkey12345"},
        )
        self.assertEqual(rv.status_code, 403)

    def test_last_used_on_updated(self):
        """Test that last_used_on is updated on API key use."""
        user = self.appbuilder.sm.find_user(USERNAME_ADMIN)
        result = self.appbuilder.sm.create_api_key(user=user, name="usage-test")
        api_key_raw = result["key"]

        # Verify last_used_on is initially None
        api_key_obj = self.appbuilder.sm.get_api_key_by_uuid(result["uuid"])
        self.assertIsNone(api_key_obj.last_used_on)

        # Use the key
        self.client.get(
            "api/v1/security/roles/",
            headers={"Authorization": f"Bearer {api_key_raw}"},
        )

        # Refresh and check
        self.appbuilder.session.refresh(api_key_obj)
        self.assertIsNotNone(api_key_obj.last_used_on)


if __name__ == "__main__":
    unittest.main()
