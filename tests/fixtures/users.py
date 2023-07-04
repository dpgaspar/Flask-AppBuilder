from flask_appbuilder.security.sqla.models import Role, User
from sqlalchemy.orm import Session
from tests.const import USERNAME_ADMIN, USERNAME_READONLY


def create_default_users(session: Session):
    # create admin user

    admin_user = session.query(User).filter_by(username=USERNAME_ADMIN).one_or_none()
    if not admin_user:
        role_admin = session.query(Role).filter_by(name="Admin").first()
        user = User()
        user.first_name = "admin"
        user.last_name = "user"
        user.email = "admin@fab.org"
        user.username = USERNAME_ADMIN
        user.active = True
        user.roles = [role_admin]
        session.add(user)

    readonly_user = (
        session.query(User).filter_by(username=USERNAME_READONLY).one_or_none()
    )
    if not readonly_user:
        # create readonly user
        user = User()
        user.first_name = "readonly"
        user.last_name = "readonly"
        user.email = "readonly@fab.org"
        user.username = USERNAME_READONLY
        user.active = True
        user.roles = [role_admin]
        session.add(user)
        session.commit()
