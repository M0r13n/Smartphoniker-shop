from flask import session


class SessionStoreMixin(object):
    """ Mixin that enables storing the object in current session on server side """
    SESSION_KW = None

    @classmethod
    def get_session_kw(cls) -> str:
        if not cls.SESSION_KW:
            raise ValueError(f"SESSION KW not set for {cls.__name__}")
        return cls.SESSION_KW

    @classmethod
    def deserialize(cls, obj):
        raise NotImplementedError()

    @classmethod
    def get_from_session(cls):
        obj = session.get(cls.get_session_kw(), None)
        if obj:
            obj = cls.deserialize(obj)
        return obj

    @classmethod
    def remove_from_session(cls) -> None:
        session.pop(cls.get_session_kw())

    def save_to_session(self) -> None:
        session[self.get_session_kw()] = self.serialize()

    def serialize(self) -> dict:
        raise NotImplementedError()
