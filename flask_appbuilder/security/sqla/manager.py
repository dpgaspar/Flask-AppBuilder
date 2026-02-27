from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from flask import current_app, has_app_context
from flask_appbuilder import const as c
from flask_appbuilder import Model
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.events import SecurityModelChangeEvent
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_appbuilder.security.signals import (
    group_created,
    group_creating,
    group_deleted,
    group_deleting,
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
from flask_appbuilder.security.sqla.apis import (
    GroupApi,
    PermissionApi,
    PermissionViewMenuApi,
    RoleApi,
    UserApi,
    ViewMenuApi,
)
from flask_appbuilder.security.sqla.models import (
    assoc_permissionview_role,
    Group,
    Permission,
    PermissionView,
    RegisterUser,
    Role,
    User,
    ViewMenu,
)
from sqlalchemy import and_, func, literal, update
from sqlalchemy import inspect
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.exc import MultipleResultsFound
from werkzeug.security import generate_password_hash


log = logging.getLogger(__name__)


class SecurityManager(BaseSecurityManager):
    """
    Responsible for authentication, registering security views,
    role and permission auto management

    If you want to change anything just inherit and override, then
    pass your own security manager to AppBuilder.
    """

    user_model = User
    """ Override to set your own User Model """
    role_model = Role
    """ Override to set your own Role Model """
    group_model = Group
    permission_model = Permission
    viewmenu_model = ViewMenu
    permissionview_model = PermissionView
    registeruser_model = RegisterUser

    # APIs
    permission_api = PermissionApi
    role_api = RoleApi
    user_api = UserApi
    view_menu_api = ViewMenuApi
    permission_view_menu_api = PermissionViewMenuApi
    group_api = GroupApi

    # ---------------------------------------------------------------------------
    # Signal emission helpers
    # ---------------------------------------------------------------------------

    def _signals_enabled(self) -> bool:
        """Check if security model signals are enabled."""
        if not has_app_context():
            return False
        return current_app.config.get("FAB_SECURITY_SIGNALS_ENABLED", True)

    def _get_triggered_by_user(self) -> Optional[Any]:
        """
        Safely get the current user for signal triggered_by field.

        Returns None if outside request context or no user is authenticated.
        """
        try:
            return self.current_user
        except Exception:
            return None

    def _emit_pre_signal(
        self,
        signal,
        model_type: str,
        action: str,
        model_id: Any,
        model: Any = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a pre-commit signal (within the transaction).

        Handlers can modify the session and changes will be committed
        together with the original operation.
        """
        if not self._signals_enabled():
            return

        event = SecurityModelChangeEvent(
            model_type=model_type,
            action=action,
            model_id=model_id,
            model=model,
            timestamp=datetime.utcnow(),
            changes=changes,
            triggered_by=self._get_triggered_by_user(),
            is_committed=False,
        )
        try:
            signal.send(self, event=event)
        except Exception as e:
            log.error("Error in pre-commit signal handler: %s", e)
            raise

    def _emit_post_signal(
        self,
        signal,
        model_type: str,
        action: str,
        model_id: Any,
        model: Any = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a post-commit signal (after the transaction).

        For notifications and side effects only. Errors in handlers
        are logged but do not affect the already-committed transaction.
        """
        if not self._signals_enabled():
            return

        event = SecurityModelChangeEvent(
            model_type=model_type,
            action=action,
            model_id=model_id,
            model=model,
            timestamp=datetime.utcnow(),
            changes=changes,
            triggered_by=self._get_triggered_by_user(),
            is_committed=True,
        )
        try:
            signal.send(self, event=event)
        except Exception as e:
            log.error("Error in post-commit signal handler: %s", e)
            # Don't re-raise - transaction already committed

    def _detect_model_changes(self, model: Any) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Detect what fields have changed on a model instance.

        Uses SQLAlchemy inspection to compare current values against
        the committed (database) values.

        Returns a dict of changed fields with old/new values, or None if
        no changes detected.
        """
        from sqlalchemy import inspect as sa_inspect

        changes = {}
        insp = sa_inspect(model)

        for attr in insp.attrs:
            hist = attr.history
            # Check if the attribute has changes (added or deleted values)
            if hist.has_changes():
                # For scalar attributes, deleted is the old value, added is new
                if hist.deleted:
                    old_val = hist.deleted[0] if hist.deleted else None
                else:
                    old_val = None
                if hist.added:
                    new_val = hist.added[0] if hist.added else None
                else:
                    new_val = getattr(model, attr.key, None)

                # Only record if values are actually different
                if old_val != new_val:
                    changes[attr.key] = {"old": old_val, "new": new_val}

        return changes if changes else None

    # ---------------------------------------------------------------------------

    def __init__(self, appbuilder):
        """
        SecurityManager contructor
        param appbuilder:
            F.A.B AppBuilder main object
        """
        super(SecurityManager, self).__init__(appbuilder)
        user_datamodel = SQLAInterface(self.user_model)
        if self.auth_type == c.AUTH_DB:
            self.userdbmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_LDAP:
            self.userldapmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_OAUTH:
            self.useroauthmodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_REMOTE_USER:
            self.userremoteusermodelview.datamodel = user_datamodel
        elif self.auth_type == c.AUTH_SAML:
            self.usersamlmodelview.datamodel = user_datamodel

        if self.userstatschartview:
            self.userstatschartview.datamodel = user_datamodel
        if self.auth_user_registration:
            self.registerusermodelview.datamodel = SQLAInterface(
                self.registeruser_model
            )

        self.rolemodelview.datamodel = SQLAInterface(self.role_model)
        self.groupmodelview.datamodel = SQLAInterface(self.group_model)
        self.permissionmodelview.datamodel = SQLAInterface(self.permission_model)
        self.viewmenumodelview.datamodel = SQLAInterface(self.viewmenu_model)
        self.permissionviewmodelview.datamodel = SQLAInterface(
            self.permissionview_model
        )
        self.create_db()

    @property
    def session(self):
        return current_app.appbuilder.session

    def register_views(self) -> None:
        super().register_views()

        if current_app.config.get("FAB_ADD_SECURITY_API", False):
            self.appbuilder.add_api(self.permission_api)
            self.appbuilder.add_api(self.role_api)
            self.appbuilder.add_api(self.user_api)
            self.appbuilder.add_api(self.view_menu_api)
            self.appbuilder.add_api(self.permission_view_menu_api)
            self.appbuilder.add_api(self.group_api)

    def create_db(self) -> None:
        if not current_app.config.get("FAB_CREATE_DB", True):
            return
            # Check if an application context does not exist
        if not has_app_context():
            # Create a new application context
            with current_app.app_context():
                self._create_db()
        else:
            self._create_db()

    def _create_db(self) -> None:
        engine = self.session.get_bind(mapper=None, clause=None)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        if "ab_user" not in existing_tables or "ab_group" not in existing_tables:
            log.info(c.LOGMSG_INF_SEC_NO_DB)
            Model.metadata.create_all(engine)
            log.info(c.LOGMSG_INF_SEC_ADD_DB)
        super().create_db()

    def find_register_user(self, registration_hash: str) -> Optional[RegisterUser]:
        return (
            self.session.query(self.registeruser_model)
            .filter(self.registeruser_model.registration_hash == registration_hash)
            .scalar()
        )

    def add_register_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str = "",
        hashed_password: str = "",
    ) -> User:
        """
        Add a registration request for the user.

        :rtype : RegisterUser
        """
        register_user = self.registeruser_model()
        register_user.username = username
        register_user.email = email
        register_user.first_name = first_name
        register_user.last_name = last_name
        if hashed_password:
            register_user.password = hashed_password
        else:
            register_user.password = generate_password_hash(
                password=password,
                method=current_app.config.get("FAB_PASSWORD_HASH_METHOD", "scrypt"),
                salt_length=current_app.config.get("FAB_PASSWORD_HASH_SALT_LENGTH", 16),
            )
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.session.add(register_user)
            self.session.commit()
            return register_user
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_REGISTER_USER, e)
            self.session.rollback()
            return None

    def del_register_user(self, register_user):
        """
        Deletes registration object from database

        :param register_user: RegisterUser object to delete
        """
        try:
            self.session.delete(register_user)
            self.session.commit()
            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_REGISTER_USER, e)
            self.session.rollback()
            return False

    def find_user(self, username=None, email=None):
        """
        Finds user by username or email
        """
        if username:
            try:
                if self.auth_username_ci:
                    return (
                        self.session.query(self.user_model)
                        .filter(
                            func.lower(self.user_model.username) == func.lower(username)
                        )
                        .one_or_none()
                    )
                else:
                    return (
                        self.session.query(self.user_model)
                        .filter(self.user_model.username == username)
                        .one_or_none()
                    )
            except MultipleResultsFound:
                log.error("Multiple results found for user %s", username)
                return None
        elif email:
            try:
                return (
                    self.session.query(self.user_model)
                    .filter_by(email=email)
                    .one_or_none()
                )
            except MultipleResultsFound:
                log.error("Multiple results found for user with email %s", email)
                return None

    def get_all_users(self):
        return self.session.query(self.user_model).all()

    def add_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        role: Union[List[Role], Role, None] = None,
        password: str = "",
        hashed_password: str = "",
        groups: Optional[List[Group]] = None,
        commit: bool = True,
    ):
        """
        Generic function to create user.

        :param username: The user's username
        :param first_name: The user's first name
        :param last_name: The user's last name
        :param email: The user's email address
        :param role: A Role or list of Roles to assign to the user
        :param password: Plain text password (will be hashed)
        :param hashed_password: Pre-hashed password (use instead of password)
        :param groups: List of Groups to assign to the user
        :param commit: If True (default), commits the transaction. If False,
            the caller is responsible for committing. Pre-commit signals
            are always fired; post-commit signals only fire if commit=True.
        :return: The created User instance, or False on error
        """
        roles = []
        if role:
            roles = role if isinstance(role, list) else [role]

        try:
            user = self.user_model()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            user.roles = roles
            user.groups = groups or []
            if hashed_password:
                user.password = hashed_password
            else:
                user.password = generate_password_hash(
                    password=password,
                    method=current_app.config.get("FAB_PASSWORD_HASH_METHOD", "scrypt"),
                    salt_length=current_app.config.get(
                        "FAB_PASSWORD_HASH_SALT_LENGTH", 16
                    ),
                )
            self.session.add(user)

            # Flush to get the user ID before emitting pre-commit signal
            self.session.flush()

            # Pre-commit signal - handlers can modify the session
            self._emit_pre_signal(user_creating, "user", "creating", user.id, user)

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_USER, username)
                # Post-commit signal - for notifications only
                self._emit_post_signal(user_created, "user", "created", user.id, user)

            return user
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_USER, e)
            self.session.rollback()
            return False

    def count_users(self):
        return self.session.query(func.count(self.user_model.id)).scalar()

    def update_user(self, user, commit: bool = True):
        """
        Update an existing user.

        :param user: The User instance with updated values
        :param commit: If True (default), commits the transaction. If False,
            the caller is responsible for committing.
        :return: None on success, False on error
        """
        try:
            # Load existing user from DB to compare role/group changes
            existing_user = self.session.get(self.user_model, user.id)

            # Detect role/group relationship changes before merge
            existing_role_ids = {r.id for r in existing_user.roles}
            existing_group_ids = {g.id for g in existing_user.groups}
            new_role_ids = {r.id for r in user.roles}
            new_group_ids = {g.id for g in user.groups}

            roles_changed = existing_role_ids != new_role_ids
            groups_changed = existing_group_ids != new_group_ids

            if roles_changed or groups_changed:
                user.changed_on = datetime.utcnow()  # pragma: no cover

            self.session.merge(user)

            # Flush changes before detecting them
            self.session.flush()

            # Detect scalar field changes using SQLAlchemy inspection
            changes = self._detect_model_changes(user)

            # Add relationship changes
            if roles_changed:
                changes = changes or {}
                changes["roles"] = {
                    "old": list(existing_role_ids),
                    "new": list(new_role_ids),
                }
            if groups_changed:
                changes = changes or {}
                changes["groups"] = {
                    "old": list(existing_group_ids),
                    "new": list(new_group_ids),
                }

            # Pre-commit signal - handlers can modify the session
            self._emit_pre_signal(
                user_updating, "user", "updating", user.id, user, changes
            )

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_UPD_USER, user)
                # Post-commit signal - for notifications only
                self._emit_post_signal(
                    user_updated, "user", "updated", user.id, user, changes
                )

        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_UPD_USER, e)
            self.session.rollback()
            return False

    def get_user_by_id(self, pk):
        return self.session.get(self.user_model, pk)

    def delete_user(self, user_or_id, commit: bool = True) -> bool:
        """
        Delete a user.

        :param user_or_id: A User instance or user ID to delete
        :param commit: If True (default), commits the transaction
        :return: True on success, False on error
        """
        if isinstance(user_or_id, self.user_model):
            user = user_or_id
        else:
            user = self.get_user_by_id(user_or_id)

        if not user:
            log.warning("User not found for deletion")
            return False

        user_id = user.id
        try:
            # Pre-commit signal - fire before delete
            self._emit_pre_signal(user_deleting, "user", "deleting", user_id, user)

            self.session.delete(user)

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_DEL_USER, user_id)
                # Post-commit signal
                self._emit_post_signal(user_deleted, "user", "deleted", user_id, None)

            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_USER, e)
            self.session.rollback()
            return False

    def get_first_user(self) -> "User":
        return self.session.query(self.user_model).first()

    def noop_user_update(self, user: "User") -> None:
        stmt = (
            update(self.user_model)
            .where(self.user_model.id == user.id)
            .values(login_count=user.login_count)
        )
        self.session.execute(stmt)
        self.session.commit()

    """
    -----------------------
     PERMISSION MANAGEMENT
    -----------------------
    """

    def add_role(
        self,
        name: str,
        permissions: Optional[List[PermissionView]] = None,
        commit: bool = True,
    ) -> Optional[Role]:
        """
        Add a new role.

        :param name: The role name
        :param permissions: List of PermissionView instances to assign
        :param commit: If True (default), commits the transaction
        :return: The created Role, or existing Role if name already exists
        """
        if not permissions:
            permissions = []

        role = self.find_role(name)
        if role is None:
            try:
                role = self.role_model()
                role.name = name
                role.permissions = permissions
                self.session.add(role)

                # Flush to get the role ID
                self.session.flush()

                # Pre-commit signal
                self._emit_pre_signal(role_creating, "role", "creating", role.id, role)

                if commit:
                    self.session.commit()
                    log.info(c.LOGMSG_INF_SEC_ADD_ROLE, name)
                    # Post-commit signal
                    self._emit_post_signal(
                        role_created, "role", "created", role.id, role
                    )

                return role
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_ROLE, e)
                self.session.rollback()
        return role

    def update_role(self, pk, name: str, commit: bool = True) -> Optional[Role]:
        """
        Update an existing role.

        :param pk: The role's primary key
        :param name: The new role name
        :param commit: If True (default), commits the transaction
        :return: The updated Role, or None on error
        """
        role = self.session.query(self.role_model).get(pk)
        if not role:
            return None
        try:
            old_name = role.name
            changes = None
            if old_name != name:
                changes = {"name": {"old": old_name, "new": name}}

            role.name = name
            self.session.merge(role)

            # Flush changes
            self.session.flush()

            # Pre-commit signal
            self._emit_pre_signal(
                role_updating, "role", "updating", role.id, role, changes
            )

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_UPD_ROLE, role)
                # Post-commit signal
                self._emit_post_signal(
                    role_updated, "role", "updated", role.id, role, changes
                )

            return role
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_UPD_ROLE, e)
            self.session.rollback()
            return None

    def find_role(self, name):
        return self.session.query(self.role_model).filter_by(name=name).one_or_none()

    def delete_role(self, role_or_id, commit: bool = True) -> bool:
        """
        Delete a role.

        :param role_or_id: A Role instance or role ID to delete
        :param commit: If True (default), commits the transaction
        :return: True on success, False on error
        """
        if isinstance(role_or_id, self.role_model):
            role = role_or_id
        else:
            role = self.session.query(self.role_model).get(role_or_id)

        if not role:
            log.warning("Role not found for deletion")
            return False

        role_id = role.id
        try:
            # Pre-commit signal - fire before delete
            self._emit_pre_signal(role_deleting, "role", "deleting", role_id, role)

            self.session.delete(role)

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_DEL_ROLE, role_id)
                # Post-commit signal
                self._emit_post_signal(role_deleted, "role", "deleted", role_id, None)

            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_ROLE, e)
            self.session.rollback()
            return False

    def get_all_roles(self):
        return self.session.query(self.role_model).all()

    def get_public_role(self):
        return (
            self.session.query(self.role_model)
            .filter_by(name=self.auth_role_public)
            .one_or_none()
        )

    def find_group(self, name: str) -> Group:
        return self.session.query(self.group_model).filter_by(name=name).one_or_none()

    def add_group(
        self,
        name: str,
        label: str,
        description: str,
        roles: Optional[List[Role]] = None,
        users: Optional[List[User]] = None,
        commit: bool = True,
    ) -> Optional[Group]:
        """
        Add a new group.

        :param name: The group name (unique identifier)
        :param label: The group label (display name)
        :param description: The group description
        :param roles: List of Roles to assign to the group
        :param users: List of Users to add to the group
        :param commit: If True (default), commits the transaction
        :return: The created Group, or existing Group if name already exists
        """
        group = self.find_group(name)
        if group is not None:
            return group
        try:
            group = self.group_model()
            group.name = name
            group.label = label
            group.description = description
            group.roles = roles or []
            group.users = users or []

            self.session.add(group)

            # Flush to get the group ID
            self.session.flush()

            # Pre-commit signal
            self._emit_pre_signal(group_creating, "group", "creating", group.id, group)

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_GROUP, name)
                # Post-commit signal
                self._emit_post_signal(
                    group_created, "group", "created", group.id, group
                )

            return group
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_GROUP, e)
            self.session.rollback()
            return None

    def delete_group(self, group_or_id, commit: bool = True) -> bool:
        """
        Delete a group.

        :param group_or_id: A Group instance or group ID to delete
        :param commit: If True (default), commits the transaction
        :return: True on success, False on error
        """
        if isinstance(group_or_id, self.group_model):
            group = group_or_id
        else:
            group = self.session.query(self.group_model).get(group_or_id)

        if not group:
            log.warning("Group not found for deletion")
            return False

        group_id = group.id
        try:
            # Pre-commit signal - fire before delete
            self._emit_pre_signal(group_deleting, "group", "deleting", group_id, group)

            self.session.delete(group)

            if commit:
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_DEL_GROUP, group_id)
                # Post-commit signal
                self._emit_post_signal(
                    group_deleted, "group", "deleted", group_id, None
                )

            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_GROUP, e)
            self.session.rollback()
            return False

    def get_public_permissions(self):
        role = self.get_public_role()
        if role:
            return role.permissions
        return []

    def find_permission(self, name):
        """
        Finds and returns a Permission by name
        """
        return (
            self.session.query(self.permission_model).filter_by(name=name).one_or_none()
        )

    def exist_permission_on_roles(
        self, view_name: str, permission_name: str, role_ids: List[int]
    ) -> bool:
        """
            Method to efficiently check if a certain permission exists
            on a list of role id's. This is used by `has_access`

        :param view_name: The view's name to check if exists on one of the roles
        :param permission_name: The permission name to check if exists
        :param role_ids: a list of Role ids
        :return: Boolean
        """
        q = (
            self.session.query(self.permissionview_model)
            .join(
                assoc_permissionview_role,
                and_(
                    (
                        self.permissionview_model.id
                        == assoc_permissionview_role.c.permission_view_id
                    )
                ),
            )
            .join(self.role_model)
            .join(self.permission_model)
            .join(self.viewmenu_model)
            .filter(
                self.viewmenu_model.name == view_name,
                self.permission_model.name == permission_name,
                self.role_model.id.in_(role_ids),
            )
            .exists()
        )
        # Special case for MSSQL/Oracle (works on PG and MySQL > 8)
        if self.session.get_bind().name in ("mssql", "oracle"):
            return self.session.query(literal(True)).filter(q).scalar()
        return self.session.query(q).scalar()

    def find_roles_permission_view_menus(
        self, permission_name: str, role_ids: List[int]
    ):
        return (
            self.session.query(self.permissionview_model)
            .join(
                assoc_permissionview_role,
                and_(
                    (
                        self.permissionview_model.id
                        == assoc_permissionview_role.c.permission_view_id
                    )
                ),
            )
            .join(self.role_model)
            .join(self.permission_model)
            .join(self.viewmenu_model)
            .filter(
                self.permission_model.name == permission_name,
                self.role_model.id.in_(role_ids),
            )
        ).all()

    def get_user_roles_permissions(self, user) -> Dict[str, List[Tuple[str, str]]]:
        """
        Utility method for fetching all roles and permissions for a specific user.
        Example of the returned data:
        ```
        {
            'Admin': [
                ('can_this_form_get', 'ResetPasswordView'),
                ('can_this_form_post', 'ResetPasswordView'),
                ...
            ]
             'EmptyRole': [],
        }
        ```
        """
        if not user.roles and not user.groups:
            raise AttributeError("User object does not have roles or groups")

        result: Dict[str, List[Tuple[str, str]]] = {}
        db_roles_ids = []
        roles = self.get_user_roles(user)
        for role in roles:
            # Make sure all db roles are included on the result
            result[role.name] = []
            if role.name in self.builtin_roles:
                for permission in self.builtin_roles[role.name]:
                    result[role.name].append((permission[1], permission[0]))
            else:
                db_roles_ids.append(role.id)

        permission_views = (
            self.session.query(PermissionView)
            .join(Permission)
            .join(ViewMenu)
            .join(PermissionView.role)
            .filter(Role.id.in_(db_roles_ids))
            .options(contains_eager(PermissionView.permission))
            .options(contains_eager(PermissionView.view_menu))
            .options(contains_eager(PermissionView.role))
        ).all()

        for permission_view in permission_views:
            for role_item in permission_view.role:
                if role_item.name in result:
                    result[role_item.name].append(
                        (
                            permission_view.permission.name,
                            permission_view.view_menu.name,
                        )
                    )
        return result

    def get_db_role_permissions(self, role_id: int) -> List[PermissionView]:
        """
        Get all DB permissions from a role (one single query)
        """
        return (
            self.session.query(PermissionView)
            .join(Permission)
            .join(ViewMenu)
            .join(PermissionView.role)
            .filter(Role.id == role_id)
            .options(contains_eager(PermissionView.permission))
            .options(contains_eager(PermissionView.view_menu))
            .all()
        )

    def add_permission(self, name):
        """
        Adds a permission to the backend, model permission

        :param name:
            name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if perm is None:
            try:
                perm = self.permission_model()
                perm.name = name
                self.session.add(perm)
                self.session.commit()
                return perm
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMISSION, e)
                self.session.rollback()
        return perm

    def del_permission(self, name: str) -> bool:
        """
        Deletes a permission from the backend, model permission

        :param name:
            name of the permission: 'can_add','can_edit' etc...
        """
        perm = self.find_permission(name)
        if not perm:
            log.warning(c.LOGMSG_WAR_SEC_DEL_PERMISSION, name)
            return False
        try:
            pvms = (
                self.session.query(self.permissionview_model)
                .filter(self.permissionview_model.permission == perm)
                .all()
            )
            if pvms:
                log.warning(c.LOGMSG_WAR_SEC_DEL_PERM_PVM, perm, pvms)
                return False
            self.session.delete(perm)
            self.session.commit()
            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION, e)
            self.session.rollback()
            return False

    """
    ----------------------
     PRIMITIVES VIEW MENU
    ----------------------
    """

    def find_view_menu(self, name):
        """
        Finds and returns a ViewMenu by name
        """
        return (
            self.session.query(self.viewmenu_model).filter_by(name=name).one_or_none()
        )

    def get_all_view_menu(self):
        return self.session.query(self.viewmenu_model).all()

    def add_view_menu(self, name):
        """
        Adds a view or menu to the backend, model view_menu
        param name:
            name of the view menu to add
        """
        view_menu = self.find_view_menu(name)
        if view_menu is None:
            try:
                view_menu = self.viewmenu_model()
                view_menu.name = name
                self.session.add(view_menu)
                self.session.commit()
                return view_menu
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_VIEWMENU, e)
                self.session.rollback()
        return view_menu

    def del_view_menu(self, name: str) -> bool:
        """
        Deletes a ViewMenu from the backend

        :param name:
            name of the ViewMenu
        """
        view_menu = self.find_view_menu(name)
        if not view_menu:
            log.warning(c.LOGMSG_WAR_SEC_DEL_VIEWMENU, name)
            return False
        try:
            pvms = (
                self.session.query(self.permissionview_model)
                .filter(self.permissionview_model.view_menu == view_menu)
                .all()
            )
            if pvms:
                log.warning(c.LOGMSG_WAR_SEC_DEL_VIEWMENU_PVM, view_menu, pvms)
                return False
            self.session.delete(view_menu)
            self.session.commit()
            return True
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_PERMISSION, e)
            self.session.rollback()
            return False

    """
    ----------------------
     PERMISSION VIEW MENU
    ----------------------
    """

    def find_permission_view_menu(self, permission_name, view_menu_name):
        """
        Finds and returns a PermissionView by names
        """
        permission = self.find_permission(permission_name)
        view_menu = self.find_view_menu(view_menu_name)
        if permission and view_menu:
            return (
                self.session.query(self.permissionview_model)
                .filter_by(permission=permission, view_menu=view_menu)
                .one_or_none()
            )

    def find_permissions_view_menu(self, view_menu):
        """
        Finds all permissions from ViewMenu, returns list of PermissionView

        :param view_menu: ViewMenu object
        :return: list of PermissionView objects
        """
        return (
            self.session.query(self.permissionview_model)
            .filter_by(view_menu_id=view_menu.id)
            .all()
        )

    def add_permission_view_menu(self, permission_name, view_menu_name):
        """
        Adds a permission on a view or menu to the backend

        :param permission_name:
            name of the permission to add: 'can_add','can_edit' etc...
        :param view_menu_name:
            name of the view menu to add
        """
        if not (permission_name and view_menu_name):
            return None
        pv = self.find_permission_view_menu(permission_name, view_menu_name)
        if pv:
            return pv
        vm = self.add_view_menu(view_menu_name)
        perm = self.add_permission(permission_name)
        pv = self.permissionview_model()
        pv.view_menu, pv.permission = vm, perm
        try:
            self.session.add(pv)
            self.session.commit()
            log.info(c.LOGMSG_INF_SEC_ADD_PERMVIEW, pv)
            return pv
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_ADD_PERMVIEW, e)
            self.session.rollback()

    def del_permission_view_menu(self, permission_name, view_menu_name, cascade=True):
        if not (permission_name and view_menu_name):
            return
        pv = self.find_permission_view_menu(permission_name, view_menu_name)
        if not pv:
            return
        roles_pvs = (
            self.session.query(self.role_model)
            .filter(self.role_model.permissions.contains(pv))
            .first()
        )
        if roles_pvs:
            log.warning(
                c.LOGMSG_WAR_SEC_DEL_PERMVIEW,
                view_menu_name,
                permission_name,
                roles_pvs,
            )
            return
        try:
            # delete permission on view
            self.session.delete(pv)
            self.session.commit()
            # if no more permission on permission view, delete permission
            if not cascade:
                return
            if (
                not self.session.query(self.permissionview_model)
                .filter_by(permission=pv.permission)
                .all()
            ):
                self.del_permission(pv.permission.name)
            log.info(c.LOGMSG_INF_SEC_DEL_PERMVIEW, permission_name, view_menu_name)
        except Exception as e:
            log.error(c.LOGMSG_ERR_SEC_DEL_PERMVIEW, e)
            self.session.rollback()

    def exist_permission_on_views(self, lst, item):
        for i in lst:
            if i.permission and i.permission.name == item:
                return True
        return False

    def exist_permission_on_view(self, lst, permission, view_menu):
        for i in lst:
            if i.permission.name == permission and i.view_menu.name == view_menu:
                return True
        return False

    def add_permission_role(self, role, perm_view):
        """
        Add permission-ViewMenu object to Role

        :param role:
            The role object
        :param perm_view:
            The PermissionViewMenu object
        """
        if perm_view and perm_view not in role.permissions:
            try:
                role.permissions.append(perm_view)
                self.session.merge(role)
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_ADD_PERMROLE, perm_view, role.name)
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_ADD_PERMROLE, e)
                self.session.rollback()

    def del_permission_role(self, role, perm_view):
        """
        Remove permission-ViewMenu object to Role

        :param role:
            The role object
        :param perm_view:
            The PermissionViewMenu object
        """
        if perm_view in role.permissions:
            try:
                role.permissions.remove(perm_view)
                self.session.merge(role)
                self.session.commit()
                log.info(c.LOGMSG_INF_SEC_DEL_PERMROLE, perm_view, role.name)
            except Exception as e:
                log.error(c.LOGMSG_ERR_SEC_DEL_PERMROLE, e)
                self.session.rollback()

    def export_roles(
        self, path: Optional[str] = None, indent: Optional[Union[int, str]] = None
    ) -> None:
        """Exports roles to JSON file."""
        log.error("BIND URL: %s", self.session.get_bind().url)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename = path or f"roles_export_{timestamp}.json"

        serialized_roles: List[Dict[str, List[Dict[str, str]]]] = []

        for role in self.get_all_roles():
            serialized_role = {"name": role.name, "permissions": []}
            for pvm in role.permissions:
                permission = pvm.permission
                view_menu = pvm.view_menu
                permission_view_menu = {
                    "permission": {"name": permission.name},
                    "view_menu": {"name": view_menu.name},
                }
                serialized_role["permissions"].append(permission_view_menu)
            serialized_roles.append(serialized_role)

        with open(filename, "w") as fd:
            fd.write(json.dumps(serialized_roles, indent=indent))

    def import_roles(self, path: str) -> None:
        """Imports roles from JSON file."""

        session = self.session()

        with open(path, "r") as fd:
            roles_json = json.loads(fd.read())

        roles = []

        for role_kwargs in roles_json:
            role = self.add_role(role_kwargs["name"])
            permission_view_menus = [
                self.add_permission_view_menu(
                    permission_name=pvm_kwargs["permission"]["name"],
                    view_menu_name=pvm_kwargs["view_menu"]["name"],
                )
                for pvm_kwargs in role_kwargs["permissions"]
            ]

            for permission_view_menu in permission_view_menus:
                if permission_view_menu not in role.permissions:
                    role.permissions.append(permission_view_menu)
            roles.append(role)

        session.add_all(roles)
        session.commit()
