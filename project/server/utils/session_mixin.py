from flask import session


class SessionStoreMixin(object):
    """ Mixin that enables storing the object in current session on server side """

    @classmethod
    def get_session_kw(cls) -> str:
        return cls.__class__.__name__

    @classmethod
    def deserialize(cls, obj):
        raise NotImplementedError()

    @classmethod
    def get_from_session(cls):
        obj = session.get(cls.get_session_kw(), None)
        if obj:
            obj = cls.deserialize(obj)
        return obj

    def save_to_session(self) -> None:
        session[self.get_session_kw()] = self.serialize()

    def serialize(self) -> dict:
        raise NotImplementedError()
