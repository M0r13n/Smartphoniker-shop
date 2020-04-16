from project.server import db


class CRUDMixin(object):
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @classmethod
    def create(cls, **kwargs):
        """
        Creates the object and saves it.
        """
        instance = cls(**kwargs)
        return instance.save()

    def save(self):
        """
        Saves the object to the database.
        """
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """
        Delete the object from the database.
        """
        db.session.delete(self)
        db.session.commit()
        return self

    def test_pw_is_hidden(self, user):
        try:
            user.password
            assert 1 == 2
        except AttributeError:
            return True
