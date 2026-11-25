def test_user_changed_on_updates_on_role_change(appbuilder):
    sm = appbuilder.sm

    role = sm.add_role("TestRole")

    user = sm.add_user(
        username="test_user",
        first_name="Test",
        last_name="User",
        email="test_user@test.com",
        password="password",
    )

    before = user.changed_on
    assert before is not None

    user.roles.append(role)
    sm.update_user(user)

    assert user.changed_on > before
