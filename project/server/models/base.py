from project.server import db
from project.server.models.crud import CRUDMixin


class BaseModel(db.Model, CRUDMixin):
    __abstract__ = True
    pass
