from project.server import db
from project.server.models.crud import CRUDMixin


class BaseModel(db.Model, CRUDMixin):
    """
    This is the base model that every Sqlalchemy model class should inherit from.
    """
    __abstract__ = True
    pass
