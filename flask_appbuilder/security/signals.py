"""
Signals for Flask-AppBuilder security model changes.

This module provides Blinker signals that fire when User, Role, and Group
models are created, updated, or deleted. There are two types of signals:

**Pre-commit signals** (e.g., `user_creating`):
    Fire BEFORE the transaction is committed. Handlers can modify the
    database session and their changes will be committed atomically
    with the original operation.

**Post-commit signals** (e.g., `user_created`):
    Fire AFTER the transaction is committed. Use these for notifications,
    logging, or other side effects that don't need transactional guarantees.

Example usage::

    from flask_appbuilder.security.signals import user_creating, user_created

    # Pre-commit handler - runs in same transaction
    @user_creating.connect
    def on_user_creating(sender, event):
        # Add related record in same transaction
        my_record = MyModel(user_id=event.model.id)
        db.session.add(my_record)  # Will commit with User

    # Post-commit handler - runs after transaction
    @user_created.connect
    def on_user_created(sender, event):
        # Send notification (transaction already committed)
        send_welcome_email(event.model.email)
"""

from blinker import Namespace

# Create a namespace for FAB security signals
_signals = Namespace()

# =============================================================================
# PRE-COMMIT SIGNALS
# These fire BEFORE commit - handlers can modify the session
# =============================================================================

# User signals (pre-commit)
user_creating = _signals.signal("user-creating")
"""Signal sent before a user is created and committed.

:param sender: The SecurityManager instance
:param event: SecurityModelChangeEvent with model_type="user"
"""

user_updating = _signals.signal("user-updating")
"""Signal sent before a user update is committed.

:param sender: The SecurityManager instance
:param event: SecurityModelChangeEvent with model_type="user"
"""

user_deleting = _signals.signal("user-deleting")
"""Signal sent before a user is deleted and committed.

:param sender: The SecurityManager instance
:param event: SecurityModelChangeEvent with model_type="user"
"""

# Role signals (pre-commit)
role_creating = _signals.signal("role-creating")
"""Signal sent before a role is created and committed."""

role_updating = _signals.signal("role-updating")
"""Signal sent before a role update is committed."""

role_deleting = _signals.signal("role-deleting")
"""Signal sent before a role is deleted and committed."""

# Group signals (pre-commit)
group_creating = _signals.signal("group-creating")
"""Signal sent before a group is created and committed."""

group_updating = _signals.signal("group-updating")
"""Signal sent before a group update is committed."""

group_deleting = _signals.signal("group-deleting")
"""Signal sent before a group is deleted and committed."""

# =============================================================================
# POST-COMMIT SIGNALS
# These fire AFTER commit - for notifications and side effects only
# =============================================================================

# User signals (post-commit)
user_created = _signals.signal("user-created")
"""Signal sent after a user has been created and committed.

:param sender: The SecurityManager instance
:param event: SecurityModelChangeEvent with model_type="user"
"""

user_updated = _signals.signal("user-updated")
"""Signal sent after a user update has been committed."""

user_deleted = _signals.signal("user-deleted")
"""Signal sent after a user has been deleted and committed."""

# Role signals (post-commit)
role_created = _signals.signal("role-created")
"""Signal sent after a role has been created and committed."""

role_updated = _signals.signal("role-updated")
"""Signal sent after a role update has been committed."""

role_deleted = _signals.signal("role-deleted")
"""Signal sent after a role has been deleted and committed."""

# Group signals (post-commit)
group_created = _signals.signal("group-created")
"""Signal sent after a group has been created and committed."""

group_updated = _signals.signal("group-updated")
"""Signal sent after a group update has been committed."""

group_deleted = _signals.signal("group-deleted")
"""Signal sent after a group has been deleted and committed."""
