from project.server import db
from project.server.models.base import BaseModel


class MiscInquiry(BaseModel):
    __tablename__ = "misc_enquiry"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text, nullable=False)

    # Relation
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship("Customer", back_populates="enquiries")

    def __repr__(self) -> str:
        return self.customer.name
