"""
Event classes for Flask-AppBuilder security signals.

This module defines the event payload structures sent with security signals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional


@dataclass
class SecurityModelChangeEvent:
    """
    Payload sent with security model change signals.

    This event is passed to signal handlers when User, Role, or Group
    models are created, updated, or deleted.

    Attributes:
        model_type: The type of model ("user", "role", or "group")
        action: The action being performed. Pre-commit actions use present
            participle ("creating", "updating", "deleting"). Post-commit
            actions use past tense ("created", "updated", "deleted").
        model_id: The primary key of the model. For creates, this is
            available after flush() but before commit().
        model: The model instance. For deletes, this may be None or
            an expired instance after commit.
        timestamp: When the event was created.
        changes: For updates, a dict of changed fields with old/new values.
            Example: {"email": {"old": "a@b.com", "new": "x@y.com"}}
        triggered_by: The User who triggered this change, if available.
        is_committed: False for pre-commit signals, True for post-commit.

    Example::

        @user_creating.connect
        def handle_user_creating(sender, event):
            print(f"Creating user {event.model.username}")
            print(f"User ID (from flush): {event.model_id}")
            print(f"Is committed: {event.is_committed}")  # False

        @user_updated.connect
        def handle_user_updated(sender, event):
            print(f"Updated user {event.model_id}")
            print(f"Changes: {event.changes}")
            print(f"Changed by: {event.triggered_by}")
    """

    model_type: Literal["user", "role", "group"]
    action: Literal[
        "creating",
        "updating",
        "deleting",  # Pre-commit
        "created",
        "updated",
        "deleted",  # Post-commit
    ]
    model_id: Any
    model: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    changes: Optional[Dict[str, Dict[str, Any]]] = None
    triggered_by: Optional[Any] = None
    is_committed: bool = False

    @property
    def is_pre_commit(self) -> bool:
        """True if this is a pre-commit event (transaction still open)."""
        return not self.is_committed

    @property
    def is_create(self) -> bool:
        """True if this is a create operation."""
        return self.action in ("creating", "created")

    @property
    def is_update(self) -> bool:
        """True if this is an update operation."""
        return self.action in ("updating", "updated")

    @property
    def is_delete(self) -> bool:
        """True if this is a delete operation."""
        return self.action in ("deleting", "deleted")
