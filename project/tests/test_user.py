from project.server.models.crud import CRUDMixin
from project.server.models.user import User


class TestUserCrud:

    def test_instance(self, user, db):
        assert isinstance(user, CRUDMixin)

    def test_create(self, db):
        user = User.create(email="123456789", password="Hello there")
        assert user is not None
        assert user.email == "123456789"
        assert user.verify_password("Hello there")
        assert user.admin is False
        assert user.registered_on is not None
        assert user.id is not None

    def test_delete(self, user, db):
        # verify it exists in the first place
        assert user is not None
        _user = User.query.filter_by(email=user.email).first()
        assert _user is not None
        assert _user == user

        # Delete it
        user.delete()

        # Verify that it is gone
        _user = User.query.filter_by(email=user.email).first()
        assert _user is None

    def test_user_save(self, user, db):
        assert User.query.filter_by(email="Wurst@Salami.com").first() is None

        user.email = "Wurst@Salami.com"
        user.save()

        assert User.query.filter_by(email="Wurst@Salami.com").first() is not None
