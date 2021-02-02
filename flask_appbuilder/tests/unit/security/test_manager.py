from unittest import TestCase
from unittest.mock import Mock, patch

from flask_appbuilder.security.manager import BaseSecurityManager


class BaseSecurityManagerTestCase(TestCase):
    def test__get_oauth_user_info_should_work_on_gitlab_case(self):
        # Given
        user_response = {
            "username": "me",
            "email": "me@somewhere.com",
            "name": "whatever",
            "id": 113,
        }
        providers = {
            "gitlab": Mock(
                get=Mock(return_value=Mock(json=Mock(return_value=user_response)))
            )
        }
        # appbuilder = Mock(sm=Mock(oauth_remotes=providers))
        with patch.object(BaseSecurityManager, "__init__", return_value=None):
            manager = BaseSecurityManager()
            manager.appbuilder = Mock(sm=Mock(oauth_remotes=providers))
            # manager.appbuilder = appbuilder
            # When
            actual = manager.get_oauth_user_info(provider="gitlab", resp=None)
            expected = {
                "username": "gitlab_me",
                "email": "me@somewhere.com",
                "name": "whatever",
                "id": 113,
            }
            # Then
            self.assertEquals(actual, expected)
