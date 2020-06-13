import logging
from contextlib import contextmanager

from project.server import db as _db

logger = logging.getLogger(__name__)


@contextmanager
def get_session():
    session = _db.session
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(e)
        raise e
    else:
        session.commit()


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
        with get_session() as session:
            session.add(self)
        return self

    def delete(self):
        """
        Delete the object from the database.
        """
        with get_session() as session:
            session.delete(self)
        return None
