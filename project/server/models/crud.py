import typing
from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NoSessionError(RuntimeError):
    pass


class SessionMixin:
    _session = None

    @classmethod
    def set_session(cls, session):
        cls._session = session

    @classmethod
    @contextmanager
    def get_session(cls):
        session = cls._session
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        else:
            session.commit()


class CRUDMixin(Base, SessionMixin):
    __abstract__ = True

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @classmethod
    def session(cls):
        return cls.get_session()

    @classmethod
    def create(cls, **kwargs):
        """
        Creates the object and saves it.
        """
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def all(cls):
        """
        Get all instances for that model class.
        """
        return cls.query.all()

    @classmethod
    def get(cls, _id):
        """
        Get the instance with the given id.
        """
        return cls.query.get(_id)

    @classmethod
    def first(cls):
        """
        Get the first instance for that model class.
        """
        return cls.query.first()

    @classmethod
    def destroy(cls, *ids: typing.List):
        """
        Delete the records with the given ids.
        """
        with cls.session():
            for pk in ids:
                cls.get(pk).delete()

    def update(self, **kwargs):
        """
        Update a instance and saves it on success.
        """
        for name in kwargs.keys():
            try:
                setattr(self, name, kwargs[name])
            except AttributeError as e:
                raise KeyError("Attribute '{}' doesn't exist".format(name)) from e
        self.save()

    def save(self):
        """
        Saves the object to the database.
        """
        with self.session() as session:
            session.add(self)
        return self

    def delete(self):
        """
        Delete the object from the database.
        """
        with self.session() as session:
            session.delete(self)
        return None

    def clone(self, **kwargs):
        """Clone an arbitrary sqlalchemy model object without its primary key values."""
        with self.session() as session:
            table = self.__table__
            non_pk_columns = [k for k in table.columns.keys() if k not in table.primary_key]
            data = {c: getattr(self, c) for c in non_pk_columns}
            data.update(kwargs)
            clone = self.__class__(**data)
            session.add(clone)
        return clone
